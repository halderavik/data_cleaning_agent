import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from services.spss_processor import SPSSProcessor
import tempfile
import os

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    data = {
        'email': ['test@example.com', 'invalid-email', 'user@domain.com'],
        'ip_address': ['192.168.1.1', 'invalid-ip', '10.0.0.1'],
        'date': ['2024-01-01', 'invalid-date', '2024-02-01'],
        'numeric': [1, 2, 3, 4, 5, 1000],  # Includes outlier
        'text': ['a', 'b', 'c', None, 'd']
    }
    return pd.DataFrame(data)

@pytest.fixture
def spss_processor():
    """Create SPSSProcessor instance for testing."""
    return SPSSProcessor()

def test_detect_data_type(spss_processor, sample_data):
    """Test data type detection."""
    # Test email detection
    assert spss_processor._detect_data_type(sample_data['email']) == 'email'
    
    # Test IP address detection
    assert spss_processor._detect_data_type(sample_data['ip_address']) == 'ip_address'
    
    # Test date detection
    assert spss_processor._detect_data_type(sample_data['date']) == 'date'
    
    # Test numeric detection
    assert spss_processor._detect_data_type(sample_data['numeric']) == 'numeric'
    
    # Test text detection
    assert spss_processor._detect_data_type(sample_data['text']) == 'text'

def test_validate_emails(spss_processor, sample_data):
    """Test email validation."""
    validation = spss_processor._validate_emails(sample_data['email'])
    
    assert validation['valid_count'] == 2
    assert validation['invalid_count'] == 1
    assert 'invalid-email' in validation['invalid_values']

def test_validate_ip_addresses(spss_processor, sample_data):
    """Test IP address validation."""
    validation = spss_processor._validate_ip_addresses(sample_data['ip_address'])
    
    assert validation['valid_count'] == 2
    assert validation['invalid_count'] == 1
    assert 'invalid-ip' in validation['invalid_values']

def test_validate_dates(spss_processor, sample_data):
    """Test date validation."""
    validation = spss_processor._validate_dates(sample_data['date'])
    
    assert validation['valid_count'] == 2
    assert validation['invalid_count'] == 1
    assert 'invalid-date' in validation['invalid_values']

def test_analyze_distribution(spss_processor, sample_data):
    """Test distribution analysis."""
    # Test numeric distribution
    numeric_dist = spss_processor._analyze_distribution(sample_data['numeric'])
    assert 'mean' in numeric_dist
    assert 'median' in numeric_dist
    assert 'std' in numeric_dist
    assert numeric_dist['min'] == 1
    assert numeric_dist['max'] == 1000
    
    # Test categorical distribution
    text_dist = spss_processor._analyze_distribution(sample_data['text'])
    assert 'unique_values' in text_dist
    assert 'most_common' in text_dist
    assert 'least_common' in text_dist

def test_calculate_completeness(spss_processor, sample_data):
    """Test completeness calculation."""
    spss_processor.data = sample_data
    completeness = spss_processor._calculate_completeness()
    
    # One null value in 'text' column out of 15 total cells
    expected_completeness = 1 - (1 / 15)
    assert abs(completeness - expected_completeness) < 0.001

def test_calculate_consistency(spss_processor, sample_data):
    """Test consistency calculation."""
    spss_processor.data = sample_data
    spss_processor.schema = {
        'numeric': {'type': 'numeric'},
        'date': {'type': 'date'}
    }
    
    consistency = spss_processor._calculate_consistency()
    assert 0 <= consistency <= 1

def test_calculate_validity(spss_processor, sample_data):
    """Test validity calculation."""
    spss_processor.data = sample_data
    spss_processor.schema = {
        'email': {'type': 'email', 'validation': {'invalid_count': 1}},
        'ip_address': {'type': 'ip_address', 'validation': {'invalid_count': 1}},
        'date': {'type': 'date', 'validation': {'invalid_count': 1}}
    }
    
    validity = spss_processor._calculate_validity()
    assert 0 <= validity <= 1

def test_analyze_data_quality(spss_processor, sample_data):
    """Test overall data quality analysis."""
    spss_processor.data = sample_data
    spss_processor.schema = {
        'email': {'type': 'email', 'validation': {'invalid_count': 1}},
        'ip_address': {'type': 'ip_address', 'validation': {'invalid_count': 1}},
        'date': {'type': 'date', 'validation': {'invalid_count': 1}},
        'numeric': {'type': 'numeric'},
        'text': {'type': 'text'}
    }
    
    quality = spss_processor.analyze_data_quality()
    assert 'completeness' in quality
    assert 'consistency' in quality
    assert 'validity' in quality
    assert 'overall_score' in quality
    assert all(0 <= score <= 1 for score in quality.values())

def test_detect_schema(spss_processor, sample_data):
    """Test schema detection."""
    spss_processor.data = sample_data
    schema = spss_processor.detect_schema()
    
    assert 'email' in schema
    assert 'ip_address' in schema
    assert 'date' in schema
    assert 'numeric' in schema
    assert 'text' in schema
    
    # Check schema structure
    for column in schema:
        assert 'type' in schema[column]
        assert 'null_count' in schema[column]
        assert 'unique_count' in schema[column]
        assert 'distribution' in schema[column]

def test_analyze_structure_without_data(spss_processor):
    """Test structure analysis without loaded data."""
    with pytest.raises(ValueError):
        spss_processor.analyze_structure() 