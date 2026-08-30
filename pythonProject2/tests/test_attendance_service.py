import csv
from datetime import date, timedelta

import numpy as np
import pytest
from sqlalchemy.orm import sessionmaker

from face_attendance import attendance_service, config
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


def test_list_attendance_records_are_usable_after_the_session_closes():
    # Regression test: attendance_window.py reads record.student.* only
    # after the session that fetched the records has been closed, which
    # raised DetachedInstanceError unless the relationship is eager-loaded.
    engine = make_engine(db_path=":memory:")
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    session = Session()
    student = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    attendance_service.mark_present(session, student.id, distance=40.0)
    records = attendance_service.list_attendance(session)
    session.close()

    assert records[0].student.name == "Ada"


def test_save_snapshot_writes_a_file_and_records_its_path(session, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SNAPSHOT_DIR", tmp_path / "photos")
    student = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    record = attendance_service.mark_present(session, student.id, distance=40.0)

    face = np.zeros((50, 50, 3), dtype=np.uint8)
    path = attendance_service.save_snapshot(session, record, face)

    assert path.exists()
    assert record.snapshot_path == str(path)


def test_export_csv_includes_the_day_name(session, tmp_path):
    student = attendance_service.add_student(session, roll_number="R1", name="Ada", department="CS")
    known_monday = date(2026, 8, 24)
    attendance_service.mark_present(session, student.id, distance=40.0, on_date=known_monday)
    records = attendance_service.list_attendance(session)

    path = attendance_service.export_csv(records, tmp_path / "out.csv")

    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    assert rows[0]["Date"] == "2026-08-24"
    assert rows[0]["Day"] == "Monday"
    assert rows[0]["Name"] == "Ada"


def test_default_export_filename_includes_date_and_day_name():
    single_day = attendance_service.default_export_filename(date(2026, 8, 24), date(2026, 8, 24))
    assert single_day == "attendance_2026-08-24_Monday.csv"

    range_name = attendance_service.default_export_filename(date(2026, 8, 1), date(2026, 8, 24))
    assert range_name == "attendance_2026-08-01_to_2026-08-24.csv"


def test_delete_student_removes_attendance_history(session):
    student = attendance_service.add_student(
        session, roll_number="R1", name="Ada", department="CS"
    )
    attendance_service.mark_present(session, student.id, distance=40.0)

    attendance_service.delete_student(session, student.id)

    assert attendance_service.list_students(session) == []
    assert attendance_service.list_attendance(session) == []
