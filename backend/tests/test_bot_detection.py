import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.core.bot_detection import BotDetector

@pytest.fixture
def sample_data():
    # Create sample survey data
    data = {
        'text_response': [
            'This is a detailed response with multiple words.',
            'Too short',
            'Another detailed response about the topic.',
            'Very brief',
            'A comprehensive analysis of the subject matter.'
        ],
        'timestamp': [
            datetime.now() - timedelta(minutes=i)
            for i in range(5)
        ],
        'ip_address': [
            '192.168.1.1',
            '192.168.1.2',
            '192.168.1.1',  # Duplicate IP
            '192.168.1.3',
            '192.168.1.4'
        ]
    }
    return pd.DataFrame(data)

@pytest.fixture
def detector():
    return BotDetector()

def test_feature_extraction(detector, sample_data):
    features = detector.extract_features(
        sample_data,
        text_columns=['text_response'],
        time_column='timestamp',
        ip_column='ip_address'
    )
    
    assert isinstance(features, np.ndarray)
    assert features.shape[0] == len(sample_data)
    assert features.shape[1] > 0

def test_bot_detection_training(detector, sample_data):
    # Train with known bots
    known_bots = [1, 3]  # Indices of known bot responses
    detector.train(
        sample_data,
        text_columns=['text_response'],
        known_bots=known_bots,
        time_column='timestamp',
        ip_column='ip_address'
    )
    
    assert detector.is_trained

def test_bot_detection(detector, sample_data):
    # Train first
    known_bots = [1, 3]
    detector.train(
        sample_data,
        text_columns=['text_response'],
        known_bots=known_bots,
        time_column='timestamp',
        ip_column='ip_address'
    )
    
    # Test detection
    results = detector.detect_bots(
        sample_data,
        text_columns=['text_response'],
        time_column='timestamp',
        ip_column='ip_address'
    )
    
    assert 'total_responses' in results
    assert 'potential_bots' in results
    assert 'bot_details' in results
    assert 'severity' in results

def test_pattern_analysis(detector, sample_data):
    results = detector.analyze_patterns(
        sample_data,
        text_columns=['text_response'],
        time_column='timestamp'
    )
    
    assert 'total_responses' in results
    assert 'patterns_found' in results
    assert 'pattern_details' in results
    assert 'severity' in results

def test_identical_responses(detector):
    # Create data with identical responses
    data = pd.DataFrame({
        'text_response': [
            'Same response',
            'Same response',
            'Same response',
            'Different response',
            'Another different response'
        ],
        'timestamp': [
            datetime.now() - timedelta(minutes=i)
            for i in range(5)
        ]
    })
    
    results = detector.analyze_patterns(
        data,
        text_columns=['text_response'],
        time_column='timestamp'
    )
    
    assert results['patterns_found'] > 0
    assert any(p['type'] == 'identical_responses' for p in results['pattern_details'])

def test_fast_responses(detector):
    # Create data with impossibly fast responses
    now = datetime.now()
    data = pd.DataFrame({
        'text_response': ['Response'] * 5,
        'timestamp': [
            now,
            now + timedelta(seconds=0.5),  # Too fast
            now + timedelta(seconds=1.5),
            now + timedelta(seconds=0.3),  # Too fast
            now + timedelta(seconds=2.0)
        ]
    })
    
    results = detector.analyze_patterns(
        data,
        text_columns=['text_response'],
        time_column='timestamp'
    )
    
    assert results['patterns_found'] > 0
    assert any(p['type'] == 'fast_responses' for p in results['pattern_details'])

def test_keyboard_patterns(detector):
    # Create data with keyboard patterns
    data = pd.DataFrame({
        'text_response': [
            'Normal response',
            'qwerty asdfgh',
            'zxcvbn asdfgh',
            'Another normal response',
            'qwerty zxcvbn'
        ],
        'timestamp': [
            datetime.now() - timedelta(minutes=i)
            for i in range(5)
        ]
    })
    
    results = detector.analyze_patterns(
        data,
        text_columns=['text_response'],
        time_column='timestamp'
    )
    
    assert results['patterns_found'] > 0
    assert any(p['type'] == 'keyboard_patterns' for p in results['pattern_details']) 