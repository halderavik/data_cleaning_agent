import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import Base, engine, get_db
from app.models.rule import Rule
from app.core.auth import get_current_user

# Test data
TEST_RULE = {
    "name": "Test Rule",
    "description": "A test rule",
    "category": "test",
    "severity": "high",
    "conditions": [
        {
            "field": "status",
            "operator": "equals",
            "value": "active"
        }
    ],
    "actions": [
        {
            "type": "flag",
            "value": "needs_review"
        }
    ],
    "is_active": True
}

# Mock authentication
def mock_get_current_user():
    return "test_user"

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture
def client():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    # Create test database session
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def test_create_rule(client, db_session):
    """Test creating a new rule."""
    response = client.post("/api/rules/", json=TEST_RULE)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_RULE["name"]
    assert data["category"] == TEST_RULE["category"]
    assert len(data["conditions"]) == 1
    assert len(data["actions"]) == 1

def test_create_invalid_rule(client):
    """Test creating an invalid rule."""
    invalid_rule = TEST_RULE.copy()
    invalid_rule["conditions"] = []  # Empty conditions should be invalid
    response = client.post("/api/rules/", json=invalid_rule)
    assert response.status_code == 400

def test_list_rules(client, db_session):
    """Test listing rules."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.get("/api/rules/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == TEST_RULE["name"]

def test_get_rule(client, db_session):
    """Test getting a specific rule."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.get("/api/rules/test-id")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_RULE["name"]

def test_get_nonexistent_rule(client):
    """Test getting a nonexistent rule."""
    response = client.get("/api/rules/nonexistent")
    assert response.status_code == 404

def test_update_rule(client, db_session):
    """Test updating a rule."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    # Update the rule
    updated_rule = TEST_RULE.copy()
    updated_rule["name"] = "Updated Rule"
    response = client.put("/api/rules/test-id", json=updated_rule)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Rule"

def test_delete_rule(client, db_session):
    """Test deleting a rule."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.delete("/api/rules/test-id")
    assert response.status_code == 200

    # Verify rule is deleted
    response = client.get("/api/rules/test-id")
    assert response.status_code == 404

def test_validate_rule(client, db_session):
    """Test validating a rule."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.post("/api/rules/test-id/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True

def test_test_rule(client, db_session):
    """Test testing a rule against sample data."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.post("/api/rules/test-id/test?sample_size=50")
    assert response.status_code == 200
    data = response.json()
    assert "execution_time" in data
    assert "matches" in data
    assert "total_rows" in data

def test_list_rule_versions(client, db_session):
    """Test listing rule versions."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    response = client.get("/api/rules/test-id/versions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Initial version

def test_compare_versions(client, db_session):
    """Test comparing rule versions."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    # Update the rule to create a new version
    updated_rule = TEST_RULE.copy()
    updated_rule["name"] = "Updated Rule"
    client.put("/api/rules/test-id", json=updated_rule)

    response = client.get("/api/rules/test-id/compare?version1=1&version2=2")
    assert response.status_code == 200
    data = response.json()
    assert "changes" in data
    assert len(data["changes"]["modified"]) > 0

def test_rollback_rule(client, db_session):
    """Test rolling back a rule to a previous version."""
    # Create a test rule
    rule = Rule(**TEST_RULE, id="test-id", created_by="test_user", updated_by="test_user")
    db_session.add(rule)
    db_session.commit()

    # Update the rule
    updated_rule = TEST_RULE.copy()
    updated_rule["name"] = "Updated Rule"
    client.put("/api/rules/test-id", json=updated_rule)

    # Rollback to version 1
    response = client.post("/api/rules/test-id/rollback/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_RULE["name"] 