from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.language_service import LanguageService
from app.schemas.language import (
    LanguageCreate,
    LanguageInDB,
    TranslationCreate,
    TranslationInDB,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    TranslationRequest,
    TranslationResponse,
    TextAnalysisRequest,
    SentimentAnalysisResponse,
    TextClassificationRequest,
    TextClassificationResponse
)

router = APIRouter()
language_service = LanguageService()

@router.post("/detect", response_model=LanguageDetectionResponse)
async def detect_language(
    request: LanguageDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect the language of the provided text."""
    try:
        result = await language_service.detect_language(request.text)
        return LanguageDetectionResponse(
            language=result["language"],
            confidence=result["confidence"]
        )
    except Exception as e:
        return LanguageDetectionResponse(
            language="",
            confidence=0.0,
            error=str(e)
        )

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    db: Session = Depends(get_db)
):
    """Translate text to the target language."""
    try:
        result = await language_service.translate_text(
            request.text,
            request.target_language,
            request.source_language
        )
        return TranslationResponse(
            original_text=result["original_text"],
            translated_text=result["translated_text"],
            source_language=result["source_language"],
            target_language=result["target_language"]
        )
    except Exception as e:
        return TranslationResponse(
            original_text=request.text,
            translated_text="",
            source_language=request.source_language or "",
            target_language=request.target_language,
            error=str(e)
        )

@router.post("/analyze/sentiment", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze the sentiment of the provided text."""
    try:
        result = await language_service.analyze_sentiment(
            request.text,
            request.language
        )
        return SentimentAnalysisResponse(
            sentiment=result["sentiment"],
            score=result["score"],
            original_text=request.text
        )
    except Exception as e:
        return SentimentAnalysisResponse(
            sentiment="",
            score=0.0,
            original_text=request.text,
            error=str(e)
        )

@router.post("/analyze/classify", response_model=TextClassificationResponse)
async def classify_text(
    request: TextClassificationRequest,
    db: Session = Depends(get_db)
):
    """Classify the provided text into categories."""
    try:
        result = await language_service.classify_text(
            request.text,
            request.categories,
            request.language
        )
        return TextClassificationResponse(
            text=request.text,
            labels=result["labels"],
            scores=result["scores"]
        )
    except Exception as e:
        return TextClassificationResponse(
            text=request.text,
            labels=[],
            scores=[],
            error=str(e)
        )

@router.get("/supported", response_model=List[LanguageInDB])
async def get_supported_languages(
    db: Session = Depends(get_db)
):
    """Get list of supported languages."""
    return await language_service.get_supported_languages(db)

@router.post("/supported", response_model=LanguageInDB)
async def add_supported_language(
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    """Add a new supported language."""
    return await language_service.add_supported_language(db, language) 