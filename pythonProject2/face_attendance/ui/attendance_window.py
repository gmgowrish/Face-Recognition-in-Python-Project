from datetime import date

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .. import attendance_service
from ..db import get_session
from ..models import AttendanceRecord

COLUMNS = ["Date", "Time", "Roll No.", "Name", "Department", "Match Distance"]
PHOTO_BOX_SIZE = 140


class AttendanceWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Attendance Records")
        self.resize(900, 480)

        self._current_records: list[AttendanceRecord] = []

        today = QDate.currentDate()
        self.from_date = QDateEdit(today.addDays(-7))
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit(today)
        self.to_date.setCalendarPopup(True)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        export_button = QPushButton("Export CSV")
        export_button.clicked.connect(self.export)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.accept)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("From"))
        filter_row.addWidget(self.from_date)
        filter_row.addWidget(QLabel("To"))
        filter_row.addWidget(self.to_date)
        filter_row.addWidget(refresh_button)
        filter_row.addWidget(export_button)
        filter_row.addWidget(back_button)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._show_selected_photo)

        self.photo_caption = QLabel("Select a record to see its photo")
        self.photo_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_box = QLabel("No photo")
        self.photo_box.setFixedSize(PHOTO_BOX_SIZE, PHOTO_BOX_SIZE)
        self.photo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_box.setStyleSheet("border: 1px solid palette(mid);")

        photo_column = QVBoxLayout()
        photo_column.addWidget(self.photo_caption)
        photo_column.addWidget(self.photo_box)
        photo_column.addStretch()

        content_row = QHBoxLayout()
        content_row.addWidget(self.table, stretch=1)
        content_row.addLayout(photo_column)

        layout = QVBoxLayout(self)
        layout.addLayout(filter_row)
        layout.addLayout(content_row)

        self.refresh()

    def _date_range(self) -> tuple[date, date]:
        return self.from_date.date().toPyDate(), self.to_date.date().toPyDate()

    def _records(self) -> list[AttendanceRecord]:
        date_from, date_to = self._date_range()
        session = get_session()
        try:
            return attendance_service.list_attendance(session, date_from=date_from, date_to=date_to)
        finally:
            session.close()

    def refresh(self) -> None:
        self._current_records = self._records()
        self.table.setRowCount(len(self._current_records))
        for row, record in enumerate(self._current_records):
            values = [
                record.date.isoformat(),
                record.marked_at.strftime("%H:%M:%S"),
                record.student.roll_number,
                record.student.name,
                record.student.department,
                f"{record.distance:.1f}",
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.photo_box.setText("No photo")
        self.photo_box.setPixmap(QPixmap())
        self.photo_caption.setText("Select a record to see its photo")

    def _show_selected_photo(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._current_records):
            return
        record = self._current_records[row]
        self.photo_caption.setText(f"{record.student.name} ({record.student.roll_number}) - {record.date.isoformat()}")
        if not record.snapshot_path:
            self.photo_box.setPixmap(QPixmap())
            self.photo_box.setText("No photo")
            return
        pixmap = QPixmap(record.snapshot_path)
        if pixmap.isNull():
            self.photo_box.setPixmap(QPixmap())
            self.photo_box.setText("Photo missing")
            return
        self.photo_box.setPixmap(
            pixmap.scaled(
                PHOTO_BOX_SIZE, PHOTO_BOX_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        )

    def export(self) -> None:
        records = self._records()
        if not records:
            QMessageBox.information(self, "Nothing to export", "There are no records in this date range.")
            return
        date_from, date_to = self._date_range()
        default_name = attendance_service.default_export_filename(date_from, date_to)
        path, _ = QFileDialog.getSaveFileName(self, "Export attendance", default_name, "CSV files (*.csv)")
        if not path:
            return
        attendance_service.export_csv(records, path)
        QMessageBox.information(self, "Exported", f"Saved {len(records)} records to {path}")
