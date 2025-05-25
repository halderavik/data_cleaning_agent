from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.services.query_optimizer import QueryOptimizer
from app.db.session import get_db
from app.schemas.query import QueryAnalysis, QueryOptimization, QueryPerformance

router = APIRouter()

@router.post("/analyze", response_model=QueryAnalysis)
async def analyze_query(
    query: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze a SQL query and return its execution plan and statistics.
    """
    try:
        optimizer = QueryOptimizer(db)
        analysis = optimizer.analyze_query(query)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/optimize", response_model=QueryOptimization)
async def optimize_query(
    query: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Optimize a SQL query and return suggestions for improvement.
    """
    try:
        optimizer = QueryOptimizer(db)
        optimization = optimizer.optimize_query(query)
        return optimization
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/performance/{query_hash}", response_model=QueryPerformance)
async def get_query_performance(
    query_hash: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get performance statistics for a specific query.
    """
    try:
        optimizer = QueryOptimizer(db)
        performance = optimizer.get_query_performance(query_hash)
        return performance
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 