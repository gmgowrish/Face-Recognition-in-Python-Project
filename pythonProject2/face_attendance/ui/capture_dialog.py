import cv2
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout

from .. import config
from ..face_engine import FaceEngine
from .camera_feed import CameraFeed
from .qt_utils import frame_to_pixmap


class CaptureDialog(QDialog):
    def __init__(self, student_id: int, student_name: str, engine: FaceEngine, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Capture Face Samples - {student_name}")
        self.resize(680, 560)

        self.engine = engine
        self.student_id = student_id
        self.target_count = config.FACE_SAMPLE_COUNT
        self.captured = engine.sample_count(student_id)
        self._latest_gray = None
        self._latest_box = None

        self.video_label = QLabel("Starting camera...")
        self.video_label.setMinimumSize(640, 480)

        self.status_label = QLabel(self._status_text())

        self.capture_button = QPushButton("Capture Sample")
        self.capture_button.clicked.connect(self.capture_sample)
        self.close_button = QPushButton("Done")
        self.close_button.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addWidget(self.capture_button)
        buttons.addWidget(self.close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        layout.addLayout(buttons)

        self.feed = CameraFeed(parent=self)
        self.feed.frame_ready.connect(self.on_frame)
        self.feed.error.connect(self.on_error)
        if not self.feed.start():
            self.capture_button.setEnabled(False)

    def _status_text(self) -> str:
        return f"Captured {self.captured}/{self.target_count} samples for this student."

    def on_frame(self, frame) -> None:
        gray, faces = self.engine.detect_faces(frame)
        box = self.engine.largest_face(faces)
        self._latest_gray = gray
        self._latest_box = box
        if box is not None:
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
        self.video_label.setPixmap(frame_to_pixmap(frame))

    def on_error(self, message: str) -> None:
        QMessageBox.warning(self, "Camera error", message)
        self.capture_button.setEnabled(False)

    def capture_sample(self) -> None:
        if self._latest_gray is None or self._latest_box is None:
            QMessageBox.information(self, "No face detected", "Position your face in the frame and try again.")
            return
        self.captured += 1
        self.engine.save_sample(self.student_id, self._latest_gray, self._latest_box, self.captured)
        self.status_label.setText(self._status_text())
        if self.captured >= self.target_count:
            QMessageBox.information(self, "Done", "Enough samples captured. Train the system next.")
            self.accept()

    def reject(self) -> None:
        self.feed.stop()
        super().reject()

    def accept(self) -> None:
        self.feed.stop()
        super().accept()
