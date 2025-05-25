from typing import List, Dict, Any
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.advanced_ai_service import AdvancedAIService
from app.schemas.advanced_ai import (
    PatternDetectionRequest,
    PatternDetectionResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    FeatureExtractionRequest,
    FeatureExtractionResponse,
    ModelAdaptationRequest,
    ModelAdaptationResponse,
    ModelMetricsResponse
)

router = APIRouter()
advanced_ai_service = AdvancedAIService()

@router.post("/detect-patterns", response_model=PatternDetectionResponse)
async def detect_patterns(
    request: PatternDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect patterns in the provided data."""
    try:
        data = np.array(request.data)
        result = await advanced_ai_service.detect_patterns(data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return PatternDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect anomalies in the provided data."""
    try:
        data = np.array(request.data)
        result = await advanced_ai_service.detect_anomalies(data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return AnomalyDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-features", response_model=FeatureExtractionResponse)
async def extract_features(
    request: FeatureExtractionRequest,
    db: Session = Depends(get_db)
):
    """Extract features from the provided data."""
    try:
        data = np.array(request.data)
        result = await advanced_ai_service.extract_features(data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return FeatureExtractionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt", response_model=ModelAdaptationResponse)
async def adapt_model(
    request: ModelAdaptationRequest,
    db: Session = Depends(get_db)
):
    """Adapt models to new data."""
    try:
        new_data = np.array(request.new_data)
        labels = np.array(request.labels) if request.labels else None
        result = await advanced_ai_service.adapt_to_new_data(new_data, labels)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return ModelAdaptationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(
    db: Session = Depends(get_db)
):
    """Get current model performance metrics."""
    try:
        result = await advanced_ai_service.get_model_metrics()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return ModelMetricsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 