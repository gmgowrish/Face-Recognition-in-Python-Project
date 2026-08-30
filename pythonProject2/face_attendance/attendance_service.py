import csv
from datetime import date as date_type
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AttendanceRecord, Student


def add_student(
    session: Session,
    *,
    roll_number: str,
    name: str,
    department: str,
    course: str = "",
    year: str = "",
    email: str | None = None,
    phone: str | None = None,
) -> Student:
    student = Student(
        roll_number=roll_number,
        name=name,
        department=department,
        course=course,
        year=year,
        email=email,
        phone=phone,
    )
    session.add(student)
    session.commit()
    return student


def list_students(session: Session) -> list[Student]:
    return list(session.scalars(select(Student).order_by(Student.name)))


def get_student(session: Session, student_id: int) -> Student | None:
    return session.get(Student, student_id)


def delete_student(session: Session, student_id: int) -> None:
    student = session.get(Student, student_id)
    if student is not None:
        session.delete(student)
        session.commit()


def mark_present(
    session: Session,
    student_id: int,
    distance: float,
    on_date: date_type | None = None,
) -> AttendanceRecord | None:
    """Record a student as present for the day. Returns None if already marked today."""
    on_date = on_date or date_type.today()
    existing = session.scalar(
        select(AttendanceRecord).where(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.date == on_date,
        )
    )
    if existing is not None:
        return None

    record = AttendanceRecord(student_id=student_id, date=on_date, distance=distance)
    session.add(record)
    session.commit()
    return record


def list_attendance(
    session: Session,
    *,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
    student_id: int | None = None,
) -> list[AttendanceRecord]:
    stmt = select(AttendanceRecord).order_by(AttendanceRecord.date.desc(), AttendanceRecord.marked_at.desc())
    if date_from is not None:
        stmt = stmt.where(AttendanceRecord.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(AttendanceRecord.date <= date_to)
    if student_id is not None:
        stmt = stmt.where(AttendanceRecord.student_id == student_id)
    return list(session.scalars(stmt))


def export_csv(records: list[AttendanceRecord], path: Path) -> Path:
    path = Path(path)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Time", "Roll Number", "Name", "Department", "Match Distance"])
        for record in records:
            writer.writerow(
                [
                    record.date.isoformat(),
                    record.marked_at.strftime("%H:%M:%S"),
                    record.student.roll_number,
                    record.student.name,
                    record.student.department,
                    f"{record.distance:.1f}",
                ]
            )
    return path
