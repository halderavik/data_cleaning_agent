from typing import List, Dict, Any
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_service import AIService
from app.schemas.ai_model import (
    AIModelCreate,
    AIModelInDB,
    ModelVersionCreate,
    ModelVersionInDB,
    PatternDetectionRequest,
    PatternDetectionResponse,
    EnsemblePredictionRequest,
    EnsemblePredictionResponse,
    ModelAdaptationRequest,
    ModelAdaptationResponse,
    ModelMetricsResponse
)

router = APIRouter()
ai_service = AIService()

@router.post("/detect-patterns", response_model=PatternDetectionResponse)
async def detect_patterns(
    request: PatternDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect patterns in the provided data."""
    try:
        data = np.array(request.data)
        result = await ai_service.detect_patterns(data)
        return PatternDetectionResponse(**result)
    except Exception as e:
        return PatternDetectionResponse(
            patterns=[],
            confidence=0.0,
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.post("/ensemble-predict", response_model=EnsemblePredictionResponse)
async def ensemble_predict(
    request: EnsemblePredictionRequest,
    db: Session = Depends(get_db)
):
    """Make predictions using the ensemble model."""
    try:
        features = np.array(request.features)
        result = await ai_service.ensemble_predict(features)
        return EnsemblePredictionResponse(**result)
    except Exception as e:
        return EnsemblePredictionResponse(
            predictions=[],
            confidence=0.0,
            model_contributions={},
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.post("/adapt", response_model=ModelAdaptationResponse)
async def adapt_model(
    request: ModelAdaptationRequest,
    db: Session = Depends(get_db)
):
    """Adapt models to new data."""
    try:
        new_data = np.array(request.new_data)
        labels = np.array(request.labels)
        result = await ai_service.adapt_to_new_data(new_data, labels)
        return ModelAdaptationResponse(**result)
    except Exception as e:
        return ModelAdaptationResponse(
            status="failed",
            new_version="",
            performance_metrics={},
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.get("/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(
    db: Session = Depends(get_db)
):
    """Get current model performance metrics."""
    try:
        result = await ai_service.get_model_metrics()
        return ModelMetricsResponse(**result)
    except Exception as e:
        return ModelMetricsResponse(
            current_version="unknown",
            metrics={},
            last_updated=datetime.utcnow(),
            error=str(e)
        )

@router.post("/models", response_model=AIModelInDB)
async def create_model(
    model: AIModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI model."""
    try:
        db_model = AIModel(**model.dict())
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models", response_model=List[AIModelInDB])
async def list_models(
    db: Session = Depends(get_db)
):
    """List all AI models."""
    return db.query(AIModel).all()

@router.get("/models/{model_id}", response_model=AIModelInDB)
async def get_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific AI model."""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.get("/models/{model_id}/versions", response_model=List[ModelVersionInDB])
async def list_model_versions(
    model_id: str,
    db: Session = Depends(get_db)
):
    """List all versions of a specific model."""
    versions = db.query(ModelVersion).filter(ModelVersion.model_id == model_id).all()
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found for this model")
    return versions 