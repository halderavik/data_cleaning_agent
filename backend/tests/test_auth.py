import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from main import app
from backend.models import User
from backend.security import get_password_hash

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        password=get_password_hash("testpassword"),
        role="analyst"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_register_user(client, db):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        params={
            "email": "new@example.com",
            "password": "newpassword",
            "name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify user was created
    user = db.query(User).filter(User.email == "new@example.com").first()
    assert user is not None
    assert user.name == "New User"
    assert user.role == "analyst"

def test_register_existing_user(client, db, analyst_user):
    """Test registering with existing email."""
    response = client.post(
        "/auth/register",
        params={
            "email": analyst_user.email,
            "password": "newpassword",
            "name": "New User"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, db, analyst_user):
    """Test successful login."""
    response = client.post(
        "/auth/token",
        data={
            "username": analyst_user.email,
            "password": "analystpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db, analyst_user):
    """Test login with wrong password."""
    response = client.post(
        "/auth/token",
        data={
            "username": analyst_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client, db):
    """Test login with nonexistent user."""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_protected_route_with_token(client, db, analyst_user, analyst_token):
    """Test accessing protected route with valid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == analyst_user.email
    assert data["name"] == analyst_user.name

def test_protected_route_without_token(client):
    """Test accessing protected route without token."""
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_invalid_token(client):
    """Test accessing protected route with invalid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials" 