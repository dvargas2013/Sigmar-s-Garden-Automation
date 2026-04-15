import os

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageGrab

STORED = list("0SAFWEQLTICRG")
d_name = "board_storage"


def fname(s):
    return f"{d_name}/{s}.png"


def image_open(f):
    return np.asarray(Image.open(f).convert("RGB"))


BD = image_open("markers/board.png")
TL = BD[:140, :140, :]
BR = BD[-150:, -150:, :]


def stored():
    return np.array([0, 0]), [image_open(fname(s)) for s in STORED]


def live(store=False):
    while (f := frame()) is None:
        pyautogui.sleep(1)
    (posx, posy), root = f
    frames = [root]
    h, w = root.shape[:2]

    y = posy + 725
    for x in [17, 22, 26, 31, 35, 41, 46, 50, 54, 58, 62, 66]:
        x = posx + x * 10
        pyautogui.mouseDown(x, y)
        data = np.asarray(ImageGrab.grab().convert("RGB"))[posy:, posx:][:h, :w]
        pyautogui.mouseUp()
        assert pyautogui.position() == (x, y)
        frames.append(data)

    if store:
        os.makedirs(d_name, exist_ok=True)
        for n, f in zip(STORED, frames):
            Image.fromarray(f).save(fname(n))

    return np.array([posx, posy]), frames


def find_sub_image(hay, needle):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(cv2.matchTemplate(hay, needle, cv2.TM_CCOEFF_NORMED))
    return max_loc if max_val > 0.9 else None


def frame():
    data = np.asarray(ImageGrab.grab().convert("RGB"))
    if (tlf := find_sub_image(data, TL)) is None: return None
    if (brf := find_sub_image(data, BR)) is None: return None
    brf0, brf1 = brf
    tlf0, tlf1 = tlf
    return np.array(tlf), data[tlf1:brf1 + 150 + 70, tlf0:brf0 + 150]
