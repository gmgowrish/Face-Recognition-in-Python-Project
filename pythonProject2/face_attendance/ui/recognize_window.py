import cv2
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

from .. import attendance_service, config
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

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        layout.addWidget(back_button)

        # Caches each recognized student's label for this window's lifetime,
        # so we hit the database once per student instead of every frame,
        # and can tell "just marked" apart from "already marked earlier".
        self._session_labels: dict[int, str] = {}

        # Requires several consecutive frames to agree on the same student
        # before accepting the match -- a single frame's lucky low distance
        # (noise, motion blur, a poor match against a sparsely-trained
        # model) isn't enough to put someone's name on a stranger's face.
        self._pending_student_id: int | None = None
        self._pending_streak = 0

        self.feed = CameraFeed(parent=self)
        self.feed.frame_ready.connect(self.on_frame)
        self.feed.error.connect(self.on_error)
        if self.recognizer is not None and not self.feed.start():
            back_button.setText("Close")

    def on_frame(self, frame) -> None:
        gray, faces = self.engine.detect_faces(frame)
        box = self.engine.largest_face(faces)

        if box is None:
            self._pending_student_id = None
            self._pending_streak = 0
            self.video_label.setPixmap(frame_to_pixmap(frame))
            return

        x, y, w, h = box
        if self.recognizer is None:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            self.video_label.setPixmap(frame_to_pixmap(frame))
            return

        student_id, distance = self.engine.predict(self.recognizer, gray, box)
        candidate_id = student_id if self.engine.is_match(distance) else None

        if candidate_id is not None and candidate_id == self._pending_student_id:
            self._pending_streak += 1
        else:
            self._pending_student_id = candidate_id
            self._pending_streak = 1 if candidate_id is not None else 0

        if candidate_id is None:
            label, color = "Unknown", (0, 0, 255)
        elif self._pending_streak >= config.RECOGNITION_CONFIRM_FRAMES:
            label = self._mark_and_label(candidate_id, distance, frame, box)
            color = (0, 200, 0)
        else:
            label = f"Verifying... ({self._pending_streak}/{config.RECOGNITION_CONFIRM_FRAMES})"
            color = (0, 200, 200)

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, max(y - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        self.video_label.setPixmap(frame_to_pixmap(frame))

    def _mark_and_label(self, student_id: int, distance: float, frame, box) -> str:
        if student_id in self._session_labels:
            return self._session_labels[student_id]

        session = get_session()
        try:
            student = attendance_service.get_student(session, student_id)
            if student is None:
                return "Unknown"

            record = attendance_service.mark_present(session, student_id, distance)
            if record is not None:
                x, y, w, h = box
                attendance_service.save_snapshot(session, record, frame[y : y + h, x : x + w])
                label = f"{student.name} - marked present"
                self.status_label.setText(f"Marked present: {student.name} ({student.roll_number})")
            else:
                label = f"{student.name} - already marked"
                self.status_label.setText(f"{student.name} ({student.roll_number}) already marked present today.")

            self._session_labels[student_id] = label
            return label
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
