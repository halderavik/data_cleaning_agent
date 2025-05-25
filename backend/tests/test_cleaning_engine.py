import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cleaning_engine import CleaningEngine, CheckSeverity, CheckResult

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    data = {
        'numeric_col': [1, 2, 3, 100, 5, 6, 7, 8, 9, 10],
        'categorical_col': ['A', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'A', 'B'],
        'date_col': [
            datetime.now() - timedelta(days=i) for i in range(10)
        ],
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
        ],
        'completion_time': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        'response_time': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    }
    return pd.DataFrame(data)

@pytest.fixture
def cleaning_engine():
    """Create a CleaningEngine instance with test configuration."""
    config = {
        'required_fields': ['numeric_col', 'categorical_col'],
        'expected_types': {
            'numeric_col': 'int64',
            'categorical_col': 'object'
        },
        'consistency_rules': [
            {
                'name': 'numeric_range',
                'fields': ['numeric_col'],
                'condition': lambda df: (df['numeric_col'] >= 0) & (df['numeric_col'] <= 100)
            }
        ],
        'format_rules': {
            'text_col': r'^[A-Za-z\s]+$'
        },
        'section_fields': {
            'demographics': ['numeric_col', 'categorical_col']
        }
    }
    return CleaningEngine(config)

def test_missing_values_check(cleaning_engine, sample_data):
    """Test missing values check."""
    # Add some missing values
    sample_data.loc[0, 'numeric_col'] = np.nan
    sample_data.loc[1, 'categorical_col'] = np.nan
    
    results = cleaning_engine._check_missing_values(sample_data)
    
    assert results['issues']
    assert len(results['issues']) == 2
    assert results['summary']['total_columns_with_missing'] == 2

def test_duplicates_check(cleaning_engine, sample_data):
    """Test duplicates check."""
    # Add a duplicate row
    sample_data = pd.concat([sample_data, sample_data.iloc[0:1]])
    
    results = cleaning_engine._check_duplicates(sample_data)
    
    assert results['issues']
    assert results['summary']['total_duplicates'] == 1

def test_outliers_check(cleaning_engine, sample_data):
    """Test outliers detection."""
    results = cleaning_engine._check_outliers(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'numeric_col' for issue in results['issues'])

def test_inconsistent_categories_check(cleaning_engine, sample_data):
    """Test inconsistent categories check."""
    # Add a rare category
    sample_data.loc[0, 'categorical_col'] = 'Z'
    
    results = cleaning_engine._check_inconsistent_categories(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'categorical_col' for issue in results['issues'])

def test_date_anomalies_check(cleaning_engine, sample_data):
    """Test date anomalies check."""
    # Add a future date
    sample_data.loc[0, 'date_col'] = datetime.now() + timedelta(days=1)
    
    results = cleaning_engine._check_date_anomalies(sample_data)
    
    assert results['issues']
    assert any(issue['issue_type'] == 'future_dates' for issue in results['issues'])

def test_numeric_range_check(cleaning_engine, sample_data):
    """Test numeric range check."""
    results = cleaning_engine._check_numeric_range(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'numeric_col' for issue in results['issues'])

def test_text_quality_check(cleaning_engine, sample_data):
    """Test text quality check."""
    results = cleaning_engine._check_text_quality(sample_data)
    
    assert results['issues']
    assert any(issue['issue_type'] == 'short_texts' for issue in results['issues'])

def test_response_patterns_check(cleaning_engine, sample_data):
    """Test response patterns check."""
    # Add an alternating pattern
    sample_data['pattern_col'] = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
    
    results = cleaning_engine._check_response_patterns(sample_data)
    
    assert results['issues']
    assert any(issue['issue_type'] == 'alternating_pattern' for issue in results['issues'])

def test_completeness_check(cleaning_engine, sample_data):
    """Test completeness check."""
    # Add missing values to required fields
    sample_data.loc[0, 'numeric_col'] = np.nan
    sample_data.loc[1, 'categorical_col'] = np.nan
    
    results = cleaning_engine._check_completeness(sample_data)
    
    assert results['issues']
    assert len(results['issues']) == 2

def test_consistency_check(cleaning_engine, sample_data):
    """Test consistency check."""
    results = cleaning_engine._check_consistency(sample_data)
    
    assert results['issues']
    assert any(issue['rule'] == 'numeric_range' for issue in results['issues'])

def test_speeders_check(cleaning_engine, sample_data):
    """Test speeders check."""
    results = cleaning_engine._check_speeders(sample_data)
    
    assert results['issues']
    assert 'speeder_count' in results['issues'][0]

def test_straightliners_check(cleaning_engine, sample_data):
    """Test straightliners check."""
    # Add a straight-lining pattern
    sample_data['straight_col'] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    
    results = cleaning_engine._check_straightliners(sample_data)
    
    assert results['issues']
    assert results['summary']['straightliner_count'] > 0

def test_logical_consistency_check(cleaning_engine, sample_data):
    """Test logical consistency check."""
    results = cleaning_engine._check_logical_consistency(sample_data)
    
    assert results['issues']
    assert any(issue['rule'] == 'numeric_range' for issue in results['issues'])

def test_text_sentiment_check(cleaning_engine, sample_data):
    """Test text sentiment check."""
    results = cleaning_engine._check_text_sentiment(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'text_col' for issue in results['issues'])

def test_response_time_check(cleaning_engine, sample_data):
    """Test response time check."""
    results = cleaning_engine._check_response_time(sample_data)
    
    assert results['issues']
    assert 'long_response_count' in results['issues'][0]

def test_data_type_check(cleaning_engine, sample_data):
    """Test data type check."""
    results = cleaning_engine._check_data_type(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'numeric_col' for issue in results['issues'])

def test_value_distribution_check(cleaning_engine, sample_data):
    """Test value distribution check."""
    results = cleaning_engine._check_value_distribution(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'numeric_col' for issue in results['issues'])

def test_cross_validation_check(cleaning_engine, sample_data):
    """Test cross validation check."""
    results = cleaning_engine._check_cross_validation(sample_data)
    
    assert results['issues']
    assert any(issue['rule'] == 'numeric_range' for issue in results['issues'])

def test_format_consistency_check(cleaning_engine, sample_data):
    """Test format consistency check."""
    results = cleaning_engine._check_format_consistency(sample_data)
    
    assert results['issues']
    assert any(issue['column'] == 'text_col' for issue in results['issues'])

def test_completeness_by_section_check(cleaning_engine, sample_data):
    """Test completeness by section check."""
    # Add missing values to section fields
    sample_data.loc[0, 'numeric_col'] = np.nan
    sample_data.loc[1, 'categorical_col'] = np.nan
    
    results = cleaning_engine._check_completeness_by_section(sample_data)
    
    assert results['issues']
    assert any(issue['section'] == 'demographics' for issue in results['issues'])

def test_process_data(cleaning_engine, sample_data):
    """Test the main process_data method."""
    results = cleaning_engine.process_data(sample_data)
    
    assert isinstance(results, dict)
    assert all(check in results for check in cleaning_engine.checks.keys())
    assert all('status' in result for result in results.values())
    assert all('issues_found' in result for result in results.values())

def test_performance_monitoring(cleaning_engine, sample_data):
    """Test performance monitoring functionality."""
    results = cleaning_engine.process_data(sample_data)
    
    assert 'summary' in results
    assert 'execution_time' in results['summary']
    assert 'check_performance' in results['summary']
    assert isinstance(results['summary']['execution_time'], float)
    assert isinstance(results['summary']['check_performance'], dict)

def test_summary_report_generation(cleaning_engine, sample_data):
    """Test summary report generation."""
    results = cleaning_engine.process_data(sample_data)
    
    assert 'summary' in results
    assert 'total_checks' in results['summary']
    assert 'total_issues_found' in results['summary']
    assert 'failed_checks' in results['summary']
    assert 'severity_distribution' in results['summary']
    
    # Verify severity distribution
    severity_dist = results['summary']['severity_distribution']
    assert all(severity in severity_dist for severity in CheckSeverity)
    assert all(isinstance(count, int) for count in severity_dist.values())

def test_check_documentation(cleaning_engine):
    """Test check documentation generation."""
    docs = cleaning_engine.get_check_documentation()
    
    assert isinstance(docs, dict)
    assert len(docs) == len(cleaning_engine.checks)
    
    # Verify documentation structure
    for check_name, check_doc in docs.items():
        assert 'description' in check_doc
        assert 'category' in check_doc
        assert 'severity' in check_doc
        assert 'configurable' in check_doc
        assert 'dependencies' in check_doc

def test_parallel_processing(cleaning_engine, sample_data):
    """Test parallel processing of checks."""
    start_time = datetime.now()
    results = cleaning_engine.process_data(sample_data)
    end_time = datetime.now()
    
    # Verify that checks were executed
    assert len(results['detailed_results']) == len(cleaning_engine.checks)
    
    # Verify performance improvement (should be faster than sequential)
    execution_time = (end_time - start_time).total_seconds()
    assert execution_time < sum(results['summary']['check_performance'].values())

def test_error_handling(cleaning_engine, sample_data):
    """Test error handling in checks."""
    # Modify a check to force an error
    def failing_check(data):
        raise ValueError("Test error")
    
    cleaning_engine.checks['missing_values']['function'] = failing_check
    
    results = cleaning_engine.process_data(sample_data)
    
    # Verify error was caught and reported
    assert results['detailed_results']['missing_values']['status'] == 'failed'
    assert 'error' in results['detailed_results']['missing_values']
    assert results['summary']['failed_checks'] > 0

def test_severity_levels(cleaning_engine, sample_data):
    """Test severity level assignment and reporting."""
    results = cleaning_engine.process_data(sample_data)
    
    # Verify severity distribution
    severity_dist = results['summary']['severity_distribution']
    assert sum(severity_dist.values()) == len(cleaning_engine.checks)
    
    # Verify severity in detailed results
    for check_result in results['detailed_results'].values():
        if check_result['status'] == 'completed':
            assert 'severity' in check_result
            assert isinstance(check_result['severity'], CheckSeverity) 