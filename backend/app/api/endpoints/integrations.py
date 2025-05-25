from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.integration_service import IntegrationService
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationInDB,
    WebhookCreate,
    WebhookUpdate,
    WebhookInDB
)
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/integrations", response_model=IntegrationInDB)
async def create_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new API integration."""
    service = IntegrationService(db)
    return await service.create_integration(
        name=integration.name,
        description=integration.description,
        config=integration.config
    )

@router.get("/integrations", response_model=List[IntegrationInDB])
async def list_integrations(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """List all integrations."""
    service = IntegrationService(db)
    return await service.list_integrations()

@router.get("/integrations/{integration_id}", response_model=IntegrationInDB)
async def get_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get integration by ID."""
    service = IntegrationService(db)
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.put("/integrations/{integration_id}", response_model=IntegrationInDB)
async def update_integration(
    integration_id: str,
    integration: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update integration configuration."""
    service = IntegrationService(db)
    updated = await service.update_integration(integration_id, integration.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Integration not found")
    return updated

@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Delete an integration."""
    service = IntegrationService(db)
    if not await service.delete_integration(integration_id):
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"message": "Integration deleted"}

@router.post("/integrations/{integration_id}/webhooks", response_model=WebhookInDB)
async def create_webhook(
    integration_id: str,
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new webhook for an integration."""
    service = IntegrationService(db)
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return await service.create_webhook(
        integration_id=integration_id,
        url=str(webhook.url),
        events=webhook.events
    )

@router.post("/webhooks/{webhook_id}/trigger")
async def trigger_webhook(
    webhook_id: str,
    event: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Trigger a webhook manually."""
    service = IntegrationService(db)
    webhook = await service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    success = await service.trigger_webhook(webhook, event, payload)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to trigger webhook")
    return {"message": "Webhook triggered successfully"}

@router.post("/webhooks/{webhook_id}/validate")
async def validate_webhook(
    webhook_id: str,
    request: Request,
    x_webhook_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Validate incoming webhook request."""
    service = IntegrationService(db)
    webhook = await service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    payload = await request.json()
    if not service.validate_webhook_signature(x_webhook_signature, payload, webhook.secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    return {"message": "Webhook signature valid"} 