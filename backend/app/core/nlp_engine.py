from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from textblob import TextBlob
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import spacy
import re
from collections import defaultdict

class NLEngine:
    def __init__(self):
        # Initialize sentiment analysis pipeline
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        # Initialize zero-shot classification pipeline
        self.zero_shot_classifier = pipeline("zero-shot-classification")
        
        # Load spaCy model for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Download if not available
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Custom entity patterns
        self.entity_patterns = {
            'product': r'\b(product|item|goods|merchandise)\b',
            'service': r'\b(service|support|assistance|help)\b',
            'price': r'\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:dollars|USD)',
            'date': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
        }
    
    def analyze_sentiment(self, texts: Union[str, List[str]], 
                         detailed: bool = False) -> Dict[str, Any]:
        """
        Analyze sentiment of text responses.
        
        Args:
            texts: Single text or list of texts to analyze
            detailed: Whether to return detailed analysis
            
        Returns:
            Dict containing sentiment analysis results
        """
        if isinstance(texts, str):
            texts = [texts]
        
        results = []
        for text in texts:
            # Get basic sentiment
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Get detailed analysis if requested
            if detailed:
                blob = TextBlob(text)
                detailed_analysis = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity,
                    'sentences': len(blob.sentences),
                    'words': len(blob.words),
                    'avg_word_length': np.mean([len(word) for word in blob.words]) if blob.words else 0
                }
            else:
                detailed_analysis = None
            
            results.append({
                'text': text,
                'label': sentiment['label'],
                'score': sentiment['score'],
                'detailed_analysis': detailed_analysis
            })
        
        return {
            'total_texts': len(texts),
            'results': results,
            'average_sentiment': np.mean([r['score'] for r in results]),
            'sentiment_distribution': {
                'positive': sum(1 for r in results if r['label'] == 'POSITIVE'),
                'negative': sum(1 for r in results if r['label'] == 'NEGATIVE'),
                'neutral': sum(1 for r in results if r['label'] == 'NEUTRAL')
            }
        }
    
    def zero_shot_classify(self, texts: Union[str, List[str]],
                          candidate_labels: List[str],
                          multi_label: bool = False) -> Dict[str, Any]:
        """
        Classify texts into predefined categories using zero-shot classification.
        
        Args:
            texts: Single text or list of texts to classify
            candidate_labels: List of possible categories
            multi_label: Whether to allow multiple labels per text
            
        Returns:
            Dict containing classification results
        """
        if isinstance(texts, str):
            texts = [texts]
        
        results = []
        for text in texts:
            classification = self.zero_shot_classifier(
                text,
                candidate_labels,
                multi_label=multi_label
            )
            
            results.append({
                'text': text,
                'labels': classification['labels'],
                'scores': classification['scores']
            })
        
        # Calculate label distribution
        label_distribution = defaultdict(int)
        for result in results:
            for label in result['labels']:
                label_distribution[label] += 1
        
        return {
            'total_texts': len(texts),
            'results': results,
            'label_distribution': dict(label_distribution)
        }
    
    def extract_entities(self, texts: Union[str, List[str]],
                        custom_patterns: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extract named entities and custom patterns from texts.
        
        Args:
            texts: Single text or list of texts to analyze
            custom_patterns: Optional dict of custom regex patterns
            
        Returns:
            Dict containing entity extraction results
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Combine default and custom patterns
        patterns = {**self.entity_patterns, **(custom_patterns or {})}
        
        results = []
        for text in texts:
            # Get spaCy entities
            doc = self.nlp(text)
            spacy_entities = {
                ent.label_: ent.text
                for ent in doc.ents
            }
            
            # Get custom pattern matches
            custom_entities = {}
            for entity_type, pattern in patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                custom_entities[entity_type] = [m.group() for m in matches]
            
            results.append({
                'text': text,
                'spacy_entities': spacy_entities,
                'custom_entities': custom_entities
            })
        
        # Calculate entity statistics
        entity_stats = defaultdict(lambda: defaultdict(int))
        for result in results:
            for label, text in result['spacy_entities'].items():
                entity_stats['spacy'][label] += 1
            
            for entity_type, matches in result['custom_entities'].items():
                entity_stats['custom'][entity_type] += len(matches)
        
        return {
            'total_texts': len(texts),
            'results': results,
            'entity_statistics': {
                'spacy': dict(entity_stats['spacy']),
                'custom': dict(entity_stats['custom'])
            }
        }
    
    def analyze_text_quality(self, texts: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze text quality metrics.
        
        Args:
            texts: Single text or list of texts to analyze
            
        Returns:
            Dict containing text quality analysis results
        """
        if isinstance(texts, str):
            texts = [texts]
        
        results = []
        for text in texts:
            # Basic metrics
            words = text.split()
            sentences = TextBlob(text).sentences
            
            # Calculate metrics
            metrics = {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
                'avg_sentence_length': np.mean([len(sent.words) for sent in sentences]) if sentences else 0,
                'unique_word_ratio': len(set(words)) / len(words) if words else 0,
                'capitalization_ratio': sum(1 for word in words if word.isupper()) / len(words) if words else 0,
                'punctuation_ratio': sum(1 for char in text if char in '.,!?;:') / len(text) if text else 0
            }
            
            # Calculate readability scores
            if sentences:
                avg_sentence_length = metrics['avg_sentence_length']
                avg_word_length = metrics['avg_word_length']
                
                # Simple readability score (lower is more readable)
                readability_score = (avg_sentence_length * 0.39) + (avg_word_length * 11.8) - 15.59
                
                metrics['readability_score'] = readability_score
                metrics['readability_level'] = (
                    'very_easy' if readability_score < 30 else
                    'easy' if readability_score < 50 else
                    'moderate' if readability_score < 70 else
                    'difficult' if readability_score < 90 else
                    'very_difficult'
                )
            
            results.append({
                'text': text,
                'metrics': metrics
            })
        
        # Calculate aggregate statistics
        aggregate_metrics = {
            'avg_word_count': np.mean([r['metrics']['word_count'] for r in results]),
            'avg_sentence_count': np.mean([r['metrics']['sentence_count'] for r in results]),
            'avg_readability_score': np.mean([r['metrics'].get('readability_score', 0) for r in results]),
            'readability_distribution': defaultdict(int)
        }
        
        for result in results:
            if 'readability_level' in result['metrics']:
                aggregate_metrics['readability_distribution'][result['metrics']['readability_level']] += 1
        
        return {
            'total_texts': len(texts),
            'results': results,
            'aggregate_metrics': aggregate_metrics
        } 