from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SystemMetricsBase(BaseModel):
    """Base schema for system metrics."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used: int = Field(..., description="Memory used in bytes")
    memory_total: int = Field(..., description="Total memory in bytes")
    disk_percent: float = Field(..., description="Disk usage percentage")
    disk_used: int = Field(..., description="Disk space used in bytes")
    disk_total: int = Field(..., description="Total disk space in bytes")
    timestamp: datetime = Field(..., description="Timestamp of the metrics")

class SystemMetricsCreate(SystemMetricsBase):
    """Schema for creating system metrics."""
    pass

class SystemMetricsInDB(SystemMetricsBase):
    """Schema for system metrics in database."""
    id: str

    class Config:
        orm_mode = True

class PerformanceMetricBase(BaseModel):
    """Base schema for performance metrics."""
    endpoint: str = Field(..., description="API endpoint path")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: datetime = Field(..., description="Timestamp of the metric")

class PerformanceMetricCreate(PerformanceMetricBase):
    """Schema for creating performance metrics."""
    pass

class PerformanceMetricInDB(PerformanceMetricBase):
    """Schema for performance metrics in database."""
    id: str

    class Config:
        orm_mode = True

class PerformanceAnalysisResponse(BaseModel):
    """Schema for performance analysis response."""
    system_metrics: Dict[str, Dict[str, float]] = Field(..., description="System resource metrics")
    endpoint_metrics: List[Dict[str, Any]] = Field(..., description="Endpoint performance metrics")
    issues: List[str] = Field(..., description="Detected performance issues")
    timestamp: datetime = Field(..., description="Timestamp of the analysis")
    error: Optional[str] = Field(None, description="Error message if analysis failed")

class DatabaseOptimizationResponse(BaseModel):
    """Schema for database optimization response."""
    status: str = Field(..., description="Success or failure status")
    index_statistics: List[Dict[str, Any]] = Field(..., description="Index usage statistics")
    timestamp: datetime = Field(..., description="Timestamp of the optimization")
    error: Optional[str] = Field(None, description="Error message if optimization failed")

class PerformanceRecommendation(BaseModel):
    """Schema for performance recommendations."""
    type: str = Field(..., description="Type of recommendation (system/endpoint)")
    component: str = Field(..., description="Component being recommended for")
    issue: str = Field(..., description="Performance issue detected")
    recommendation: str = Field(..., description="Recommended action")

class PerformanceRecommendationsResponse(BaseModel):
    """Schema for performance recommendations response."""
    recommendations: List[PerformanceRecommendation] = Field(..., description="List of recommendations")
    timestamp: datetime = Field(..., description="Timestamp of the recommendations")
    error: Optional[str] = Field(None, description="Error message if recommendations failed") 