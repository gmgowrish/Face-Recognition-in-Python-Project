import sys
import traceback
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import config
from ..face_engine import FaceEngine
from .attendance_window import AttendanceWindow
from .dashboard_window import DashboardWindow
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
        dashboard_button = self._make_button("Dashboard", self.open_dashboard)
        exit_button = self._make_button("Exit", self.close)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.clock_label)
        for button in (students_button, train_button, recognize_button, records_button, dashboard_button, exit_button):
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

    def open_dashboard(self) -> None:
        DashboardWindow(parent=self).exec()


def _install_exception_hook() -> None:
    # PyQt6 aborts the whole process on an unhandled exception raised inside
    # a slot unless sys.excepthook is overridden -- with this in place, a bug
    # (or a real failure like a locked/unwritable database) shows a message
    # box instead of silently killing the app.
    def hook(exc_type, exc_value, exc_tb) -> None:
        traceback.print_exception(exc_type, exc_value, exc_tb)
        QMessageBox.critical(
            None,
            "Unexpected error",
            f"{exc_type.__name__}: {exc_value}\n\nSee the terminal output for details.",
        )

    sys.excepthook = hook


def run() -> None:
    config.ensure_data_dirs()
    app = QApplication(sys.argv)
    _install_exception_hook()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
