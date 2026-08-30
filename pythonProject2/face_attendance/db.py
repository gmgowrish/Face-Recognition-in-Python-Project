from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from . import config
from .models import AttendanceRecord, Base


def _add_missing_columns(engine) -> None:
    """Add new columns to an existing SQLite file without a migration tool.

    create_all() only creates tables that don't exist yet, so a column added
    to a model after someone already has a database on disk (e.g.
    snapshot_path) needs this instead.
    """
    inspector = inspect(engine)
    existing = {col["name"] for col in inspector.get_columns(AttendanceRecord.__tablename__)}
    if "snapshot_path" not in existing:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {AttendanceRecord.__tablename__} ADD COLUMN snapshot_path VARCHAR(255)"))


def make_engine(db_path=None):
    path = db_path or config.DB_PATH
    if path == ":memory:":
        url = "sqlite:///:memory:"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path}"
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)
    return engine


_engine = None
_SessionLocal: sessionmaker | None = None


def get_session() -> Session:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = make_engine()
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _SessionLocal()
