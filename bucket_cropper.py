import cv2
import numpy as np
from skimage.measure import label

from get_raw_data import BD, STORED

BD_select = [slice(0, i) for i in BD.shape]

assert STORED[0] == "0"
CATEGORIES = ["VM", *STORED[1:]]


def select_diff(img, base=BD):
    if img.shape != BD.shape:
        img = img[*BD_select]
    if base.shape != BD.shape:
        base = base[*BD_select]
    mask = 1 + ((img - base).min(axis=2) == 0)
    mask2 = label(mask, connectivity=1) != 1
    return img * np.expand_dims(mask2, 2)


def find_circles(data):
    circles = cv2.HoughCircles(
        data,
        method=cv2.HOUGH_GRADIENT, dp=1.1, minDist=50,
        param1=70, param2=30, minRadius=26, maxRadius=34
    )
    if circles is None: return []
    return circles[0]


_91_circles = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6]


def find_grid(circles):
    assert len(circles) == 95
    circles = circles[np.lexsort((circles[:, 0],))][2:-2]
    circles = circles[np.lexsort((circles[:, 1],))]
    curr = 0
    for i in _91_circles:
        sub = circles[curr:curr + i]
        sub[:] = sub[np.lexsort((sub[:, 0],))]
        curr += i
    return np.round(circles).astype(int)


def flat_to_hex(fc):
    out = []
    i = 0
    for L in _91_circles:
        out.append(fc[i:i + L])
        i += L
    return out


def rgb_to_circles(rgb):
    return find_grid(find_circles(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)))


def adjust_frames(F):
    """converts the 13 frames into clean_board, circles, clean_frames
    clean_board = screen - board.png
    circles = different positions of the hex grid [(x,y,r),...][:91]
    clean_frames = [highlight(c) for c in CATEGORIES]
        where highlight would select only that part of the image
    """
    # out[0] will become "VM" category
    out = [np.array(clean := select_diff(F[0]))]
    for i, f in enumerate(F[1:], start=1):
        out.append(select_diff(F[0], f))
        out[0] *= out[-1] == 0

    return clean, rgb_to_circles(F[0]), np.array(out)
