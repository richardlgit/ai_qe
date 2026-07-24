from collections.abc import Generator

from sqlalchemy.orm import Session

from edgepulse.app.database.config import SessionLocal


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()