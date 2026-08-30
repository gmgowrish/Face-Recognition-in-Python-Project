import calendar
from dataclasses import dataclass, field
from datetime import date as date_type

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import attendance_service
from .models import AttendanceRecord

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class StudentMonthStat:
    roll_number: str
    name: str
    department: str
    days_present: int
    last_seen: date_type


@dataclass
class MonthlySummary:
    year: int
    month: int
    days_in_month: int
    elapsed_days: int  # days.this month up to today if it's the current month, else all of them
    total_checkins: int
    unique_students: int
    avg_per_day: float
    best_day: date_type | None
    best_day_count: int
    daily_counts: dict[int, int]  # day-of-month (1-31) -> count
    weekday_avg: dict[str, float] = field(default_factory=dict)  # weekday name -> avg check-ins
    department_counts: dict[str, int] = field(default_factory=dict)
    roster: list[StudentMonthStat] = field(default_factory=list)


def list_attendance_months(session: Session) -> list[str]:
    """Distinct 'YYYY-MM' months that have at least one attendance record, sorted ascending."""
    dates = session.scalars(select(AttendanceRecord.date).distinct())
    months = {d.strftime("%Y-%m") for d in dates}
    return sorted(months)


def monthly_summary(session: Session, year: int, month: int) -> MonthlySummary:
    days_in_month = calendar.monthrange(year, month)[1]
    date_from = date_type(year, month, 1)
    date_to = date_type(year, month, days_in_month)
    records = attendance_service.list_attendance(session, date_from=date_from, date_to=date_to)

    today = date_type.today()
    is_current_month = (today.year, today.month) == (year, month)
    elapsed_days = today.day if is_current_month else days_in_month

    daily_counts: dict[int, int] = {}
    weekday_counts: dict[str, int] = {w: 0 for w in WEEKDAY_NAMES}
    weekday_occurrences: dict[str, int] = {w: 0 for w in WEEKDAY_NAMES}
    department_counts: dict[str, int] = {}
    student_days: dict[str, set[date_type]] = {}
    student_info: dict[str, StudentMonthStat] = {}

    for d in range(1, days_in_month + 1):
        weekday_occurrences[WEEKDAY_NAMES[date_type(year, month, d).weekday()]] += 1

    for record in records:
        day_of_month = record.date.day
        daily_counts[day_of_month] = daily_counts.get(day_of_month, 0) + 1
        weekday_counts[WEEKDAY_NAMES[record.date.weekday()]] += 1
        department_counts[record.student.department] = department_counts.get(record.student.department, 0) + 1

        roll = record.student.roll_number
        student_days.setdefault(roll, set()).add(record.date)
        existing = student_info.get(roll)
        if existing is None or record.date > existing.last_seen:
            student_info[roll] = StudentMonthStat(
                roll_number=roll,
                name=record.student.name,
                department=record.student.department,
                days_present=0,
                last_seen=record.date,
            )

    for roll, days in student_days.items():
        student_info[roll].days_present = len(days)

    best_day_num = max(daily_counts, key=daily_counts.get) if daily_counts else None
    best_day = date_type(year, month, best_day_num) if best_day_num else None

    weekday_avg = {
        w: (weekday_counts[w] / weekday_occurrences[w] if weekday_occurrences[w] else 0.0) for w in WEEKDAY_NAMES
    }

    roster = sorted(student_info.values(), key=lambda s: s.days_present, reverse=True)

    return MonthlySummary(
        year=year,
        month=month,
        days_in_month=days_in_month,
        elapsed_days=elapsed_days,
        total_checkins=len(records),
        unique_students=len(student_days),
        avg_per_day=(len(records) / elapsed_days) if elapsed_days else 0.0,
        best_day=best_day,
        best_day_count=daily_counts.get(best_day_num, 0) if best_day_num else 0,
        daily_counts=daily_counts,
        weekday_avg=weekday_avg,
        department_counts=department_counts,
        roster=roster,
    )
