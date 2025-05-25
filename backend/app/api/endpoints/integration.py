from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.integration_service import IntegrationService
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationInDB,
    IntegrationLogFilter,
    IntegrationLogResponse,
    ApiRequest,
    ApiResponse
)

router = APIRouter()
integration_service = IntegrationService()

@router.post("/", response_model=IntegrationInDB)
async def create_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db)
):
    """Create a new integration."""
    try:
        return await integration_service.create_integration(
            name=integration.name,
            integration_type=integration.integration_type,
            config=integration.config,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{integration_id}", response_model=IntegrationInDB)
async def get_integration(
    integration_id: str,
    db: Session = Depends(get_db)
):
    """Get an integration by ID."""
    try:
        integration = await integration_service.get_integration(integration_id, db)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return integration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{integration_id}", response_model=IntegrationInDB)
async def update_integration(
    integration_id: str,
    integration: IntegrationUpdate,
    db: Session = Depends(get_db)
):
    """Update an integration's configuration."""
    try:
        updated = await integration_service.update_integration(
            integration_id=integration_id,
            config=integration.config,
            db=db
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Integration not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    db: Session = Depends(get_db)
):
    """Delete an integration."""
    try:
        deleted = await integration_service.delete_integration(integration_id, db)
        if not deleted:
            raise HTTPException(status_code=404, detail="Integration not found")
        return {"message": "Integration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{integration_id}/request", response_model=ApiResponse)
async def make_api_request(
    integration_id: str,
    request: ApiRequest,
    db: Session = Depends(get_db)
):
    """Make an API request using an integration."""
    try:
        integration = await integration_service.get_integration(integration_id, db)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        response = await integration_service.make_api_request(
            integration=integration,
            method=request.method,
            endpoint=request.endpoint,
            data=request.data,
            headers=request.headers
        )
        
        return ApiResponse(
            data=response,
            status_code=200,
            headers={}  # Add actual response headers if needed
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{integration_id}/logs", response_model=IntegrationLogResponse)
async def get_integration_logs(
    integration_id: str,
    filter_params: IntegrationLogFilter = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get logs for an integration."""
    try:
        logs = await integration_service.get_integration_logs(
            integration_id=integration_id,
            start_time=filter_params.start_time,
            end_time=filter_params.end_time,
            db=db
        )
        
        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_logs = logs[start_idx:end_idx]
        
        return IntegrationLogResponse(
            logs=paginated_logs,
            total=len(logs),
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 