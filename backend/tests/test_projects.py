import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from main import app
from models import Project

client = TestClient(app)

def test_create_project(client, db, analyst_token):
    """Test creating a new project."""
    response = client.post(
        "/projects/",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Test Project",
            "description": "A test project",
            "status": "active"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert data["status"] == "active"
    
    # Verify project was created
    project = db.query(Project).filter(Project.name == "Test Project").first()
    assert project is not None
    assert project.description == "A test project"
    assert project.status == "active"

def test_create_project_invalid_status(client, db, analyst_token):
    """Test creating a project with invalid status."""
    response = client.post(
        "/projects/",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Test Project",
            "description": "A test project",
            "status": "invalid_status"
        }
    )
    assert response.status_code == 422

def test_list_projects(client, db, analyst_token):
    """Test listing projects."""
    # Create test projects
    project1 = Project(
        name="Project 1",
        description="First project",
        status="active",
        owner_id=db.query(User).filter(User.email == "analyst@example.com").first().id
    )
    project2 = Project(
        name="Project 2",
        description="Second project",
        status="completed",
        owner_id=db.query(User).filter(User.email == "analyst@example.com").first().id
    )
    db.add_all([project1, project2])
    db.commit()
    
    response = client.get(
        "/projects/",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    project_names = [p["name"] for p in data]
    assert "Project 1" in project_names
    assert "Project 2" in project_names

def test_get_project(client, db, analyst_token):
    """Test getting a specific project."""
    # Create test project
    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
        owner_id=db.query(User).filter(User.email == "analyst@example.com").first().id
    )
    db.add(project)
    db.commit()
    
    response = client.get(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert data["status"] == "active"

def test_get_nonexistent_project(client, db, analyst_token):
    """Test getting a nonexistent project."""
    response = client.get(
        "/projects/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_update_project(client, db, analyst_token):
    """Test updating a project."""
    # Create test project
    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
        owner_id=db.query(User).filter(User.email == "analyst@example.com").first().id
    )
    db.add(project)
    db.commit()
    
    response = client.put(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Updated Project",
            "description": "Updated description",
            "status": "completed"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated description"
    assert data["status"] == "completed"
    
    # Verify project was updated
    updated_project = db.query(Project).filter(Project.id == project.id).first()
    assert updated_project.name == "Updated Project"
    assert updated_project.description == "Updated description"
    assert updated_project.status == "completed"

def test_update_project_unauthorized(client, db, analyst_token, admin_user):
    """Test updating another user's project."""
    # Create test project owned by admin
    project = Project(
        name="Admin Project",
        description="Admin's project",
        status="active",
        owner_id=admin_user.id
    )
    db.add(project)
    db.commit()
    
    response = client.put(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Updated Project"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_delete_project(client, db, analyst_token):
    """Test deleting a project."""
    # Create test project
    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
        owner_id=db.query(User).filter(User.email == "analyst@example.com").first().id
    )
    db.add(project)
    db.commit()
    
    response = client.delete(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 204
    
    # Verify project was deleted
    deleted_project = db.query(Project).filter(Project.id == project.id).first()
    assert deleted_project is None

def test_delete_project_unauthorized(client, db, analyst_token, admin_user):
    """Test deleting another user's project."""
    # Create test project owned by admin
    project = Project(
        name="Admin Project",
        description="Admin's project",
        status="active",
        owner_id=admin_user.id
    )
    db.add(project)
    db.commit()
    
    response = client.delete(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions" 