import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from models import Base, User, Project, DataFile, CleaningCheck, CleaningResult

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
def session(engine):
    """Create a test database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_create_user(session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        name="Test User",
        role="analyst"
    )
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "analyst"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)

def test_create_project(session):
    """Test creating a project."""
    user = User(
        email="project_owner@example.com",
        name="Project Owner"
    )
    session.add(user)
    session.commit()
    
    project = Project(
        name="Test Project",
        description="A test project",
        owner_id=user.id
    )
    session.add(project)
    session.commit()
    
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.owner_id == user.id
    assert project.status == "draft"
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)

def test_create_data_file(session):
    """Test creating a data file."""
    user = User(email="file_owner@example.com", name="File Owner")
    session.add(user)
    session.commit()
    
    project = Project(name="File Project", owner_id=user.id)
    session.add(project)
    session.commit()
    
    data_file = DataFile(
        project_id=project.id,
        original_filename="test.sav",
        file_size=1024,
        file_type="spss"
    )
    session.add(data_file)
    session.commit()
    
    assert data_file.id is not None
    assert data_file.project_id == project.id
    assert data_file.original_filename == "test.sav"
    assert data_file.file_size == 1024
    assert data_file.file_type == "spss"
    assert data_file.upload_status == "pending"
    assert isinstance(data_file.created_at, datetime)

def test_create_cleaning_check(session):
    """Test creating a cleaning check."""
    check = CleaningCheck(
        name="Duplicate Check",
        description="Check for duplicate responses",
        category="duplicates",
        is_standard=True,
        check_function="def check_duplicates(data): pass"
    )
    session.add(check)
    session.commit()
    
    assert check.id is not None
    assert check.name == "Duplicate Check"
    assert check.description == "Check for duplicate responses"
    assert check.category == "duplicates"
    assert check.is_standard is True
    assert check.check_function == "def check_duplicates(data): pass"
    assert isinstance(check.created_at, datetime)

def test_create_cleaning_result(session):
    """Test creating a cleaning result."""
    user = User(email="result_owner@example.com", name="Result Owner")
    session.add(user)
    session.commit()
    
    project = Project(name="Result Project", owner_id=user.id)
    session.add(project)
    session.commit()
    
    data_file = DataFile(project_id=project.id, original_filename="test.sav")
    session.add(data_file)
    session.commit()
    
    check = CleaningCheck(name="Test Check", category="test")
    session.add(check)
    session.commit()
    
    result = CleaningResult(
        project_id=project.id,
        data_file_id=data_file.id,
        check_id=check.id,
        status="completed",
        issues_found=5,
        details={"issues": ["issue1", "issue2"]}
    )
    session.add(result)
    session.commit()
    
    assert result.id is not None
    assert result.project_id == project.id
    assert result.data_file_id == data_file.id
    assert result.check_id == check.id
    assert result.status == "completed"
    assert result.issues_found == 5
    assert result.details == {"issues": ["issue1", "issue2"]}
    assert isinstance(result.created_at, datetime)
    assert result.completed_at is None 