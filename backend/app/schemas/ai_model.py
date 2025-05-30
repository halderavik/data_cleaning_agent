from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AIModelBase(BaseModel):
    """Base schema for AI models, supporting local and external providers (e.g., DeepSeek, OpenAI)."""
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    model_type: str = Field(..., description="Type of model (ensemble, pattern_detector, etc.)")
    provider: str = Field('local', description="Model provider (e.g., 'local', 'deepseek', 'openai')")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Model configuration and hyperparameters. "
            "For DeepSeek, example: { 'api_key': 'sk-...', 'base_url': 'https://api.deepseek.com', 'model': 'deepseek-chat' }"
        )
    )

class AIModelCreate(AIModelBase):
    """Schema for creating an AI model."""
    pass

class AIModelUpdate(AIModelBase):
    """Schema for updating an AI model."""
    pass

class AIModelInDB(AIModelBase):
    """Schema for AI model in database."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ModelVersionBase(BaseModel):
    """Base schema for model versions."""
    version: str = Field(..., description="Semantic version")
    model_type: str = Field(..., description="Type of model")
    performance_metrics: Dict[str, Any] = Field(..., description="Model performance metrics")

class ModelVersionCreate(ModelVersionBase):
    """Schema for creating a model version."""
    model_id: str = Field(..., description="ID of the parent model")

class ModelVersionInDB(ModelVersionBase):
    """Schema for model version in database."""
    id: str
    model_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class PatternDetectionRequest(BaseModel):
    """Schema for pattern detection request."""
    data: List[List[float]] = Field(..., description="Input data array")

class PatternDetectionResponse(BaseModel):
    """Schema for pattern detection response."""
    patterns: List[float] = Field(..., description="Detected patterns")
    confidence: float = Field(..., description="Confidence score")
    timestamp: datetime = Field(..., description="Timestamp of detection")
    error: Optional[str] = Field(None, description="Error message if detection failed")

class EnsemblePredictionRequest(BaseModel):
    """Schema for ensemble prediction request."""
    features: List[List[float]] = Field(..., description="Input features array")

class EnsemblePredictionResponse(BaseModel):
    """Schema for ensemble prediction response."""
    predictions: List[List[float]] = Field(..., description="Model predictions")
    confidence: float = Field(..., description="Confidence score")
    model_contributions: Dict[str, float] = Field(..., description="Contribution of each model")
    timestamp: datetime = Field(..., description="Timestamp of prediction")
    error: Optional[str] = Field(None, description="Error message if prediction failed")

class ModelAdaptationRequest(BaseModel):
    """Schema for model adaptation request."""
    new_data: List[List[float]] = Field(..., description="New training data")
    labels: List[int] = Field(..., description="Corresponding labels")

class ModelAdaptationResponse(BaseModel):
    """Schema for model adaptation response."""
    status: str = Field(..., description="Success or failure status")
    new_version: str = Field(..., description="New model version")
    performance_metrics: Dict[str, Any] = Field(..., description="Updated performance metrics")
    timestamp: datetime = Field(..., description="Timestamp of adaptation")
    error: Optional[str] = Field(None, description="Error message if adaptation failed")

class ModelMetricsResponse(BaseModel):
    """Schema for model metrics response."""
    current_version: str = Field(..., description="Current model version")
    metrics: Dict[str, Any] = Field(..., description="Current performance metrics")
    last_updated: datetime = Field(..., description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if retrieval failed") 