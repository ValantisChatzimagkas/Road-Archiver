from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings

engine = create_engine(settings.DB_URL, echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, Any, None]:
    """
    Used for database dependency injection.
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
