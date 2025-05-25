from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from app.models.language import Language, Translation
from app.core.config import settings
from transformers import pipeline
from langdetect import detect, DetectorFactory
from googletrans import Translator

class LanguageService:
    """Service for handling multi-language support and text analysis."""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)
        self.translator = Translator()
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.text_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        # Initialize language detector with seed for reproducibility
        DetectorFactory.seed = 0

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Dict containing language code and confidence
        """
        try:
            language = detect(text)
            return {
                "language": language,
                "confidence": 1.0  # langdetect doesn't provide confidence scores
            }
        except Exception as e:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }

    async def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Optional source language code
            
        Returns:
            Dict containing translated text and metadata
        """
        try:
            result = self.translator.translate(
                text,
                dest=target_language,
                src=source_language
            )
            
            # Store translation in database
            translation = Translation(
                original_text=text,
                translated_text=result.text,
                source_language=result.src,
                target_language=result.dest,
                created_at=datetime.utcnow()
            )
            self.db.add(translation)
            self.db.commit()
            
            return {
                "original_text": text,
                "translated_text": result.text,
                "source_language": result.src,
                "target_language": result.dest
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_text": text,
                "translated_text": None
            }

    async def analyze_sentiment(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            language: Optional language code
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            # Translate to English if not already in English
            if language and language != "en":
                translation = await self.translate_text(text, "en", language)
                text = translation["translated_text"]
            
            result = self.sentiment_analyzer(text)[0]
            return {
                "sentiment": result["label"],
                "score": result["score"],
                "original_text": text
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_text": text,
                "sentiment": None
            }

    async def classify_text(self, text: str, categories: List[str], language: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify text into given categories.
        
        Args:
            text: Text to classify
            categories: List of possible categories
            language: Optional language code
            
        Returns:
            Dict containing classification results
        """
        try:
            # Translate to English if not already in English
            if language and language != "en":
                translation = await self.translate_text(text, "en", language)
                text = translation["translated_text"]
            
            result = self.text_classifier(text, categories)
            return {
                "text": text,
                "labels": result["labels"],
                "scores": result["scores"]
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": text,
                "labels": None
            }

    async def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported languages."""
        return [
            {"code": lang.code, "name": lang.name, "native_name": lang.native_name}
            for lang in self.db.query(Language).all()
        ]

    async def add_supported_language(self, code: str, name: str, native_name: str) -> Language:
        """Add a new supported language."""
        language = Language(
            code=code,
            name=name,
            native_name=native_name,
            created_at=datetime.utcnow()
        )
        self.db.add(language)
        self.db.commit()
        self.db.refresh(language)
        return language 