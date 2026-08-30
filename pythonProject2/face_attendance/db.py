from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import config
from .models import Base


def make_engine(db_path=None):
    path = db_path or config.DB_PATH
    if path == ":memory:":
        url = "sqlite:///:memory:"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path}"
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    return engine


_engine = None
_SessionLocal: sessionmaker | None = None


def get_session() -> Session:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = make_engine()
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _SessionLocal()
