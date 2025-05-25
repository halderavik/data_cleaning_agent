import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tempfile

from ..main import app
from ..database import get_db
from ..models import User, Project, DataFile, CleaningCheck, CleaningResult
from ..auth import create_access_token

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create a test database session."""
    from ..database import Base, engine
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def test_project(test_db, test_user):
    """Create a test project."""
    project = Project(
        name="Test Project",
        user_id=test_user.id
    )
    test_db.add(project)
    test_db.commit()
    return project

@pytest.fixture
def test_data_file(test_db, test_project):
    """Create a test data file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        df = pd.DataFrame({
            'numeric_col': [1, 2, 3, 100, 5, 6, 7, 8, 9, 10],
            'categorical_col': ['A', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'A', 'B'],
            'text_col': [
                'Good response',
                'Bad response',
                'Test',
                'asdf',
                'Nice answer',
                'qwer',
                'Detailed response',
                '123',
                'Helpful comment',
                'none'
            ]
        })
        df.to_csv(temp_file.name, index=False)
        
        data_file = DataFile(
            project_id=test_project.id,
            original_filename="test.csv",
            file_path=temp_file.name,
            file_size=os.path.getsize(temp_file.name),
            file_type="csv",
            upload_status="completed"
        )
        test_db.add(data_file)
        test_db.commit()
        
        return data_file

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

def test_clean_data_file(test_db, test_data_file, auth_headers):
    """Test cleaning a data file."""
    response = client.post(
        f"/cleaning/{test_data_file.id}/clean",
        headers=auth_headers,
        json={
            "config": {
                "required_fields": ["numeric_col", "categorical_col"],
                "expected_types": {
                    "numeric_col": "int64",
                    "categorical_col": "object"
                }
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data_file_id"] == str(test_data_file.id)
    assert "results" in data
    
    # Verify cleaning results were saved
    results = test_db.query(CleaningResult).filter(
        CleaningResult.data_file_id == test_data_file.id
    ).all()
    assert len(results) > 0

def test_get_cleaning_results(test_db, test_data_file, auth_headers):
    """Test getting cleaning results."""
    # First run cleaning
    client.post(
        f"/cleaning/{test_data_file.id}/clean",
        headers=auth_headers,
        json={}
    )
    
    # Then get results
    response = client.get(
        f"/cleaning/{test_data_file.id}/results",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data_file_id"] == str(test_data_file.id)
    assert "results" in data
    assert len(data["results"]) > 0

def test_clean_nonexistent_file(test_db, auth_headers):
    """Test cleaning a nonexistent file."""
    response = client.post(
        "/cleaning/nonexistent-id/clean",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Data file not found"

def test_get_results_nonexistent_file(test_db, auth_headers):
    """Test getting results for a nonexistent file."""
    response = client.get(
        "/cleaning/nonexistent-id/results",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Data file not found"

def test_clean_file_unauthorized(test_db, test_data_file):
    """Test cleaning a file without authentication."""
    response = client.post(
        f"/cleaning/{test_data_file.id}/clean",
        json={}
    )
    
    assert response.status_code == 401

def test_get_results_unauthorized(test_db, test_data_file):
    """Test getting results without authentication."""
    response = client.get(
        f"/cleaning/{test_data_file.id}/results"
    )
    
    assert response.status_code == 401 