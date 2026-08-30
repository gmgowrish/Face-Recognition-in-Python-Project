import time

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
        self.resize(680, 600)

        self.engine = engine
        self.student_id = student_id
        self.target_count = config.FACE_SAMPLE_COUNT
        self.captured = engine.sample_count(student_id)
        self._latest_gray = None
        self._latest_box = None
        self._quality_ok = False
        self._quality_reason = ""
        self._duplicate_checked = False
        self._last_capture_time = 0.0

        self.video_label = QLabel("Starting camera...")
        self.video_label.setMinimumSize(640, 480)

        self.pose_label = QLabel()
        self.pose_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.status_label = QLabel(self._status_text())

        self.capture_button = QPushButton("Capture Now")
        self.capture_button.setToolTip("Samples are captured automatically -- this forces one immediately.")
        self.capture_button.clicked.connect(lambda: self._try_capture(auto=False))
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addWidget(self.capture_button)
        buttons.addWidget(self.back_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_label)
        layout.addWidget(self.pose_label)
        layout.addWidget(self.status_label)
        layout.addLayout(buttons)

        self.feed = CameraFeed(parent=self)
        self.feed.frame_ready.connect(self.on_frame)
        self.feed.error.connect(self.on_error)
        if not self.feed.start():
            self.capture_button.setEnabled(False)

    def _status_text(self, note: str = "") -> str:
        base = f"Captured {self.captured}/{self.target_count} samples for this student."
        return f"{base} {note}".strip()

    def _pose_instruction(self) -> str:
        progress = self.captured / self.target_count if self.target_count else 1.0
        instruction = config.POSE_GUIDE[0][1]
        for threshold, text in config.POSE_GUIDE:
            if progress >= threshold:
                instruction = text
        return instruction

    def on_frame(self, frame) -> None:
        gray, faces = self.engine.detect_faces(frame)
        box = self.engine.largest_face(faces)
        self._latest_gray = gray
        self._latest_box = box

        if self.captured >= self.target_count:
            self.pose_label.setText("Done!")
        else:
            self.pose_label.setText(self._pose_instruction())

        if box is not None:
            x, y, w, h = box
            self._quality_ok, self._quality_reason = self.engine.capture_quality(gray, box)
            color = (0, 200, 0) if self._quality_ok else (0, 140, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            if not self._quality_ok:
                cv2.putText(frame, self._quality_reason, (x, max(y - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                self.status_label.setText(self._status_text(f"- {self._quality_reason}"))
            else:
                self.status_label.setText(self._status_text())
                self._try_capture(auto=True)
        else:
            self._quality_ok = False
            self._quality_reason = "No face detected"
            self.status_label.setText(self._status_text("- No face detected."))

        self.video_label.setPixmap(frame_to_pixmap(frame))

    def on_error(self, message: str) -> None:
        QMessageBox.warning(self, "Camera error", message)
        self.capture_button.setEnabled(False)

    def _confirm_not_a_duplicate(self) -> bool:
        """Warn if this face already matches a different, already-trained student."""
        match = self.engine.find_duplicate(self._latest_gray, self._latest_box)
        if match is None:
            return True
        matched_student_id, distance = match
        if matched_student_id == self.student_id:
            return True
        proceed = QMessageBox.question(
            self,
            "Possible duplicate face",
            "This face already matches an existing registered student "
            f"(student ID {matched_student_id}, match distance {distance:.0f}).\n\n"
            "Continue capturing samples for this student anyway?",
        )
        return proceed == QMessageBox.StandardButton.Yes

    def _try_capture(self, auto: bool) -> None:
        if self.captured >= self.target_count:
            return
        if self._latest_gray is None or self._latest_box is None:
            if not auto:
                QMessageBox.information(self, "No face detected", "Position your face in the frame and try again.")
            return
        if not self._quality_ok:
            if not auto:
                QMessageBox.information(self, "Not good enough yet", self._quality_reason)
            return
        if auto and (time.monotonic() - self._last_capture_time) < config.CAPTURE_COOLDOWN_SECONDS:
            return

        if not self._duplicate_checked:
            self._duplicate_checked = True
            if not self._confirm_not_a_duplicate():
                return

        self.captured += 1
        self._last_capture_time = time.monotonic()
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
