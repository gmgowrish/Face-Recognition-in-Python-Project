from datetime import date

import pytest
from sqlalchemy.orm import sessionmaker

from face_attendance import analytics, attendance_service
from face_attendance.db import make_engine


@pytest.fixture()
def session():
    engine = make_engine(db_path=":memory:")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    s = Session()
    try:
        yield s
    finally:
        s.close()


def test_list_attendance_months_returns_distinct_sorted_months(session):
    ada = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    attendance_service.mark_present(session, ada.id, distance=40.0, on_date=date(2026, 7, 15))
    attendance_service.mark_present(session, ada.id, distance=40.0, on_date=date(2026, 8, 1))

    assert analytics.list_attendance_months(session) == ["2026-07", "2026-08"]


def test_monthly_summary_aggregates_daily_and_weekday_counts(session):
    ada = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    bob = attendance_service.add_student(session, roll_number="R2", name="Bob", department="EE")

    # 2026-08-03 is a Monday
    attendance_service.mark_present(session, ada.id, distance=30.0, on_date=date(2026, 8, 3))
    attendance_service.mark_present(session, bob.id, distance=35.0, on_date=date(2026, 8, 3))
    attendance_service.mark_present(session, ada.id, distance=32.0, on_date=date(2026, 8, 10))

    summary = analytics.monthly_summary(session, 2026, 8)

    assert summary.total_checkins == 3
    assert summary.unique_students == 2
    assert summary.daily_counts == {3: 2, 10: 1}
    assert summary.best_day == date(2026, 8, 3)
    assert summary.best_day_count == 2
    assert summary.department_counts == {"CS": 2, "EE": 1}
    assert summary.weekday_avg["Monday"] > 0


def test_monthly_summary_roster_counts_distinct_days_not_records(session):
    ada = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    attendance_service.mark_present(session, ada.id, distance=30.0, on_date=date(2026, 8, 3))
    attendance_service.mark_present(session, ada.id, distance=30.0, on_date=date(2026, 8, 4))

    summary = analytics.monthly_summary(session, 2026, 8)

    assert len(summary.roster) == 1
    assert summary.roster[0].days_present == 2
    assert summary.roster[0].last_seen == date(2026, 8, 4)


def test_monthly_summary_handles_a_month_with_no_records(session):
    summary = analytics.monthly_summary(session, 2026, 8)

    assert summary.total_checkins == 0
    assert summary.unique_students == 0
    assert summary.best_day is None
    assert summary.roster == []
