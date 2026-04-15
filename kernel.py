import os.path
from glob import glob

import cv2
import numpy as np
from PIL import Image
from scipy.signal import correlate2d
from skimage.morphology import skeletonize

templateFs = glob("kernels/*x.png")


def template_open(fname):
    return crop_and_pad(
        np.asarray(Image.open(fname).convert("L"), np.uint8)
        , shape=None
    )


def crop_and_pad(a, pad=1, zero=0, shape=(50, 50)):
    a = uint8_coerce(a)
    nz = np.argwhere(a != 0)
    if nz.size == 0:
        return np.full(shape if shape else (1, 1), zero, dtype=np.uint8)
    starts = np.maximum(nz.min(axis=0) - pad, 0)
    ends = np.minimum(nz.max(axis=0) + 1 + pad, a.shape)
    a = a[tuple(slice(int(s), int(e)) for s, e in zip(starts, ends))]
    if not shape:
        return a
    H, W = a.shape
    out = np.full(shape, zero, dtype=np.uint8)
    out[:H, :W] = a
    return out


def uint8_coerce(potential_bool):
    if potential_bool.dtype == bool:
        return potential_bool.astype(np.uint8) * 255
    assert potential_bool.dtype == np.uint8
    return potential_bool


def disk_mask(h, w, radius):
    y = np.arange(h)[:, None] - (h - 1) / 2.0
    x = np.arange(w)[None, :] - (w - 1) / 2.0
    return y ** 2 + x ** 2 <= radius * radius


def zero_out_outside_radius(arr, radius, zero=0):
    mask = disk_mask(*arr.shape[:2], radius)
    arr[~mask] = zero
    return arr


def contrast(image):
    mask = ~np.all(image == 0, axis=2)
    fg = image.reshape(-1, 3)[mask.reshape(-1)]
    mins = fg.min(axis=0)
    ranges = fg.max(axis=0) - mins
    ranges[ranges <= 0] = 255
    scale = 255.0 / ranges
    out = (image - mins[np.newaxis, np.newaxis, :]) * scale[np.newaxis, np.newaxis, :]
    out[~mask] = 0
    return np.clip(out, 0, 255).astype(np.uint8)


def rgb_to_canny(rgb, outer_radius=23, inner_radius=19, final_shape=(50, 50)):
    rgb = contrast(zero_out_outside_radius(rgb, outer_radius))
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 1.0)
    g_bit = skeletonize(cv2.Canny(g, 50, 150) > 0)
    out = zero_out_outside_radius(g_bit, inner_radius)
    return crop_and_pad(out, zero=0, shape=final_shape)


templateNames = [os.path.basename(f)[0] for f in templateFs]
assert len(set(templateNames)) == len(templateNames)
assert set(templateNames) == set("VM")
templates = [template_open(f) for f in templateFs]


def find_best_kernel(rgb, ktest=0):
    image = rgb_to_canny(rgb)
    scores = [
        correlate2d(image, kernel, mode='valid').max()
        for kernel in templates]
    vm = templateNames[np.argmax(scores)]

    if ktest:
        os.makedirs("board_storage/vm", exist_ok=True)
        while os.path.exists(f"board_storage/vm/{vm}{ktest}.png"):
            ktest += 1
        Image.fromarray(rgb).save(f"board_storage/vm/{vm}{ktest}.png")
        Image.fromarray(image).save(f"board_storage/vm/{vm}{ktest}x.png")

    return vm


def convert_to_example(f_name, t_name):
    Image.fromarray(rgb_to_canny(Image.open(f_name))).save(t_name)
