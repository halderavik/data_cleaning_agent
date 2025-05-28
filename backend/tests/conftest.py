import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.database.base import Base
from main import app
from backend.models import User
from backend.security import get_password_hash
from backend.security import create_access_token

# Test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/survey_cleaning_test"

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db(engine):
    """Create a test database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        name="Admin User",
        password=get_password_hash("adminpassword"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def analyst_user(db):
    """Create an analyst user."""
    user = User(
        email="analyst@example.com",
        name="Analyst User",
        password=get_password_hash("analystpassword"),
        role="analyst"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token(admin_user):
    """Create an admin access token."""
    return create_access_token(data={"sub": admin_user.email})

@pytest.fixture(scope="function")
def analyst_token(analyst_user):
    """Create an analyst access token."""
    return create_access_token(data={"sub": analyst_user.email}) 