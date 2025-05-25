from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PatternDetectionRequest(BaseModel):
    """Schema for pattern detection request."""
    data: List[List[float]] = Field(..., description="Input data array")

class PatternDetectionResponse(BaseModel):
    """Schema for pattern detection response."""
    patterns: List[float] = Field(..., description="Detected patterns")
    features: List[List[float]] = Field(..., description="Extracted features")
    confidence: float = Field(..., description="Confidence score")
    timestamp: datetime = Field(..., description="Timestamp of detection")
    error: Optional[str] = Field(None, description="Error message if detection failed")

class AnomalyDetectionRequest(BaseModel):
    """Schema for anomaly detection request."""
    data: List[List[float]] = Field(..., description="Input data array")

class AnomalyDetectionResponse(BaseModel):
    """Schema for anomaly detection response."""
    anomalies: List[int] = Field(..., description="Detected anomalies (-1 for anomaly, 1 for normal)")
    scores: List[float] = Field(..., description="Anomaly scores")
    features: List[List[float]] = Field(..., description="Extracted features")
    confidence: float = Field(..., description="Confidence score")
    timestamp: datetime = Field(..., description="Timestamp of detection")
    error: Optional[str] = Field(None, description="Error message if detection failed")

class FeatureExtractionRequest(BaseModel):
    """Schema for feature extraction request."""
    data: List[List[float]] = Field(..., description="Input data array")

class FeatureExtractionResponse(BaseModel):
    """Schema for feature extraction response."""
    features: List[List[float]] = Field(..., description="Extracted features")
    feature_dimensions: int = Field(..., description="Number of feature dimensions")
    timestamp: datetime = Field(..., description="Timestamp of extraction")
    error: Optional[str] = Field(None, description="Error message if extraction failed")

class ModelAdaptationRequest(BaseModel):
    """Schema for model adaptation request."""
    new_data: List[List[float]] = Field(..., description="New training data")
    labels: Optional[List[int]] = Field(None, description="Optional labels for supervised learning")

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