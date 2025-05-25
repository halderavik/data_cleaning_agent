import pytest
from app.core.nlp_engine import NLEngine

@pytest.fixture
def nlp_engine():
    return NLEngine()

def test_sentiment_analysis(nlp_engine):
    texts = [
        'I love this product! It is amazing.',
        'This is terrible, I hate it.',
        'The product is okay, nothing special.'
    ]
    
    results = nlp_engine.analyze_sentiment(texts)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'average_sentiment' in results
    assert 'sentiment_distribution' in results
    assert len(results['results']) == len(texts)

def test_detailed_sentiment_analysis(nlp_engine):
    text = 'I love this product! It is amazing.'
    
    results = nlp_engine.analyze_sentiment(text, detailed=True)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert results['results'][0]['detailed_analysis'] is not None
    assert 'polarity' in results['results'][0]['detailed_analysis']
    assert 'subjectivity' in results['results'][0]['detailed_analysis']

def test_zero_shot_classification(nlp_engine):
    texts = [
        'The product is too expensive.',
        'I love the customer service.',
        'The quality is excellent.'
    ]
    candidate_labels = ['price', 'service', 'quality']
    
    results = nlp_engine.zero_shot_classify(texts, candidate_labels)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'label_distribution' in results
    assert len(results['results']) == len(texts)

def test_multi_label_classification(nlp_engine):
    texts = [
        'The product is expensive but the quality is excellent.',
        'Great service and good quality.',
        'Poor service and high price.'
    ]
    candidate_labels = ['price', 'service', 'quality']
    
    results = nlp_engine.zero_shot_classify(texts, candidate_labels, multi_label=True)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert len(results['results'][0]['labels']) > 1

def test_entity_extraction(nlp_engine):
    texts = [
        'I bought a product for $99.99 on 12/25/2023.',
        'The service was excellent at 2:30 PM.',
        'I need help with my order.'
    ]
    
    results = nlp_engine.extract_entities(texts)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'entity_statistics' in results
    assert len(results['results']) == len(texts)

def test_custom_entity_patterns(nlp_engine):
    texts = [
        'I bought a product for $99.99 on 12/25/2023.',
        'The service was excellent at 2:30 PM.',
        'I need help with my order.'
    ]
    custom_patterns = {
        'currency': r'\$\d+(?:\.\d{2})?',
        'time': r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?'
    }
    
    results = nlp_engine.extract_entities(texts, custom_patterns)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'entity_statistics' in results
    assert 'custom' in results['entity_statistics']
    assert 'currency' in results['entity_statistics']['custom']
    assert 'time' in results['entity_statistics']['custom']

def test_text_quality_analysis(nlp_engine):
    texts = [
        'This is a simple text.',
        'This is a more complex text with multiple sentences. It has more words and better structure.',
        'VERY SHORT TEXT!'
    ]
    
    results = nlp_engine.analyze_text_quality(texts)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'aggregate_metrics' in results
    assert len(results['results']) == len(texts)
    
    # Check metrics
    for result in results['results']:
        assert 'metrics' in result
        assert 'word_count' in result['metrics']
        assert 'sentence_count' in result['metrics']
        assert 'readability_score' in result['metrics']
        assert 'readability_level' in result['metrics']

def test_readability_levels(nlp_engine):
    # Test different readability levels
    texts = [
        'The cat sat on the mat.',  # Very easy
        'The quick brown fox jumps over the lazy dog.',  # Easy
        'The implementation of the algorithm requires careful consideration of edge cases.',  # Moderate
        'The quantum mechanical properties of subatomic particles exhibit wave-particle duality.',  # Difficult
        'The phenomenological hermeneutics of existential ontology necessitates a deconstruction of metaphysical presuppositions.'  # Very difficult
    ]
    
    results = nlp_engine.analyze_text_quality(texts)
    
    assert 'total_texts' in results
    assert 'results' in results
    assert 'aggregate_metrics' in results
    assert 'readability_distribution' in results['aggregate_metrics']
    
    # Check that we have different readability levels
    levels = set(r['metrics']['readability_level'] for r in results['results'])
    assert len(levels) > 1 