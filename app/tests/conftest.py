import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.main import app
from app.db.database import Base
from app.db.tenant import get_tenant_db
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash
from app.core.auth import create_session

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Start a fresh transaction for each test
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_tenant_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session):
    user = User(username="admin_test", hashed_password=get_password_hash("pass"), role=RoleEnum.ADMIN)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def tech_user(db_session):
    user = User(username="tech_test", hashed_password=get_password_hash("pass"), role=RoleEnum.TECHNICAL)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def comm_user(db_session):
    user = User(username="comm_test", hashed_password=get_password_hash("pass"), role=RoleEnum.COMMERCIAL)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_client(client, admin_user):
    session_id = create_session(admin_user.id)
    client.cookies.set("session_id", session_id)
    return client

@pytest.fixture
def tech_client(client, tech_user):
    session_id = create_session(tech_user.id)
    client.cookies.set("session_id", session_id)
    return client

@pytest.fixture
def comm_client(client, comm_user):
    session_id = create_session(comm_user.id)
    client.cookies.set("session_id", session_id)
    return client
