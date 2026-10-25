from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./erp.db")

# For testing and demo purposes, we might use memory or multiple sqlite db files
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
poolclass = StaticPool if DATABASE_URL == "sqlite:///:memory:" else None

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=poolclass,
    echo=os.environ.get("ECHO_SQL", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
