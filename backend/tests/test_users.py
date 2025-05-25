import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from main import app
from models import User
from security import get_password_hash, create_access_token

client = TestClient(app)

@pytest.fixture
def admin_user(db: Session):
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

@pytest.fixture
def analyst_user(db: Session):
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

@pytest.fixture
def admin_token(admin_user):
    """Create an admin access token."""
    return create_access_token(data={"sub": admin_user.email})

@pytest.fixture
def analyst_token(analyst_user):
    """Create an analyst access token."""
    return create_access_token(data={"sub": analyst_user.email})

def test_create_user_as_admin(client, db, admin_token):
    """Test creating a user as admin."""
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "new@example.com",
            "name": "New User",
            "password": "newpassword",
            "role": "analyst"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"
    assert data["role"] == "analyst"
    
    # Verify user was created
    user = db.query(User).filter(User.email == "new@example.com").first()
    assert user is not None
    assert user.name == "New User"
    assert user.role == "analyst"

def test_create_user_as_analyst(client, db, analyst_token):
    """Test creating a user as analyst (should fail)."""
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "email": "new@example.com",
            "name": "New User",
            "password": "newpassword",
            "role": "analyst"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_get_current_user(client, db, analyst_token, analyst_user):
    """Test getting current user information."""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == analyst_user.email
    assert data["name"] == analyst_user.name
    assert data["role"] == analyst_user.role

def test_update_current_user(client, db, analyst_token, analyst_user):
    """Test updating current user information."""
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Updated Name"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    
    # Verify user was updated
    user = db.query(User).filter(User.id == analyst_user.id).first()
    assert user.name == "Updated Name"

def test_list_users_as_admin(client, db, admin_token, admin_user, analyst_user):
    """Test listing users as admin."""
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # At least admin and analyst users
    emails = [user["email"] for user in data]
    assert admin_user.email in emails
    assert analyst_user.email in emails

def test_list_users_as_analyst(client, db, analyst_token):
    """Test listing users as analyst (should fail)."""
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_get_user_by_id_as_admin(client, db, admin_token, analyst_user):
    """Test getting user by ID as admin."""
    response = client.get(
        f"/users/{analyst_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == analyst_user.email
    assert data["name"] == analyst_user.name
    assert data["role"] == analyst_user.role

def test_get_user_by_id_as_analyst(client, db, analyst_token, admin_user):
    """Test getting user by ID as analyst (should fail)."""
    response = client.get(
        f"/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_update_user_as_admin(client, db, admin_token, analyst_user):
    """Test updating user as admin."""
    response = client.put(
        f"/users/{analyst_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated by Admin",
            "role": "senior_analyst"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated by Admin"
    assert data["role"] == "senior_analyst"
    
    # Verify user was updated
    user = db.query(User).filter(User.id == analyst_user.id).first()
    assert user.name == "Updated by Admin"
    assert user.role == "senior_analyst"

def test_update_user_as_analyst(client, db, analyst_token, admin_user):
    """Test updating user as analyst (should fail)."""
    response = client.put(
        f"/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "name": "Updated by Analyst"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions" 