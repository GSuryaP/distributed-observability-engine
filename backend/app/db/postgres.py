from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from backend.app.config import settings
from backend.app.models.db_models import Base

logger = logging.getLogger("postgres_db")

try:
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info("Connected to PostgreSQL database successfully.")
except Exception as e:
    logger.warning(f"Failed to connect to PostgreSQL ({e}). Using SQLite fallback database.")
    sqlite_url = "sqlite:///./nexus_fallback.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
