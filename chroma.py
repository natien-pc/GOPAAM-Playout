import cv2
import numpy as np

def apply_chroma_key(foreground, background, key_color=(0,255,0), threshold=60, x=0, y=0):
    """
    Basic chroma key compositing: places 'foreground' over 'background' at (x,y),
    removing pixels close to key_color in the foreground.
    """
    fh, fw = foreground.shape[:2]
    bh, bw = background.shape[:2]
    if y + fh > bh or x + fw > bw:
        # simple clipping
        fh = min(fh, bh - y)
        fw = min(fw, bw - x)
        foreground = foreground[:fh, :fw]

    hsv = cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV)
    key_hsv = cv2.cvtColor(np.uint8([[key_color]]), cv2.COLOR_BGR2HSV)[0][0]
    lower = np.array([max(0, key_hsv[0] - 10), 50, 50])
    upper = np.array([min(179, key_hsv[0] + 10), 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask_inv = cv2.bitwise_not(mask)

    fg_fg = cv2.bitwise_and(foreground, foreground, mask=mask_inv)
    bg_roi = background[y:y+fh, x:x+fw]
    bg_bg = cv2.bitwise_and(bg_roi, bg_roi, mask=mask)
    composed = cv2.add(bg_bg, fg_fg)
    background[y:y+fh, x:x+fw] = composed
    return background