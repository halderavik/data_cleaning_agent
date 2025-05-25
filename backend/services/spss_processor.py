import pyreadstat
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import re
import ipaddress
from datetime import datetime

class SPSSProcessor:
    """
    Service for loading and analyzing SPSS (.sav) files.
    """
    def __init__(self):
        self.data = None
        self.metadata = None
        self.schema = None

    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load SPSS file and extract data and metadata.

        Args:
            file_path (str): Path to the SPSS (.sav) file.

        Returns:
            dict: Structure analysis of the SPSS file.
        """
        self.data, self.metadata = pyreadstat.read_sav(file_path)
        self.schema = self.detect_schema()
        return self.analyze_structure()

    def analyze_structure(self) -> Dict[str, Any]:
        """
        Analyze data structure and variable types.

        Returns:
            dict: Structure information (total records, variables, types, value labels)
        """
        if self.data is None or self.metadata is None:
            raise ValueError("No SPSS file loaded.")
        
        structure = {
            'total_records': len(self.data),
            'variables': list(self.data.columns),
            'variable_types': self.metadata.original_variable_types,
            'value_labels': self.metadata.variable_value_labels,
            'schema': self.schema,
            'data_quality': self.analyze_data_quality()
        }
        return structure

    def detect_schema(self) -> Dict[str, Any]:
        """
        Detect data types and patterns in the dataset.

        Returns:
            dict: Schema information for each variable
        """
        schema = {}
        
        for column in self.data.columns:
            column_data = self.data[column]
            schema[column] = {
                'type': self._detect_data_type(column_data),
                'null_count': column_data.isna().sum(),
                'unique_count': column_data.nunique(),
                'distribution': self._analyze_distribution(column_data)
            }
            
            # Add specific validations based on detected type
            if schema[column]['type'] == 'email':
                schema[column]['validation'] = self._validate_emails(column_data)
            elif schema[column]['type'] == 'ip_address':
                schema[column]['validation'] = self._validate_ip_addresses(column_data)
            elif schema[column]['type'] == 'date':
                schema[column]['validation'] = self._validate_dates(column_data)
        
        return schema

    def _detect_data_type(self, column_data: pd.Series) -> str:
        """
        Detect the data type of a column.

        Args:
            column_data (pd.Series): Column data to analyze.

        Returns:
            str: Detected data type
        """
        # Check for email pattern
        if column_data.astype(str).str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').all():
            return 'email'
        
        # Check for IP address pattern
        if column_data.astype(str).str.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$').all():
            return 'ip_address'
        
        # Check for date pattern
        if column_data.astype(str).str.match(r'^\d{4}-\d{2}-\d{2}$').all():
            return 'date'
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(column_data):
            return 'numeric'
        
        # Default to text
        return 'text'

    def _analyze_distribution(self, column_data: pd.Series) -> Dict[str, Any]:
        """
        Analyze the distribution of values in a column.

        Args:
            column_data (pd.Series): Column data to analyze.

        Returns:
            dict: Distribution statistics
        """
        if pd.api.types.is_numeric_dtype(column_data):
            return {
                'mean': float(column_data.mean()),
                'median': float(column_data.median()),
                'std': float(column_data.std()),
                'min': float(column_data.min()),
                'max': float(column_data.max())
            }
        else:
            value_counts = column_data.value_counts()
            return {
                'unique_values': len(value_counts),
                'most_common': value_counts.head(5).to_dict(),
                'least_common': value_counts.tail(5).to_dict()
            }

    def _validate_emails(self, column_data: pd.Series) -> Dict[str, Any]:
        """
        Validate email addresses in a column.

        Args:
            column_data (pd.Series): Column containing email addresses.

        Returns:
            dict: Validation results
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_emails = column_data[~column_data.astype(str).str.match(email_pattern)]
        
        return {
            'valid_count': len(column_data) - len(invalid_emails),
            'invalid_count': len(invalid_emails),
            'invalid_values': invalid_emails.tolist() if len(invalid_emails) > 0 else []
        }

    def _validate_ip_addresses(self, column_data: pd.Series) -> Dict[str, Any]:
        """
        Validate IP addresses in a column.

        Args:
            column_data (pd.Series): Column containing IP addresses.

        Returns:
            dict: Validation results
        """
        invalid_ips = []
        for ip in column_data.dropna():
            try:
                ipaddress.ip_address(str(ip))
            except ValueError:
                invalid_ips.append(ip)
        
        return {
            'valid_count': len(column_data) - len(invalid_ips),
            'invalid_count': len(invalid_ips),
            'invalid_values': invalid_ips
        }

    def _validate_dates(self, column_data: pd.Series) -> Dict[str, Any]:
        """
        Validate dates in a column.

        Args:
            column_data (pd.Series): Column containing dates.

        Returns:
            dict: Validation results
        """
        invalid_dates = []
        for date in column_data.dropna():
            try:
                datetime.strptime(str(date), '%Y-%m-%d')
            except ValueError:
                invalid_dates.append(date)
        
        return {
            'valid_count': len(column_data) - len(invalid_dates),
            'invalid_count': len(invalid_dates),
            'invalid_values': invalid_dates
        }

    def analyze_data_quality(self) -> Dict[str, Any]:
        """
        Analyze overall data quality metrics.

        Returns:
            dict: Data quality metrics
        """
        quality_metrics = {
            'completeness': self._calculate_completeness(),
            'consistency': self._calculate_consistency(),
            'validity': self._calculate_validity()
        }
        
        # Calculate overall quality score
        quality_metrics['overall_score'] = (
            quality_metrics['completeness'] * 0.4 +
            quality_metrics['consistency'] * 0.3 +
            quality_metrics['validity'] * 0.3
        )
        
        return quality_metrics

    def _calculate_completeness(self) -> float:
        """
        Calculate data completeness score.

        Returns:
            float: Completeness score (0-1)
        """
        total_cells = self.data.size
        null_cells = self.data.isna().sum().sum()
        return 1 - (null_cells / total_cells)

    def _calculate_consistency(self) -> float:
        """
        Calculate data consistency score.

        Returns:
            float: Consistency score (0-1)
        """
        consistency_scores = []
        
        for column in self.data.columns:
            if self.schema[column]['type'] in ['numeric', 'date']:
                # Check for outliers
                if self.schema[column]['type'] == 'numeric':
                    q1 = self.data[column].quantile(0.25)
                    q3 = self.data[column].quantile(0.75)
                    iqr = q3 - q1
                    outliers = ((self.data[column] < (q1 - 1.5 * iqr)) | 
                              (self.data[column] > (q3 + 1.5 * iqr))).sum()
                    consistency_scores.append(1 - (outliers / len(self.data)))
        
        return np.mean(consistency_scores) if consistency_scores else 1.0

    def _calculate_validity(self) -> float:
        """
        Calculate data validity score.

        Returns:
            float: Validity score (0-1)
        """
        validity_scores = []
        
        for column in self.data.columns:
            if 'validation' in self.schema[column]:
                validation = self.schema[column]['validation']
                if validation['invalid_count'] > 0:
                    validity_scores.append(
                        1 - (validation['invalid_count'] / len(self.data))
                    )
        
        return np.mean(validity_scores) if validity_scores else 1.0 