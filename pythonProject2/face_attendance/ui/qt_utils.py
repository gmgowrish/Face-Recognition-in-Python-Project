import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap


def frame_to_pixmap(frame_bgr: np.ndarray) -> QPixmap:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb.shape
    image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(image.copy())
