from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryAnalysis(BaseModel):
    """Schema for query analysis results."""
    execution_plan: Dict[str, Any] = Field(..., description="Query execution plan")
    statistics: Dict[str, Any] = Field(..., description="Query execution statistics")
    timestamp: str = Field(..., description="Analysis timestamp")
    query_hash: str = Field(..., description="Unique hash of the query")

class OptimizationSuggestion(BaseModel):
    """Schema for query optimization suggestions."""
    type: str = Field(..., description="Type of optimization (index, join, pagination, etc.)")
    description: str = Field(..., description="Description of the suggestion")
    impact: str = Field(..., description="Expected impact of the optimization")
    query: Optional[str] = Field(None, description="Example of optimized query")

class QueryOptimization(BaseModel):
    """Schema for query optimization results."""
    original_query: str = Field(..., description="Original SQL query")
    optimized_query: str = Field(..., description="Optimized SQL query")
    suggestions: List[OptimizationSuggestion] = Field(..., description="List of optimization suggestions")
    improvement: Dict[str, Any] = Field(..., description="Expected performance improvement")
    timestamp: str = Field(..., description="Optimization timestamp")

class QueryPerformance(BaseModel):
    """Schema for query performance statistics."""
    execution_time: float = Field(..., description="Query execution time in seconds")
    plan: Dict[str, Any] = Field(..., description="Query execution plan")
    timestamp: str = Field(..., description="Performance measurement timestamp")
    rows_affected: Optional[int] = Field(None, description="Number of rows affected")
    cache_hits: Optional[int] = Field(None, description="Number of cache hits")
    cache_misses: Optional[int] = Field(None, description="Number of cache misses") 