from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .. import attendance_service
from ..db import get_session
from ..face_engine import FaceEngine
from .capture_dialog import CaptureDialog

COLUMNS = ["ID", "Roll No.", "Name", "Department", "Course", "Year", "Face Samples"]


class StudentDialog(QDialog):
    def __init__(self, engine: FaceEngine, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Students")
        self.resize(760, 480)
        self.engine = engine

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.roll_input = QLineEdit()
        self.name_input = QLineEdit()
        self.department_input = QLineEdit()
        self.course_input = QLineEdit()
        self.year_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Roll number", self.roll_input)
        form.addRow("Name", self.name_input)
        form.addRow("Department", self.department_input)
        form.addRow("Course", self.course_input)
        form.addRow("Year", self.year_input)

        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_student)

        capture_button = QPushButton("Capture Face Samples")
        capture_button.clicked.connect(self.capture_samples)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.addWidget(add_button)
        button_row.addWidget(capture_button)
        button_row.addWidget(delete_button)
        button_row.addWidget(back_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        session = get_session()
        try:
            students = attendance_service.list_students(session)
        finally:
            session.close()

        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            values = [
                str(student.id),
                student.roll_number,
                student.name,
                student.department,
                student.course,
                student.year,
                str(self.engine.sample_count(student.id)),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def add_student(self) -> None:
        roll_number = self.roll_input.text().strip()
        name = self.name_input.text().strip()
        department = self.department_input.text().strip()
        if not roll_number or not name or not department:
            QMessageBox.information(self, "Missing details", "Roll number, name and department are required.")
            return

        session = get_session()
        try:
            attendance_service.add_student(
                session,
                roll_number=roll_number,
                name=name,
                department=department,
                course=self.course_input.text().strip(),
                year=self.year_input.text().strip(),
            )
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Duplicate roll number", f"A student with roll number '{roll_number}' already exists.")
            return
        except SQLAlchemyError as exc:
            session.rollback()
            QMessageBox.critical(self, "Database error", f"Could not save the student:\n{exc}")
            return
        finally:
            session.close()

        for field in (self.roll_input, self.name_input, self.department_input, self.course_input, self.year_input):
            field.clear()
        self.refresh()

    def selected_student_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def capture_samples(self) -> None:
        student_id = self.selected_student_id()
        if student_id is None:
            QMessageBox.information(self, "No selection", "Select a student first.")
            return
        name = self.table.item(self.table.currentRow(), 2).text()
        dialog = CaptureDialog(student_id, name, self.engine, parent=self)
        dialog.exec()
        self.refresh()

    def delete_selected(self) -> None:
        student_id = self.selected_student_id()
        if student_id is None:
            QMessageBox.information(self, "No selection", "Select a student first.")
            return
        confirm = QMessageBox.question(
            self, "Confirm delete", "Delete this student and their attendance history?"
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        session = get_session()
        try:
            attendance_service.delete_student(session, student_id)
        finally:
            session.close()
        self.engine.clear_samples(student_id)
        self.refresh()
