from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

from backend.database.base import get_db
from backend.models import DataFile, CleaningResult, CleaningCheck, User
from backend.schemas import CleaningResultBase, CleaningResultUpdate
from backend.cleaning_engine import CleaningEngine
from backend.security import get_current_user

router = APIRouter(prefix="/api/v1/cleaning", tags=["cleaning"])

class CleaningConfig(BaseModel):
    """Configuration for cleaning checks."""
    required_fields: Optional[list[str]] = None
    expected_types: Optional[Dict[str, str]] = None
    consistency_rules: Optional[list[Dict[str, Any]]] = None
    format_rules: Optional[Dict[str, str]] = None
    section_fields: Optional[Dict[str, list[str]]] = None

class CleaningRequest(BaseModel):
    """Request model for cleaning operation."""
    data: Dict[str, Any]  # DataFrame serialized as dict
    config: Optional[CleaningConfig] = None

class CleaningResponse(BaseModel):
    """Response model for cleaning operation."""
    summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    documentation: Dict[str, Any]

@router.post("/process", response_model=CleaningResponse)
async def process_data(
    request: CleaningRequest,
    current_user: User = Depends(get_current_user)
) -> CleaningResponse:
    """
    Process data through the cleaning engine.
    
    Args:
        request (CleaningRequest): The cleaning request containing data and config
        current_user (User): The authenticated user
        
    Returns:
        CleaningResponse: Results of the cleaning operation
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Initialize cleaning engine with config
        engine = CleaningEngine(request.config.dict() if request.config else None)
        
        # Process data
        results = engine.process_data(df)
        
        # Get documentation
        docs = engine.get_check_documentation()
        
        return CleaningResponse(
            summary=results['summary'],
            detailed_results=results['detailed_results'],
            documentation=docs
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data: {str(e)}"
        )

@router.get("/documentation")
async def get_documentation(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get documentation for all cleaning checks.
    
    Args:
        current_user (User): The authenticated user
        
    Returns:
        Dict[str, Any]: Documentation for all checks
    """
    try:
        engine = CleaningEngine()
        return engine.get_check_documentation()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting documentation: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance metrics for cleaning checks.
    
    Args:
        current_user (User): The authenticated user
        
    Returns:
        Dict[str, Any]: Performance metrics
    """
    try:
        engine = CleaningEngine()
        return {
            'check_times': engine.check_times,
            'total_execution_time': engine.total_execution_time
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting performance metrics: {str(e)}"
        )

@router.post("/{data_file_id}/clean", response_model=Dict[str, Any])
async def clean_data_file(
    data_file_id: str,
    config: Dict[str, Any] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Clean a data file using the cleaning engine.
    
    Args:
        data_file_id (str): ID of the data file to clean
        config (Dict[str, Any], optional): Configuration for cleaning checks
        db (Session): Database session
        current_user: Current authenticated user
    
    Returns:
        Dict[str, Any]: Results of the cleaning process
    """
    # Get data file
    data_file = db.query(DataFile).filter(DataFile.id == data_file_id).first()
    if not data_file:
        raise HTTPException(status_code=404, detail="Data file not found")
    
    # Initialize cleaning engine
    cleaning_engine = CleaningEngine(config)
    
    try:
        # Read data file
        if data_file.file_type == 'sav':
            import pyreadstat
            df, meta = pyreadstat.read_sav(data_file.file_path)
        else:
            df = pd.read_csv(data_file.file_path)
        
        # Process data through cleaning engine
        results = cleaning_engine.process_data(df)
        
        # Save cleaning results
        for check_name, check_result in results.items():
            cleaning_check = db.query(CleaningCheck).filter(
                CleaningCheck.name == check_name
            ).first()
            
            if not cleaning_check:
                cleaning_check = CleaningCheck(
                    name=check_name,
                    description=cleaning_engine.checks[check_name]['description'],
                    category=cleaning_engine.checks[check_name]['category']
                )
                db.add(cleaning_check)
                db.flush()
            
            cleaning_result = CleaningResult(
                project_id=data_file.project_id,
                data_file_id=data_file.id,
                check_id=cleaning_check.id,
                status=check_result['status'],
                issues_found=check_result['issues_found'],
                details=check_result.get('details', {}),
                completed_at=datetime.utcnow()
            )
            db.add(cleaning_result)
        
        db.commit()
        
        return {
            'status': 'success',
            'data_file_id': data_file_id,
            'results': results
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{data_file_id}/results", response_model=Dict[str, Any])
async def get_cleaning_results(
    data_file_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get cleaning results for a data file.
    
    Args:
        data_file_id (str): ID of the data file
        db (Session): Database session
        current_user: Current authenticated user
    
    Returns:
        Dict[str, Any]: Cleaning results
    """
    # Get data file
    data_file = db.query(DataFile).filter(DataFile.id == data_file_id).first()
    if not data_file:
        raise HTTPException(status_code=404, detail="Data file not found")
    
    # Get cleaning results
    results = db.query(CleaningResult).filter(
        CleaningResult.data_file_id == data_file_id
    ).all()
    
    return {
        'data_file_id': data_file_id,
        'results': [
            {
                'check_name': result.check.name,
                'status': result.status,
                'issues_found': result.issues_found,
                'details': result.details,
                'completed_at': result.completed_at
            }
            for result in results
        ]
    } 