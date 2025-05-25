from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.reporting_engine import ReportingEngine
from app.services.export_service import ExportService
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ReportTemplate(BaseModel):
    """Schema for custom report template."""
    sections: List[Dict[str, Any]]

@router.get("/projects/{project_id}/quality-scorecard")
async def get_quality_scorecard(
    project_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get quality scorecard for a project."""
    engine = ReportingEngine(db)
    return engine.generate_quality_scorecard(project_id, start_date, end_date)

@router.get("/projects/{project_id}/trends/{metric}")
async def get_trend_report(
    project_id: str,
    metric: str,
    interval: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get trend analysis for a specific metric."""
    engine = ReportingEngine(db)
    return engine.generate_trend_report(project_id, metric, interval, days)

@router.post("/projects/{project_id}/custom-report")
async def generate_custom_report(
    project_id: str,
    template: ReportTemplate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Generate a custom report based on template."""
    engine = ReportingEngine(db)
    return engine.generate_custom_report(project_id, template.dict())

@router.get("/projects/{project_id}/distribution/{dimension}")
async def get_distribution_report(
    project_id: str,
    dimension: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get distribution report for a specific dimension."""
    engine = ReportingEngine(db)
    return engine._generate_distribution_report(project_id, dimension)

@router.post("/projects/{project_id}/export-report")
async def export_report(
    project_id: str,
    data: Dict[str, Any],
    format: str = Query(..., regex="^(csv|json|xlsx|pdf)$"),
    name: str = "report",
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Export report in specified format."""
    export_service = ExportService()
    file_data = export_service.export_report(data, format, name)
    
    # Set appropriate content type
    content_types = {
        'csv': 'text/csv',
        'json': 'application/json',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pdf': 'application/pdf'
    }
    
    return Response(
        content=file_data.getvalue(),
        media_type=content_types[format],
        headers={
            'Content-Disposition': f'attachment; filename="{name}.{format}"'
        }
    ) 