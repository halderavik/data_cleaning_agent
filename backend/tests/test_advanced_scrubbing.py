import pytest
import pandas as pd
import numpy as np
from app.core.advanced_scrubbing import AdvancedScrubbing

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'text_response': [
            'This is a detailed response with multiple words.',
            'Too short',
            'Another detailed response about the topic.',
            'Very brief',
            'A comprehensive analysis of the subject matter.'
        ],
        'closed_response': ['Yes', 'No', 'Yes', 'Maybe', 'Yes'],
        'open_response': [
            'I agree with the statement completely.',
            'I disagree with everything.',
            'I strongly agree with the proposal.',
            'Not sure about this.',
            'I fully support this idea.'
        ],
        'brand_name': ['Nike', 'Adidas', 'Invalid Brand', 'Puma', 'Nike'],
        'age': [25, 45, 15, 30, 35],
        'gender': ['M', 'F', 'M', 'F', 'M'],
        'topic_familiarity': [4, 3, 1, 5, 4],
        'knowledge_q1': [True, False, False, True, True],
        'knowledge_q2': [True, True, False, True, True],
        'sentiment1': ['I love this product!', 'It is okay', 'Hate it', 'Great experience', 'Not bad'],
        'sentiment2': ['Excellent service', 'Average', 'Terrible', 'Amazing', 'Good']
    })

@pytest.fixture
def scrubbing():
    return AdvancedScrubbing()

def test_check_response_brevity(scrubbing, sample_data):
    result = scrubbing.check_response_brevity(sample_data, 'text_response', min_words=3)
    assert result['total_responses'] == 5
    assert result['brief_responses'] == 2
    assert len(result['brief_response_indices']) == 2
    assert result['severity'] == 'high'

def test_check_closed_open_consistency(scrubbing, sample_data):
    expected_keywords = {
        'yes': ['agree', 'support', 'like'],
        'no': ['disagree', 'against', 'dislike'],
        'maybe': ['unsure', 'not sure', 'maybe']
    }
    result = scrubbing.check_closed_open_consistency(
        sample_data, 'closed_response', 'open_response', expected_keywords
    )
    assert result['total_responses'] == 5
    assert result['inconsistent_responses'] > 0
    assert 'inconsistency_details' in result

def test_check_plagiarism(scrubbing, sample_data):
    result = scrubbing.check_plagiarism(sample_data, 'text_response', similarity_threshold=0.8)
    assert result['total_responses'] == 5
    assert 'similar_pairs' in result
    assert 'similarity_details' in result

def test_check_brand_recall(scrubbing, sample_data):
    expected_brands = ['Nike', 'Adidas', 'Puma']
    result = scrubbing.check_brand_recall(
        sample_data, 'brand_name', expected_brands, ['age', 'gender']
    )
    assert result['total_responses'] == 5
    assert result['invalid_brands'] == 1
    assert len(result['invalid_brand_details']) == 1

def test_check_target_audience(scrubbing, sample_data):
    demographic_columns = {
        'age': list(range(18, 65)),
        'gender': ['M', 'F']
    }
    target_criteria = {
        'min_age': 18,
        'max_age': 65,
        'valid_genders': ['M', 'F']
    }
    result = scrubbing.check_target_audience(
        sample_data, demographic_columns, target_criteria
    )
    assert result['total_responses'] == 5
    assert result['ineligible_respondents'] == 1
    assert len(result['ineligibility_details']) == 1

def test_check_topic_awareness(scrubbing, sample_data):
    result = scrubbing.check_topic_awareness(
        sample_data,
        'topic_familiarity',
        ['knowledge_q1', 'knowledge_q2'],
        min_correct_answers=1
    )
    assert result['total_responses'] == 5
    assert 'low_awareness_count' in result
    assert 'low_awareness_details' in result

def test_check_sentiment_consistency(scrubbing, sample_data):
    result = scrubbing.check_sentiment_consistency(
        sample_data,
        ['sentiment1', 'sentiment2'],
        threshold=0.3
    )
    assert result['total_responses'] == 5
    assert 'inconsistent_sentiments' in result
    assert 'inconsistency_details' in result 