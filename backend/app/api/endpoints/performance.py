from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.performance_service import PerformanceService
from app.schemas.performance import (
    SystemMetricsInDB,
    PerformanceMetricInDB,
    PerformanceAnalysisResponse,
    DatabaseOptimizationResponse,
    PerformanceRecommendationsResponse
)

router = APIRouter()
performance_service = PerformanceService()

@router.get("/metrics/system", response_model=SystemMetricsInDB)
async def get_system_metrics(
    db: Session = Depends(get_db)
):
    """Get current system resource metrics."""
    try:
        metrics = await performance_service.collect_system_metrics()
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/endpoints", response_model=List[PerformanceMetricInDB])
async def get_endpoint_metrics(
    time_range: timedelta = timedelta(hours=1),
    db: Session = Depends(get_db)
):
    """Get endpoint performance metrics for a time range."""
    try:
        analysis = await performance_service.analyze_performance(time_range)
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        return analysis["endpoint_metrics"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis", response_model=PerformanceAnalysisResponse)
async def analyze_performance(
    time_range: timedelta = timedelta(hours=1),
    db: Session = Depends(get_db)
):
    """Analyze system performance over a time range."""
    try:
        analysis = await performance_service.analyze_performance(time_range)
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/database", response_model=DatabaseOptimizationResponse)
async def optimize_database(
    db: Session = Depends(get_db)
):
    """Perform database optimization tasks."""
    try:
        result = await performance_service.optimize_database()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations", response_model=PerformanceRecommendationsResponse)
async def get_performance_recommendations(
    db: Session = Depends(get_db)
):
    """Get performance optimization recommendations."""
    try:
        recommendations = await performance_service.get_performance_recommendations()
        if "error" in recommendations:
            raise HTTPException(status_code=500, detail=recommendations["error"])
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 