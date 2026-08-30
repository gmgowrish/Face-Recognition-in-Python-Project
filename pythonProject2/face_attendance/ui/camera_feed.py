import cv2
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from .. import config


class CameraFeed(QObject):
    """Polls a webcam on a Qt timer and emits each BGR frame.

    Kept on the main thread deliberately: frame handling here (Haar
    detection on a small preview frame) is cheap enough that a timer-driven
    loop stays responsive without the complexity of a worker thread.
    """

    frame_ready = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, camera_index: int | None = None, interval_ms: int = 33, parent=None):
        super().__init__(parent)
        self.camera_index = config.CAMERA_INDEX if camera_index is None else camera_index
        self._capture: cv2.VideoCapture | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._tick)

    def start(self) -> bool:
        self._capture = cv2.VideoCapture(self.camera_index)
        if not self._capture.isOpened():
            self.error.emit(f"Could not open camera index {self.camera_index}.")
            self._capture = None
            return False
        self._timer.start()
        return True

    def stop(self) -> None:
        self._timer.stop()
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _tick(self) -> None:
        if self._capture is None:
            return
        ok, frame = self._capture.read()
        if not ok:
            self.error.emit("Failed to read a frame from the camera.")
            return
        self.frame_ready.emit(frame)
