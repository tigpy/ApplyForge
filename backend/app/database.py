"""SQLite engine + session helpers (SQLAlchemy 2.x)."""
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


_url = settings.sqlalchemy_url
_is_sqlite = _url.startswith("sqlite")
if _is_sqlite:
    db_file = _url.split("sqlite:///", 1)[1]
    if db_file and db_file != ":memory:":
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(_url, connect_args={"check_same_thread": False} if _is_sqlite else {})

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_conn, _record):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401  (register tables)

    Base.metadata.create_all(engine)
