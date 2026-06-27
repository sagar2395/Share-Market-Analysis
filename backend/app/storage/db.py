"""SQLite (via SQLAlchemy) — mutable application state.

Holds the owner's watchlist and portfolio. Small, transactional, zero-config. Large
append-only price history lives separately in DuckDB (see ``storage/history.py``).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine():
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    db_path = settings.data_dir / "app.sqlite"
    return create_engine(f"sqlite:///{db_path}", future=True)


_engine_instance = None
_SessionLocal: sessionmaker[Session] | None = None


def init_db() -> None:
    """Create tables if they don't exist."""
    global _engine_instance, _SessionLocal
    if _engine_instance is None:
        _engine_instance = _engine()
        _SessionLocal = sessionmaker(bind=_engine_instance, expire_on_commit=False, future=True)
    # Import models so they register on Base.metadata before create_all.
    from app.storage import models  # noqa: F401

    Base.metadata.create_all(_engine_instance)


@contextmanager
def session_scope() -> Iterator[Session]:
    if _SessionLocal is None:
        init_db()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
