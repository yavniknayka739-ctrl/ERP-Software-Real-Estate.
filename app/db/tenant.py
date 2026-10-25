import os
import shutil
import uuid
from fastapi import Request, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import get_db, SessionLocal
from app.core.config import settings

DEMO_DB_DIR = "./demo_dbs"
os.makedirs(DEMO_DB_DIR, exist_ok=True)

# Cache engines to avoid leaking connections
_demo_engines = {}

def get_demo_db_path(demo_id: str) -> str:
    return os.path.join(DEMO_DB_DIR, f"demo_{demo_id}.db")

def create_demo_session(demo_id: str):
    source_db = "demo_base.db"
    target_db = get_demo_db_path(demo_id)
    if not os.path.exists(target_db):
        if os.path.exists(source_db):
            shutil.copy2(source_db, target_db)
        else:
            # For tests that don't seed the DB
            pass

    if demo_id not in _demo_engines:
        engine = create_engine(
            f"sqlite:///{target_db}",
            connect_args={"check_same_thread": False},
            echo=False
        )
        _demo_engines[demo_id] = engine

    return sessionmaker(autocommit=False, autoflush=False, bind=_demo_engines[demo_id])

def get_tenant_db(request: Request):
    if not settings.DEMO_MODE:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
        return

    demo_id = request.cookies.get("demo_id")
    if not demo_id:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
        return

    DemoSessionLocal = create_demo_session(demo_id)
    db = DemoSessionLocal()
    try:
        yield db
    finally:
        db.close()
