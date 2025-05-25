import pytest
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.query_optimizer import QueryOptimizer

# Test database setup
TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def query_optimizer(db_session):
    """Create a QueryOptimizer instance."""
    return QueryOptimizer(db_session)

@pytest.fixture
def sample_tables(db_session):
    """Create sample tables for testing."""
    # Create test tables
    db_session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    db_session.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            amount DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Insert test data
    db_session.execute(text("""
        INSERT INTO users (name, email) VALUES
        ('John Doe', 'john@example.com'),
        ('Jane Smith', 'jane@example.com')
    """))
    
    db_session.execute(text("""
        INSERT INTO orders (user_id, amount) VALUES
        (1, 100.50),
        (1, 200.75),
        (2, 150.25)
    """))
    
    db_session.commit()

def test_analyze_query(query_optimizer, sample_tables):
    """Test query analysis functionality."""
    query = "SELECT * FROM users WHERE name = 'John Doe'"
    analysis = query_optimizer.analyze_query(query)
    
    assert 'execution_plan' in analysis
    assert 'statistics' in analysis
    assert 'timestamp' in analysis
    assert 'query_hash' in analysis
    assert isinstance(analysis['timestamp'], str)
    assert isinstance(analysis['query_hash'], str)

def test_optimize_query(query_optimizer, sample_tables):
    """Test query optimization functionality."""
    query = "SELECT * FROM users WHERE name = 'John Doe'"
    optimization = query_optimizer.optimize_query(query)
    
    assert 'original_query' in optimization
    assert 'optimized_query' in optimization
    assert 'suggestions' in optimization
    assert 'improvement' in optimization
    assert 'timestamp' in optimization
    assert isinstance(optimization['suggestions'], list)
    assert isinstance(optimization['improvement'], dict)

def test_get_query_performance(query_optimizer, sample_tables):
    """Test query performance tracking."""
    query = "SELECT * FROM users WHERE name = 'John Doe'"
    analysis = query_optimizer.analyze_query(query)
    performance = query_optimizer.get_query_performance(analysis['query_hash'])
    
    assert 'execution_time' in performance
    assert 'plan' in performance
    assert 'timestamp' in performance
    assert isinstance(performance['execution_time'], float)

def test_sequential_scan_detection(query_optimizer, sample_tables):
    """Test detection of sequential scans."""
    query = "SELECT * FROM users"
    analysis = query_optimizer.analyze_query(query)
    suggestions = query_optimizer._generate_optimization_suggestions(analysis)
    
    assert any(s['type'] == 'index' for s in suggestions)

def test_inefficient_join_detection(query_optimizer, sample_tables):
    """Test detection of inefficient joins."""
    query = """
        SELECT u.name, o.amount 
        FROM users u 
        JOIN orders o ON u.id = o.user_id
    """
    analysis = query_optimizer.analyze_query(query)
    suggestions = query_optimizer._generate_optimization_suggestions(analysis)
    
    assert any(s['type'] == 'join' for s in suggestions)

def test_large_result_set_detection(query_optimizer, sample_tables):
    """Test detection of large result sets."""
    # Insert many records to trigger large result set detection
    for i in range(10000):
        query_optimizer.db.execute(text(
            f"INSERT INTO users (name, email) VALUES ('User {i}', 'user{i}@example.com')"
        ))
    query_optimizer.db.commit()
    
    query = "SELECT * FROM users"
    analysis = query_optimizer.analyze_query(query)
    suggestions = query_optimizer._generate_optimization_suggestions(analysis)
    
    assert any(s['type'] == 'pagination' for s in suggestions)

def test_query_hashing(query_optimizer):
    """Test query hashing functionality."""
    query1 = "SELECT * FROM users WHERE name = 'John'"
    query2 = "SELECT * FROM users WHERE name = 'John'"
    query3 = "SELECT * FROM users WHERE name = 'Jane'"
    
    hash1 = query_optimizer._hash_query(query1)
    hash2 = query_optimizer._hash_query(query2)
    hash3 = query_optimizer._hash_query(query3)
    
    assert hash1 == hash2  # Same query should have same hash
    assert hash1 != hash3  # Different queries should have different hashes

def test_error_handling(query_optimizer):
    """Test error handling for invalid queries."""
    invalid_query = "SELECT * FROM non_existent_table"
    
    with pytest.raises(Exception):
        query_optimizer.analyze_query(invalid_query)
    
    with pytest.raises(Exception):
        query_optimizer.optimize_query(invalid_query) 