from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import re
from textblob import TextBlob
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import uuid
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CheckSeverity(Enum):
    """Severity levels for cleaning check issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CheckResult:
    """Structured result for a cleaning check."""
    check_name: str
    status: str
    issues_found: int
    severity: CheckSeverity
    details: Dict[str, Any]
    execution_time: float

class CleaningEngine:
    """
    Core data cleaning engine that implements 20 standard scrubbing checks.
    
    This engine provides comprehensive data quality checks including:
    - Data completeness and consistency
    - Outlier detection
    - Response pattern analysis
    - Text quality assessment
    - Logical validation
    - And more...
    
    Each check is configurable and can be customized based on project requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the cleaning engine with configuration.

        Args:
            config (Dict[str, Any], optional): Configuration for cleaning checks.
                Defaults to None.
        """
        self.config = config or {}
        self.checks = self._initialize_checks()
        self._setup_performance_monitoring()
        
    def _setup_performance_monitoring(self):
        """Setup performance monitoring attributes."""
        self.check_times = {}
        self.total_execution_time = 0
        
    def _initialize_checks(self) -> Dict[str, Any]:
        """
        Initialize the 20 standard cleaning checks.

        Returns:
            Dict[str, Any]: Dictionary of check functions and their configurations.
        """
        return {
            'missing_values': {
                'function': self._check_missing_values,
                'description': 'Detect and analyze missing values in the dataset',
                'category': 'data_quality',
                'severity': CheckSeverity.HIGH
            },
            'duplicates': {
                'function': self._check_duplicates,
                'description': 'Identify duplicate records',
                'category': 'data_quality'
            },
            'outliers': {
                'function': self._check_outliers,
                'description': 'Detect statistical outliers in numerical columns',
                'category': 'data_quality'
            },
            'inconsistent_categories': {
                'function': self._check_inconsistent_categories,
                'description': 'Find inconsistent category values',
                'category': 'data_quality'
            },
            'date_anomalies': {
                'function': self._check_date_anomalies,
                'description': 'Detect anomalies in date fields',
                'category': 'data_quality'
            },
            'numeric_range': {
                'function': self._check_numeric_range,
                'description': 'Check numeric values against expected ranges',
                'category': 'validation'
            },
            'text_quality': {
                'function': self._check_text_quality,
                'description': 'Analyze text quality in string columns',
                'category': 'data_quality'
            },
            'response_patterns': {
                'function': self._check_response_patterns,
                'description': 'Detect suspicious response patterns',
                'category': 'validation'
            },
            'completeness': {
                'function': self._check_completeness,
                'description': 'Check data completeness by required fields',
                'category': 'data_quality'
            },
            'consistency': {
                'function': self._check_consistency,
                'description': 'Check data consistency across related fields',
                'category': 'validation'
            },
            'speeders': {
                'function': self._check_speeders,
                'description': 'Identify respondents who completed too quickly',
                'category': 'validation'
            },
            'straightliners': {
                'function': self._check_straightliners,
                'description': 'Detect straight-line response patterns',
                'category': 'validation'
            },
            'logical_consistency': {
                'function': self._check_logical_consistency,
                'description': 'Check logical consistency between related questions',
                'category': 'validation'
            },
            'text_sentiment': {
                'function': self._check_text_sentiment,
                'description': 'Analyze sentiment in text responses',
                'category': 'data_quality'
            },
            'response_time': {
                'function': self._check_response_time,
                'description': 'Analyze response time patterns',
                'category': 'validation'
            },
            'data_type': {
                'function': self._check_data_type,
                'description': 'Verify correct data types for each column',
                'category': 'data_quality'
            },
            'value_distribution': {
                'function': self._check_value_distribution,
                'description': 'Analyze value distributions for anomalies',
                'category': 'data_quality'
            },
            'cross_validation': {
                'function': self._check_cross_validation,
                'description': 'Cross-validate related fields',
                'category': 'validation'
            },
            'format_consistency': {
                'function': self._check_format_consistency,
                'description': 'Check format consistency in text fields',
                'category': 'data_quality'
            },
            'completeness_by_section': {
                'function': self._check_completeness_by_section,
                'description': 'Check completeness by survey sections',
                'category': 'data_quality'
            }
        }

    def process_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Process the dataset through all cleaning checks.

        Args:
            data (pd.DataFrame): Input dataset to clean

        Returns:
            Dict[str, Any]: Results of all cleaning checks
        """
        start_time = datetime.now()
        results = {}
        
        # Use ThreadPoolExecutor for parallel processing of checks
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_check = {
                executor.submit(self._run_check, check_name, check_info, data): check_name
                for check_name, check_info in self.checks.items()
            }
            
            for future in future_to_check:
                check_name = future_to_check[future]
                try:
                    check_result = future.result()
                    results[check_name] = check_result
                except Exception as e:
                    logger.error(f"Error in check {check_name}: {str(e)}")
                    results[check_name] = {
                        'status': 'failed',
                        'error': str(e),
                        'issues_found': 0,
                        'severity': CheckSeverity.CRITICAL
                    }
        
        self.total_execution_time = (datetime.now() - start_time).total_seconds()
        return self._generate_summary_report(results)

    def _run_check(self, check_name: str, check_info: Dict[str, Any], data: pd.DataFrame) -> CheckResult:
        """
        Run a single cleaning check with performance monitoring.

        Args:
            check_name (str): Name of the check
            check_info (Dict[str, Any]): Check configuration
            data (pd.DataFrame): Data to check

        Returns:
            CheckResult: Result of the check
        """
        start_time = datetime.now()
        try:
            check_result = check_info['function'](data)
            execution_time = (datetime.now() - start_time).total_seconds()
            self.check_times[check_name] = execution_time
            
            return CheckResult(
                check_name=check_name,
                status='completed',
                issues_found=len(check_result.get('issues', [])),
                severity=check_info.get('severity', CheckSeverity.MEDIUM),
                details=check_result,
                execution_time=execution_time
            )
        except Exception as e:
            logger.error(f"Error in check {check_name}: {str(e)}")
            raise

    def _generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report of all checks.

        Args:
            results (Dict[str, Any]): Results from all checks

        Returns:
            Dict[str, Any]: Summary report
        """
        total_issues = sum(result.get('issues_found', 0) for result in results.values())
        failed_checks = sum(1 for result in results.values() if result.get('status') == 'failed')
        
        severity_counts = {
            severity: sum(1 for result in results.values() 
                         if result.get('severity') == severity)
            for severity in CheckSeverity
        }
        
        return {
            'summary': {
                'total_checks': len(results),
                'total_issues_found': total_issues,
                'failed_checks': failed_checks,
                'severity_distribution': severity_counts,
                'execution_time': self.total_execution_time,
                'check_performance': self.check_times
            },
            'detailed_results': results
        }

    def _check_missing_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values in the dataset."""
        missing_stats = data.isnull().sum()
        missing_percentages = (missing_stats / len(data)) * 100
        
        issues = []
        for col in data.columns:
            if missing_percentages[col] > 0:
                issues.append({
                    'column': col,
                    'missing_count': int(missing_stats[col]),
                    'missing_percentage': float(missing_percentages[col])
                })
        
        return {
            'issues': issues,
            'summary': {
                'total_columns_with_missing': len(issues),
                'max_missing_percentage': float(missing_percentages.max())
            }
        }

    def _check_duplicates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for duplicate records."""
        duplicates = data.duplicated()
        duplicate_count = duplicates.sum()
        
        issues = []
        if duplicate_count > 0:
            duplicate_indices = duplicates[duplicates].index.tolist()
            issues.append({
                'duplicate_count': int(duplicate_count),
                'duplicate_indices': duplicate_indices
            })
        
        return {
            'issues': issues,
            'summary': {
                'total_duplicates': int(duplicate_count)
            }
        }

    def _check_outliers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numerical columns."""
        issues = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Use Isolation Forest for outlier detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers = iso_forest.fit_predict(data[[col]].dropna())
            
            outlier_indices = data[col].dropna().index[outliers == -1].tolist()
            if outlier_indices:
                issues.append({
                    'column': col,
                    'outlier_count': len(outlier_indices),
                    'outlier_indices': outlier_indices
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_outliers': len(issues)
            }
        }

    def _check_inconsistent_categories(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for inconsistent category values."""
        issues = []
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            # Get unique values and their frequencies
            value_counts = data[col].value_counts()
            total_values = len(data[col].dropna())
            
            # Check for low frequency categories
            low_freq_categories = value_counts[value_counts < total_values * 0.01]
            if not low_freq_categories.empty:
                issues.append({
                    'column': col,
                    'low_freq_categories': low_freq_categories.to_dict()
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_inconsistencies': len(issues)
            }
        }

    def _check_date_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for anomalies in date fields."""
        issues = []
        date_cols = data.select_dtypes(include=['datetime64']).columns
        
        for col in date_cols:
            # Check for future dates
            future_dates = data[data[col] > datetime.now()]
            if not future_dates.empty:
                issues.append({
                    'column': col,
                    'issue_type': 'future_dates',
                    'count': len(future_dates),
                    'indices': future_dates.index.tolist()
                })
            
            # Check for unreasonable date ranges
            date_range = data[col].max() - data[col].min()
            if date_range.days > 365 * 10:  # More than 10 years
                issues.append({
                    'column': col,
                    'issue_type': 'large_date_range',
                    'range_days': date_range.days
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_anomalies': len(issues)
            }
        }

    def _check_numeric_range(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check numeric values against expected ranges."""
        issues = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Check for values outside 3 standard deviations
            mean = data[col].mean()
            std = data[col].std()
            outliers = data[abs(data[col] - mean) > 3 * std]
            
            if not outliers.empty:
                issues.append({
                    'column': col,
                    'outlier_count': len(outliers),
                    'min_value': float(outliers[col].min()),
                    'max_value': float(outliers[col].max())
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_range_issues': len(issues)
            }
        }

    def _check_text_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze text quality in string columns."""
        issues = []
        text_cols = data.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            # Check for very short responses
            short_texts = data[data[col].str.len() < 3].index.tolist()
            if short_texts:
                issues.append({
                    'column': col,
                    'issue_type': 'short_texts',
                    'count': len(short_texts),
                    'indices': short_texts
                })
            
            # Check for repeated characters
            repeated_chars = data[data[col].str.contains(r'(.)\1{3,}')].index.tolist()
            if repeated_chars:
                issues.append({
                    'column': col,
                    'issue_type': 'repeated_chars',
                    'count': len(repeated_chars),
                    'indices': repeated_chars
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_quality_issues': len(issues)
            }
        }

    def _check_response_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect suspicious response patterns."""
        issues = []
        
        # Check for alternating patterns
        for col in data.columns:
            if data[col].dtype in [np.number, 'object']:
                values = data[col].values
                if len(values) > 2:
                    # Check for alternating patterns
                    is_alternating = all(values[i] == values[i+2] for i in range(len(values)-2))
                    if is_alternating:
                        issues.append({
                            'column': col,
                            'issue_type': 'alternating_pattern',
                            'pattern_length': len(values)
                        })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_patterns': len(issues)
            }
        }

    def _check_completeness(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check data completeness by required fields."""
        issues = []
        required_fields = self.config.get('required_fields', [])
        
        for field in required_fields:
            if field in data.columns:
                missing_count = data[field].isnull().sum()
                if missing_count > 0:
                    issues.append({
                        'field': field,
                        'missing_count': int(missing_count),
                        'completeness_percentage': float((len(data) - missing_count) / len(data) * 100)
                    })
        
        return {
            'issues': issues,
            'summary': {
                'incomplete_required_fields': len(issues)
            }
        }

    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check data consistency across related fields."""
        issues = []
        consistency_rules = self.config.get('consistency_rules', [])
        
        for rule in consistency_rules:
            if all(field in data.columns for field in rule['fields']):
                # Apply consistency rule
                condition = rule['condition']
                violations = data[~condition].index.tolist()
                
                if violations:
                    issues.append({
                        'rule': rule['name'],
                        'violation_count': len(violations),
                        'violation_indices': violations
                    })
        
        return {
            'issues': issues,
            'summary': {
                'consistency_violations': len(issues)
            }
        }

    def _check_speeders(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify respondents who completed too quickly."""
        issues = []
        
        if 'completion_time' in data.columns:
            # Calculate average completion time
            avg_time = data['completion_time'].mean()
            std_time = data['completion_time'].std()
            
            # Identify speeders (completion time < mean - 2*std)
            speeders = data[data['completion_time'] < (avg_time - 2*std_time)]
            
            if not speeders.empty:
                issues.append({
                    'speeder_count': len(speeders),
                    'speeder_indices': speeders.index.tolist(),
                    'threshold': float(avg_time - 2*std_time)
                })
        
        return {
            'issues': issues,
            'summary': {
                'total_speeders': len(issues[0]['speeder_indices']) if issues else 0
            }
        }

    def _check_straightliners(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect straight-line response patterns."""
        issues = []
        
        # Get numeric columns for straight-lining check
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for i in range(len(data)):
            row = data.iloc[i]
            # Check if all numeric values are the same
            if len(numeric_cols) > 1:
                values = row[numeric_cols]
                if len(values.unique()) == 1:
                    issues.append({
                        'row_index': i,
                        'value': float(values.iloc[0])
                    })
        
        return {
            'issues': issues,
            'summary': {
                'straightliner_count': len(issues)
            }
        }

    def _check_logical_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check logical consistency between related questions."""
        issues = []
        logical_rules = self.config.get('logical_rules', [])
        
        for rule in logical_rules:
            if all(field in data.columns for field in rule['fields']):
                # Apply logical rule
                condition = rule['condition']
                violations = data[~condition].index.tolist()
                
                if violations:
                    issues.append({
                        'rule': rule['name'],
                        'violation_count': len(violations),
                        'violation_indices': violations
                    })
        
        return {
            'issues': issues,
            'summary': {
                'logical_violations': len(issues)
            }
        }

    def _check_text_sentiment(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment in text responses."""
        issues = []
        text_cols = data.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            # Analyze sentiment for each text response
            sentiments = []
            for text in data[col].dropna():
                blob = TextBlob(str(text))
                sentiments.append(blob.sentiment.polarity)
            
            # Check for extreme sentiments
            if sentiments:
                extreme_sentiments = [i for i, s in enumerate(sentiments) if abs(s) > 0.8]
                if extreme_sentiments:
                    issues.append({
                        'column': col,
                        'extreme_sentiment_count': len(extreme_sentiments),
                        'indices': extreme_sentiments
                    })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_extreme_sentiments': len(issues)
            }
        }

    def _check_response_time(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze response time patterns."""
        issues = []
        
        if 'response_time' in data.columns:
            # Check for unusually long response times
            avg_time = data['response_time'].mean()
            std_time = data['response_time'].std()
            
            long_responses = data[data['response_time'] > (avg_time + 2*std_time)]
            if not long_responses.empty:
                issues.append({
                    'long_response_count': len(long_responses),
                    'indices': long_responses.index.tolist(),
                    'threshold': float(avg_time + 2*std_time)
                })
        
        return {
            'issues': issues,
            'summary': {
                'unusual_response_times': len(issues[0]['indices']) if issues else 0
            }
        }

    def _check_data_type(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Verify correct data types for each column."""
        issues = []
        expected_types = self.config.get('expected_types', {})
        
        for col, expected_type in expected_types.items():
            if col in data.columns:
                current_type = str(data[col].dtype)
                if current_type != expected_type:
                    issues.append({
                        'column': col,
                        'current_type': current_type,
                        'expected_type': expected_type
                    })
        
        return {
            'issues': issues,
            'summary': {
                'type_mismatches': len(issues)
            }
        }

    def _check_value_distribution(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze value distributions for anomalies."""
        issues = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Calculate distribution statistics
            mean = data[col].mean()
            median = data[col].median()
            
            # Check for significant mean-median difference
            if abs(mean - median) > 0.5 * std:
                issues.append({
                    'column': col,
                    'mean': float(mean),
                    'median': float(median),
                    'difference': float(abs(mean - median))
                })
        
        return {
            'issues': issues,
            'summary': {
                'columns_with_distribution_issues': len(issues)
            }
        }

    def _check_cross_validation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Cross-validate related fields."""
        issues = []
        validation_rules = self.config.get('validation_rules', [])
        
        for rule in validation_rules:
            if all(field in data.columns for field in rule['fields']):
                # Apply validation rule
                condition = rule['condition']
                violations = data[~condition].index.tolist()
                
                if violations:
                    issues.append({
                        'rule': rule['name'],
                        'violation_count': len(violations),
                        'violation_indices': violations
                    })
        
        return {
            'issues': issues,
            'summary': {
                'validation_violations': len(issues)
            }
        }

    def _check_format_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check format consistency in text fields."""
        issues = []
        format_rules = self.config.get('format_rules', {})
        
        for col, pattern in format_rules.items():
            if col in data.columns:
                # Check format consistency
                violations = data[~data[col].str.match(pattern)].index.tolist()
                if violations:
                    issues.append({
                        'column': col,
                        'violation_count': len(violations),
                        'violation_indices': violations
                    })
        
        return {
            'issues': issues,
            'summary': {
                'format_violations': len(issues)
            }
        }

    def _check_completeness_by_section(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check completeness by survey sections."""
        issues = []
        section_fields = self.config.get('section_fields', {})
        
        for section, fields in section_fields.items():
            if all(field in data.columns for field in fields):
                # Calculate completeness for section
                section_data = data[fields]
                missing_by_section = section_data.isnull().sum(axis=1)
                incomplete_sections = missing_by_section[missing_by_section > 0]
                
                if not incomplete_sections.empty:
                    issues.append({
                        'section': section,
                        'incomplete_count': len(incomplete_sections),
                        'indices': incomplete_sections.index.tolist()
                    })
        
        return {
            'issues': issues,
            'summary': {
                'incomplete_sections': len(issues)
            }
        }

    def get_check_documentation(self) -> Dict[str, Any]:
        """
        Get documentation for all cleaning checks.

        Returns:
            Dict[str, Any]: Documentation for each check
        """
        return {
            check_name: {
                'description': check_info['description'],
                'category': check_info['category'],
                'severity': check_info.get('severity', CheckSeverity.MEDIUM).value,
                'configurable': bool(check_info.get('config', {})),
                'dependencies': check_info.get('dependencies', [])
            }
            for check_name, check_info in self.checks.items()
        } 