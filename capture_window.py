import mss
import numpy as np
import win32gui
import cv2


def get_client_rect(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"未找到窗口：{title}")

    # 1. 取客户区大小（不含边框）
    client_rect = win32gui.GetClientRect(hwnd)   # (left, top, right, bottom)
    w = client_rect[2] - client_rect[0]
    h = client_rect[3] - client_rect[1]

    # 2. 把客户区左上角转换成屏幕坐标
    left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    left, top = left_top

    return {"left": left, "top": top, "width": w, "height": h}


def capture_window(monitor):
    with mss.mss() as sct:
        # [, , 4] means BGRA format
        img = np.array(sct.grab(monitor))
        # Convert BGRA to BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img
