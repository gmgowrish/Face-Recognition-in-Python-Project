from datetime import date

from PyQt6.QtCore import QDate
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

COLUMNS = ["Date", "Time", "Roll No.", "Name", "Department", "Match Distance"]


class AttendanceWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Attendance Records")
        self.resize(760, 480)

        today = QDate.currentDate()
        self.from_date = QDateEdit(today.addDays(-7))
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit(today)
        self.to_date.setCalendarPopup(True)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        export_button = QPushButton("Export CSV")
        export_button.clicked.connect(self.export)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("From"))
        filter_row.addWidget(self.from_date)
        filter_row.addWidget(QLabel("To"))
        filter_row.addWidget(self.to_date)
        filter_row.addWidget(refresh_button)
        filter_row.addWidget(export_button)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout(self)
        layout.addLayout(filter_row)
        layout.addWidget(self.table)

        self.refresh()

    def _date_range(self) -> tuple[date, date]:
        return self.from_date.date().toPyDate(), self.to_date.date().toPyDate()

    def _records(self):
        date_from, date_to = self._date_range()
        session = get_session()
        try:
            return attendance_service.list_attendance(session, date_from=date_from, date_to=date_to)
        finally:
            session.close()

    def refresh(self) -> None:
        records = self._records()
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
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

    def export(self) -> None:
        records = self._records()
        if not records:
            QMessageBox.information(self, "Nothing to export", "There are no records in this date range.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export attendance", "attendance.csv", "CSV files (*.csv)")
        if not path:
            return
        attendance_service.export_csv(records, path)
        QMessageBox.information(self, "Exported", f"Saved {len(records)} records to {path}")
