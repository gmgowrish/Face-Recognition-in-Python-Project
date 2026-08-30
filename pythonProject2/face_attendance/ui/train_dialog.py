from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

from ..face_engine import FaceEngine


class _TrainWorker(QThread):
    finished_ok = pyqtSignal(int)
    failed = pyqtSignal(str)

    def __init__(self, engine: FaceEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

    def run(self) -> None:
        try:
            count = self.engine.train()
        except Exception as exc:  # noqa: BLE001 - surfaced to the user as-is
            self.failed.emit(str(exc))
        else:
            self.finished_ok.emit(count)


class TrainDialog(QDialog):
    def __init__(self, engine: FaceEngine, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Train Recognition Model")
        self.resize(360, 140)

        self.status_label = QLabel("Train the model on all captured face samples.")
        self.train_button = QPushButton("Start Training")
        self.train_button.clicked.connect(self.start_training)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.train_button)

        self.engine = engine
        self._worker: _TrainWorker | None = None

    def start_training(self) -> None:
        self.train_button.setEnabled(False)
        self.status_label.setText("Training in progress...")
        self._worker = _TrainWorker(self.engine, parent=self)
        self._worker.finished_ok.connect(self.on_success)
        self._worker.failed.connect(self.on_failure)
        self._worker.start()

    def on_success(self, sample_count: int) -> None:
        self.status_label.setText(f"Training complete: {sample_count} samples used.")
        self.train_button.setEnabled(True)

    def on_failure(self, message: str) -> None:
        QMessageBox.warning(self, "Training failed", message)
        self.status_label.setText("Training failed. See message above.")
        self.train_button.setEnabled(True)
