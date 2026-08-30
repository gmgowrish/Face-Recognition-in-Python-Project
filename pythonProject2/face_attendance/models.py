from datetime import date as date_type
from datetime import datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    roll_number: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    department: Mapped[str] = mapped_column(String(100))
    course: Mapped[str] = mapped_column(String(100), default="")
    year: Mapped[str] = mapped_column(String(20), default="")
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("student_id", "date", name="uq_student_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    date: Mapped[date_type] = mapped_column(Date, index=True)
    marked_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    distance: Mapped[float] = mapped_column(Float)

    student: Mapped["Student"] = relationship(back_populates="attendance_records")
