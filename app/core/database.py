from typing import Any, Generator


from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings
import logging

engine = create_engine(settings.DB_URL, echo=True, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("DB rollback due to error")
        raise
    finally:
        db.close()
