from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.security_service import SecurityService
from app.schemas.security import (
    AuditLogCreate,
    AuditLogInDB,
    AuditLogFilter,
    AuditLogResponse,
    AccessControlCreate,
    AccessControlInDB,
    AccessControlResponse,
    EncryptionResponse
)

router = APIRouter()
security_service = SecurityService()

@router.post("/encrypt", response_model=EncryptionResponse)
async def encrypt_data(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Encrypt sensitive data."""
    try:
        encrypted_data = await security_service.encrypt_data(data)
        return EncryptionResponse(
            encrypted_data=encrypted_data,
            key_id=security_service.encryption_key.decode(),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt")
async def decrypt_data(
    encrypted_data: str,
    db: Session = Depends(get_db)
):
    """Decrypt encrypted data."""
    try:
        decrypted_data = await security_service.decrypt_data(encrypted_data)
        return decrypted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit-logs", response_model=AuditLogInDB)
async def create_audit_log(
    log: AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit log entry."""
    try:
        await security_service.log_audit_event(
            event_type=log.event_type,
            user_id=log.user_id,
            resource_id=log.resource_id,
            action=log.action,
            details=log.details
        )
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    filter_params: AuditLogFilter = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering."""
    try:
        logs = await security_service.get_audit_logs(
            start_time=filter_params.start_time,
            end_time=filter_params.end_time,
            event_type=filter_params.event_type,
            user_id=filter_params.user_id
        )
        
        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_logs = logs[start_idx:end_idx]
        
        return AuditLogResponse(
            logs=paginated_logs,
            total=len(logs),
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/access-control", response_model=AccessControlInDB)
async def create_access_control(
    access_control: AccessControlCreate,
    db: Session = Depends(get_db)
):
    """Create a new access control rule."""
    try:
        # Implementation will be added when we create the access control service
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/access-control/check", response_model=AccessControlResponse)
async def check_access(
    user_id: str,
    resource_id: str,
    action: str,
    db: Session = Depends(get_db)
):
    """Check if a user has access to a resource."""
    try:
        has_access = await security_service.check_access(
            user_id=user_id,
            resource_id=resource_id,
            action=action
        )
        return AccessControlResponse(
            has_access=has_access,
            reason="Access granted" if has_access else "Access denied",
            expires_at=None  # Will be implemented with access control service
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/encryption-key/rotate")
async def rotate_encryption_key(
    db: Session = Depends(get_db)
):
    """Rotate the encryption key."""
    try:
        await security_service.rotate_encryption_key()
        return {"message": "Encryption key rotated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 