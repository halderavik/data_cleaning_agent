from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class LanguageBase(BaseModel):
    """Base schema for languages."""
    code: str = Field(..., description="ISO 639-1 language code")
    name: str = Field(..., description="Language name in English")
    native_name: str = Field(..., description="Language name in its native script")

class LanguageCreate(LanguageBase):
    """Schema for creating a language."""
    pass

class LanguageInDB(LanguageBase):
    """Schema for language in database."""
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TranslationBase(BaseModel):
    """Base schema for translations."""
    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")

class TranslationCreate(TranslationBase):
    """Schema for creating a translation."""
    pass

class TranslationInDB(TranslationBase):
    """Schema for translation in database."""
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class LanguageDetectionRequest(BaseModel):
    """Schema for language detection request."""
    text: str = Field(..., description="Text to detect language for")

class LanguageDetectionResponse(BaseModel):
    """Schema for language detection response."""
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score")
    error: Optional[str] = Field(None, description="Error message if detection failed")

class TranslationRequest(BaseModel):
    """Schema for translation request."""
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code")
    source_language: Optional[str] = Field(None, description="Source language code (optional)")

class TranslationResponse(BaseModel):
    """Schema for translation response."""
    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")
    error: Optional[str] = Field(None, description="Error message if translation failed")

class TextAnalysisRequest(BaseModel):
    """Schema for text analysis request."""
    text: str = Field(..., description="Text to analyze")
    language: Optional[str] = Field(None, description="Language code (optional)")

class SentimentAnalysisResponse(BaseModel):
    """Schema for sentiment analysis response."""
    sentiment: str = Field(..., description="Sentiment label")
    score: float = Field(..., description="Confidence score")
    original_text: str = Field(..., description="Original text")
    error: Optional[str] = Field(None, description="Error message if analysis failed")

class TextClassificationRequest(BaseModel):
    """Schema for text classification request."""
    text: str = Field(..., description="Text to classify")
    categories: List[str] = Field(..., description="List of possible categories")
    language: Optional[str] = Field(None, description="Language code (optional)")

class TextClassificationResponse(BaseModel):
    """Schema for text classification response."""
    text: str = Field(..., description="Analyzed text")
    labels: List[str] = Field(..., description="Category labels")
    scores: List[float] = Field(..., description="Confidence scores")
    error: Optional[str] = Field(None, description="Error message if classification failed") 