import cv2
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

from .. import attendance_service
from ..db import get_session
from ..face_engine import FaceEngine
from .camera_feed import CameraFeed
from .qt_utils import frame_to_pixmap


class RecognizeWindow(QDialog):
    def __init__(self, engine: FaceEngine, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Take Attendance")
        self.resize(680, 560)
        self.engine = engine

        try:
            self.recognizer = engine.load_recognizer()
        except RuntimeError as exc:
            QMessageBox.warning(self, "Not trained", str(exc))
            self.recognizer = None

        self.video_label = QLabel("Starting camera...")
        self.video_label.setMinimumSize(640, 480)
        self.status_label = QLabel("Looking for a face...")

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        layout.addWidget(stop_button)

        self._marked_this_session: set[int] = set()

        self.feed = CameraFeed(parent=self)
        self.feed.frame_ready.connect(self.on_frame)
        self.feed.error.connect(self.on_error)
        if self.recognizer is not None and not self.feed.start():
            stop_button.setText("Close")

    def on_frame(self, frame) -> None:
        gray, faces = self.engine.detect_faces(frame)

        for x, y, w, h in faces:
            if self.recognizer is None:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                continue

            student_id, distance = self.engine.predict(self.recognizer, gray, (x, y, w, h))
            if self.engine.is_match(distance):
                label = self._mark_and_label(student_id, distance)
                color = (0, 200, 0)
            else:
                label = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, max(y - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        self.video_label.setPixmap(frame_to_pixmap(frame))

    def _mark_and_label(self, student_id: int, distance: float) -> str:
        session = get_session()
        try:
            student = attendance_service.get_student(session, student_id)
            if student is None:
                return "Unknown"

            if student_id not in self._marked_this_session:
                record = attendance_service.mark_present(session, student_id, distance)
                if record is not None:
                    self._marked_this_session.add(student_id)
                    self.status_label.setText(f"Marked present: {student.name} ({student.roll_number})")
                else:
                    self._marked_this_session.add(student_id)

            return f"{student.name} ({distance:.0f})"
        finally:
            session.close()

    def on_error(self, message: str) -> None:
        QMessageBox.warning(self, "Camera error", message)

    def reject(self) -> None:
        self.feed.stop()
        super().reject()

    def accept(self) -> None:
        self.feed.stop()
        super().accept()
