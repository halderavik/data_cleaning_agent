from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import re
from datetime import datetime, timedelta
import json

class BotDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, df: pd.DataFrame, 
                        text_columns: List[str],
                        time_column: Optional[str] = None,
                        ip_column: Optional[str] = None) -> np.ndarray:
        """
        Extract features for bot detection from survey responses.
        
        Args:
            df: DataFrame containing survey responses
            text_columns: List of columns containing text responses
            time_column: Optional column containing response timestamps
            ip_column: Optional column containing IP addresses
            
        Returns:
            Feature matrix for bot detection
        """
        features = []
        
        # Text-based features
        for col in text_columns:
            # Response length
            features.append(df[col].str.len())
            
            # Word count
            features.append(df[col].str.split().str.len())
            
            # Character diversity (unique chars / total chars)
            features.append(df[col].apply(lambda x: len(set(str(x))) / len(str(x)) if len(str(x)) > 0 else 0))
            
            # Special character ratio
            features.append(df[col].str.count(r'[^a-zA-Z0-9\s]') / df[col].str.len())
            
            # Capital letter ratio
            features.append(df[col].str.count(r'[A-Z]') / df[col].str.len())
            
            # Number ratio
            features.append(df[col].str.count(r'[0-9]') / df[col].str.len())
        
        # Time-based features
        if time_column:
            # Convert to datetime if string
            if df[time_column].dtype == 'object':
                df[time_column] = pd.to_datetime(df[time_column])
            
            # Response time (seconds)
            if len(df) > 1:
                time_diffs = df[time_column].diff().dt.total_seconds()
                features.append(time_diffs)
            
            # Time of day (hour)
            features.append(df[time_column].dt.hour)
            
            # Day of week
            features.append(df[time_column].dt.dayofweek)
        
        # IP-based features
        if ip_column:
            # IP frequency
            ip_counts = df[ip_column].value_counts()
            features.append(df[ip_column].map(ip_counts))
            
            # IP diversity (number of unique IPs)
            features.append(pd.Series([len(df[ip_column].unique())] * len(df)))
        
        # Combine all features
        feature_matrix = np.column_stack(features)
        
        # Handle NaN values
        feature_matrix = np.nan_to_num(feature_matrix)
        
        return feature_matrix
    
    def train(self, df: pd.DataFrame,
              text_columns: List[str],
              known_bots: List[int],
              time_column: Optional[str] = None,
              ip_column: Optional[str] = None) -> None:
        """
        Train the bot detection model.
        
        Args:
            df: DataFrame containing survey responses
            text_columns: List of columns containing text responses
            known_bots: List of indices of known bot responses
            time_column: Optional column containing response timestamps
            ip_column: Optional column containing IP addresses
        """
        # Extract features
        X = self.extract_features(df, text_columns, time_column, ip_column)
        
        # Create labels (1 for bots, 0 for humans)
        y = np.zeros(len(df))
        y[known_bots] = 1
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
    
    def detect_bots(self, df: pd.DataFrame,
                   text_columns: List[str],
                   time_column: Optional[str] = None,
                   ip_column: Optional[str] = None,
                   threshold: float = 0.7) -> Dict[str, Any]:
        """
        Detect potential bot responses in survey data.
        
        Args:
            df: DataFrame containing survey responses
            text_columns: List of columns containing text responses
            time_column: Optional column containing response timestamps
            ip_column: Optional column containing IP addresses
            threshold: Probability threshold for bot classification
            
        Returns:
            Dict containing bot detection results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detection")
        
        # Extract features
        X = self.extract_features(df, text_columns, time_column, ip_column)
        
        # Scale features
        X = self.scaler.transform(X)
        
        # Get bot probabilities
        bot_probs = self.model.predict_proba(X)[:, 1]
        
        # Identify potential bots
        potential_bots = np.where(bot_probs > threshold)[0]
        
        # Calculate additional metrics
        response_times = []
        if time_column and len(df) > 1:
            time_diffs = df[time_column].diff().dt.total_seconds()
            response_times = time_diffs[potential_bots].tolist()
        
        # Prepare detailed results
        bot_details = []
        for idx in potential_bots:
            detail = {
                'index': int(idx),
                'bot_probability': float(bot_probs[idx]),
                'text_responses': {col: str(df.iloc[idx][col]) for col in text_columns}
            }
            
            if time_column:
                detail['response_time'] = float(response_times[idx]) if idx < len(response_times) else None
            
            if ip_column:
                detail['ip_address'] = str(df.iloc[idx][ip_column])
            
            bot_details.append(detail)
        
        return {
            'total_responses': len(df),
            'potential_bots': len(potential_bots),
            'bot_probability_threshold': threshold,
            'average_bot_probability': float(np.mean(bot_probs)),
            'bot_details': bot_details,
            'severity': 'critical' if len(potential_bots) > len(df) * 0.1 else 'high'
        }
    
    def analyze_patterns(self, df: pd.DataFrame,
                        text_columns: List[str],
                        time_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze patterns in responses that might indicate bot behavior.
        
        Args:
            df: DataFrame containing survey responses
            text_columns: List of columns containing text responses
            time_column: Optional column containing response timestamps
            
        Returns:
            Dict containing pattern analysis results
        """
        patterns = []
        
        # Check for identical responses
        for col in text_columns:
            value_counts = df[col].value_counts()
            identical_responses = value_counts[value_counts > 1]
            
            if not identical_responses.empty:
                patterns.append({
                    'type': 'identical_responses',
                    'column': col,
                    'count': len(identical_responses),
                    'examples': identical_responses.head(3).to_dict()
                })
        
        # Check for response time patterns
        if time_column and len(df) > 1:
            time_diffs = df[time_column].diff().dt.total_seconds()
            
            # Check for unusually consistent response times
            if time_diffs.std() < 1.0:  # Less than 1 second standard deviation
                patterns.append({
                    'type': 'consistent_timing',
                    'mean_response_time': float(time_diffs.mean()),
                    'std_response_time': float(time_diffs.std())
                })
            
            # Check for impossibly fast responses
            fast_responses = time_diffs[time_diffs < 1.0]  # Less than 1 second
            if len(fast_responses) > 0:
                patterns.append({
                    'type': 'fast_responses',
                    'count': len(fast_responses),
                    'indices': fast_responses.index.tolist()
                })
        
        # Check for text patterns
        for col in text_columns:
            # Check for repetitive patterns
            repetitive = df[col].str.count(r'(\b\w+\b)(?:\s+\1\b)+')
            if repetitive.any():
                patterns.append({
                    'type': 'repetitive_text',
                    'column': col,
                    'count': int(repetitive.sum()),
                    'indices': repetitive[repetitive > 0].index.tolist()
                })
            
            # Check for keyboard patterns
            keyboard_patterns = df[col].str.count(r'(qwerty|asdfgh|zxcvbn)')
            if keyboard_patterns.any():
                patterns.append({
                    'type': 'keyboard_patterns',
                    'column': col,
                    'count': int(keyboard_patterns.sum()),
                    'indices': keyboard_patterns[keyboard_patterns > 0].index.tolist()
                })
        
        return {
            'total_responses': len(df),
            'patterns_found': len(patterns),
            'pattern_details': patterns,
            'severity': 'high' if len(patterns) > 3 else 'medium'
        } 