from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Enable WAL mode for SQLite
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
