from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime

class AdvancedScrubbing:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def check_response_brevity(self, df: pd.DataFrame, text_column: str, min_words: int = 3) -> Dict[str, Any]:
        """
        Check for overly brief responses that may indicate low-quality data.
        
        Args:
            df: DataFrame containing the survey data
            text_column: Name of the column containing text responses
            min_words: Minimum number of words expected in a valid response
            
        Returns:
            Dict containing brevity analysis results
        """
        word_counts = df[text_column].str.split().str.len()
        brief_responses = df[word_counts < min_words]
        
        return {
            'total_responses': len(df),
            'brief_responses': len(brief_responses),
            'brief_response_indices': brief_responses.index.tolist(),
            'severity': 'high' if len(brief_responses) > len(df) * 0.1 else 'medium'
        }
    
    def check_closed_open_consistency(self, df: pd.DataFrame, 
                                    closed_column: str, 
                                    open_column: str,
                                    expected_keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Validate consistency between closed-ended and open-ended responses.
        
        Args:
            df: DataFrame containing the survey data
            closed_column: Name of the column with closed-ended responses
            open_column: Name of the column with open-ended responses
            expected_keywords: Dict mapping closed responses to expected keywords
            
        Returns:
            Dict containing consistency analysis results
        """
        inconsistencies = []
        
        for idx, row in df.iterrows():
            closed_response = str(row[closed_column]).lower()
            open_response = str(row[open_column]).lower()
            
            if closed_response in expected_keywords:
                expected = expected_keywords[closed_response]
                if not any(keyword.lower() in open_response for keyword in expected):
                    inconsistencies.append({
                        'index': idx,
                        'closed_response': closed_response,
                        'open_response': open_response,
                        'expected_keywords': expected
                    })
        
        return {
            'total_responses': len(df),
            'inconsistent_responses': len(inconsistencies),
            'inconsistency_details': inconsistencies,
            'severity': 'high' if len(inconsistencies) > len(df) * 0.15 else 'medium'
        }
    
    def check_plagiarism(self, df: pd.DataFrame, text_column: str, similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        Detect potential plagiarism in text responses using TF-IDF and cosine similarity.
        
        Args:
            df: DataFrame containing the survey data
            text_column: Name of the column containing text responses
            similarity_threshold: Threshold for considering responses as similar
            
        Returns:
            Dict containing plagiarism analysis results
        """
        # Clean and prepare text
        texts = df[text_column].fillna('').astype(str)
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find similar pairs
        similar_pairs = []
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i][j] > similarity_threshold:
                    similar_pairs.append({
                        'index1': i,
                        'index2': j,
                        'similarity_score': similarity_matrix[i][j],
                        'text1': texts.iloc[i],
                        'text2': texts.iloc[j]
                    })
        
        return {
            'total_responses': len(df),
            'similar_pairs': len(similar_pairs),
            'similarity_details': similar_pairs,
            'severity': 'critical' if len(similar_pairs) > len(df) * 0.05 else 'high'
        }
    
    def check_brand_recall(self, df: pd.DataFrame, 
                          brand_column: str,
                          expected_brands: List[str],
                          context_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate brand recall responses against expected brands and context.
        
        Args:
            df: DataFrame containing the survey data
            brand_column: Name of the column containing brand responses
            expected_brands: List of expected brand names
            context_columns: Optional list of columns providing context
            
        Returns:
            Dict containing brand recall analysis results
        """
        invalid_brands = []
        
        for idx, row in df.iterrows():
            brand = str(row[brand_column]).lower().strip()
            if brand not in [b.lower() for b in expected_brands]:
                context = {}
                if context_columns:
                    context = {col: row[col] for col in context_columns}
                
                invalid_brands.append({
                    'index': idx,
                    'brand': brand,
                    'context': context
                })
        
        return {
            'total_responses': len(df),
            'invalid_brands': len(invalid_brands),
            'invalid_brand_details': invalid_brands,
            'severity': 'high' if len(invalid_brands) > len(df) * 0.1 else 'medium'
        }
    
    def check_target_audience(self, df: pd.DataFrame,
                             demographic_columns: Dict[str, List[Any]],
                             target_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if respondents meet target audience criteria.
        
        Args:
            df: DataFrame containing the survey data
            demographic_columns: Dict mapping demographic columns to valid values
            target_criteria: Dict defining target audience criteria
            
        Returns:
            Dict containing target audience analysis results
        """
        ineligible_respondents = []
        
        for idx, row in df.iterrows():
            eligibility_issues = []
            
            for col, valid_values in demographic_columns.items():
                if row[col] not in valid_values:
                    eligibility_issues.append({
                        'column': col,
                        'value': row[col],
                        'valid_values': valid_values
                    })
            
            if eligibility_issues:
                ineligible_respondents.append({
                    'index': idx,
                    'issues': eligibility_issues
                })
        
        return {
            'total_responses': len(df),
            'ineligible_respondents': len(ineligible_respondents),
            'ineligibility_details': ineligible_respondents,
            'severity': 'high' if len(ineligible_respondents) > len(df) * 0.2 else 'medium'
        }
    
    def check_topic_awareness(self, df: pd.DataFrame,
                             topic_column: str,
                             knowledge_columns: List[str],
                             min_correct_answers: int) -> Dict[str, Any]:
        """
        Analyze respondents' awareness and knowledge of the survey topic.
        
        Args:
            df: DataFrame containing the survey data
            topic_column: Column indicating topic familiarity
            knowledge_columns: List of columns testing topic knowledge
            min_correct_answers: Minimum number of correct answers required
            
        Returns:
            Dict containing topic awareness analysis results
        """
        low_awareness = []
        
        for idx, row in df.iterrows():
            correct_answers = sum(1 for col in knowledge_columns if row[col] == True)
            if correct_answers < min_correct_answers:
                low_awareness.append({
                    'index': idx,
                    'topic_familiarity': row[topic_column],
                    'correct_answers': correct_answers,
                    'required_answers': min_correct_answers
                })
        
        return {
            'total_responses': len(df),
            'low_awareness_count': len(low_awareness),
            'low_awareness_details': low_awareness,
            'severity': 'high' if len(low_awareness) > len(df) * 0.3 else 'medium'
        }
    
    def check_sentiment_consistency(self, df: pd.DataFrame,
                                  sentiment_columns: List[str],
                                  threshold: float = 0.3) -> Dict[str, Any]:
        """
        Check for consistency in sentiment across related responses.
        
        Args:
            df: DataFrame containing the survey data
            sentiment_columns: List of columns to analyze for sentiment
            threshold: Maximum allowed sentiment difference
            
        Returns:
            Dict containing sentiment consistency analysis results
        """
        inconsistencies = []
        
        for idx, row in df.iterrows():
            sentiments = []
            for col in sentiment_columns:
                text = str(row[col])
                sentiment = TextBlob(text).sentiment.polarity
                sentiments.append(sentiment)
            
            if max(sentiments) - min(sentiments) > threshold:
                inconsistencies.append({
                    'index': idx,
                    'sentiments': dict(zip(sentiment_columns, sentiments)),
                    'difference': max(sentiments) - min(sentiments)
                })
        
        return {
            'total_responses': len(df),
            'inconsistent_sentiments': len(inconsistencies),
            'inconsistency_details': inconsistencies,
            'severity': 'medium' if len(inconsistencies) > len(df) * 0.2 else 'low'
        } 