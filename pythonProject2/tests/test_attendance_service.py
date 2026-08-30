from datetime import date, timedelta

import pytest
from sqlalchemy.orm import sessionmaker

from face_attendance import attendance_service
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


def test_add_and_list_students(session):
    attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )
    attendance_service.add_student(
        session, roll_number="R2", name="Bob", department="EE"
    )

    students = attendance_service.list_students(session)
    assert [s.name for s in students] == ["Ada", "Bob"]


def test_mark_present_is_idempotent_per_day(session):
    student = attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )

    first = attendance_service.mark_present(session, student.id, distance=40.0)
    second = attendance_service.mark_present(session, student.id, distance=40.0)

    assert first is not None
    assert second is None
    assert len(attendance_service.list_attendance(session)) == 1


def test_mark_present_allows_a_new_record_on_a_different_day(session):
    student = attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )

    yesterday = date.today() - timedelta(days=1)
    attendance_service.mark_present(session, student.id, distance=40.0, on_date=yesterday)
    attendance_service.mark_present(session, student.id, distance=40.0)

    assert len(attendance_service.list_attendance(session)) == 2


def test_list_attendance_filters_by_date_range(session):
    student = attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )
    old_date = date.today() - timedelta(days=30)
    attendance_service.mark_present(session, student.id, distance=40.0, on_date=old_date)
    attendance_service.mark_present(session, student.id, distance=40.0)

    recent = attendance_service.list_attendance(session, date_from=date.today() - timedelta(days=1))
    assert len(recent) == 1


def test_delete_student_removes_attendance_history(session):
    student = attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )
    attendance_service.mark_present(session, student.id, distance=40.0)

    attendance_service.delete_student(session, student.id)

    assert attendance_service.list_students(session) == []
    assert attendance_service.list_attendance(session) == []
