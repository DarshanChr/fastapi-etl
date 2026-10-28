from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+psycopg2://admin:admin@postgress:5432/etldb"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        logger.exception("Database session operation failed")
        db.rollback()
        raise
    finally:
        db.close()

Base = declarative_base()