from PyQt5.QtGui import QImage
import numpy as np
import cv2

def cvframe_to_qimage(frame):
    """
    Convert an OpenCV BGR frame to QImage
    """
    if frame is None:
        return QImage()
    h, w = frame.shape[:2]
    if frame.ndim == 2:
        img = QImage(frame.data, w, h, w, QImage.Format_Grayscale8)
    else:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return img.copy()