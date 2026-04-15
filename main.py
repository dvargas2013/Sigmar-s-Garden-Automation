import pyautogui

from SigmarsThreading import solver
from bucket_cropper import adjust_frames, flat_to_hex
from categories import categorize
from get_raw_data import live, stored

from_storage = False
debug = False


def hex_click(xys, y, x):
    return xys[y][x]


def clicker(pss, TLxy, xys):
    for ps in pss:
        x, y = pyautogui.position()
        for p in ps:
            x, y = TLxy + hex_click(xys, *p)
            pyautogui.moveTo(x, y)
            pyautogui.sleep(0.03)
            pyautogui.click()
        pyautogui.sleep(0.1)
        assert pyautogui.position() == (x, y)


def restart(TLxy):
    x, y = TLxy + [70, 720]
    pyautogui.moveTo(x, y)
    pyautogui.sleep(2)
    assert pyautogui.position() == (x, y)
    pyautogui.click()
    pyautogui.sleep(6)


while True:
    if from_storage:
        pos, frames = stored()
    else:
        pos, frames = live(store=debug)
    no_bg, flat_circles, datas = adjust_frames(frames)
    s = "".join(categorize(datas, c, debug) for c in flat_circles)
    hex_circles = flat_to_hex([(x, y) for x, y, r in flat_circles])

    x, y = pyautogui.position()
    path = solver(s, n_threads=2)
    assert pyautogui.position() == (x, y)

    if from_storage:
        break
    else:
        clicker(path, pos, hex_circles)
        restart(pos)
