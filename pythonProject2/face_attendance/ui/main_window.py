import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from .. import config
from ..face_engine import FaceEngine
from .attendance_window import AttendanceWindow
from .recognize_window import RecognizeWindow
from .student_dialog import StudentDialog
from .train_dialog import TrainDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition Attendance System")
        self.resize(480, 420)

        self.engine = FaceEngine()

        title = QLabel("Face Recognition Attendance System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 12px;")

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_clock)
        self._timer.start(1000)
        self._tick_clock()

        students_button = self._make_button("Manage Students", self.open_students)
        train_button = self._make_button("Train Recognition Model", self.open_training)
        recognize_button = self._make_button("Take Attendance", self.open_recognition)
        records_button = self._make_button("Attendance Records", self.open_records)
        exit_button = self._make_button("Exit", self.close)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.clock_label)
        for button in (students_button, train_button, recognize_button, records_button, exit_button):
            layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _make_button(self, text: str, handler) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(44)
        button.clicked.connect(handler)
        return button

    def _tick_clock(self) -> None:
        self.clock_label.setText(datetime.now().strftime("%A, %d %B %Y  %H:%M:%S"))

    def open_students(self) -> None:
        StudentDialog(self.engine, parent=self).exec()

    def open_training(self) -> None:
        TrainDialog(self.engine, parent=self).exec()

    def open_recognition(self) -> None:
        RecognizeWindow(self.engine, parent=self).exec()

    def open_records(self) -> None:
        AttendanceWindow(parent=self).exec()


def run() -> None:
    config.ensure_data_dirs()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
