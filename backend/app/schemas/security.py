from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AuditLogBase(BaseModel):
    """Base schema for audit logs."""
    event_type: str = Field(..., description="Type of event (e.g., 'login', 'data_access')")
    user_id: str = Field(..., description="ID of the user performing the action")
    resource_id: str = Field(..., description="ID of the resource being accessed")
    action: str = Field(..., description="Action performed")
    details: Dict[str, Any] = Field(default={}, description="Additional event details")

class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""
    pass

class AuditLogInDB(AuditLogBase):
    """Schema for audit log entry in database."""
    id: str = Field(..., description="Unique identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    
    class Config:
        orm_mode = True

class AccessControlBase(BaseModel):
    """Base schema for access control rules."""
    user_id: str = Field(..., description="ID of the user")
    resource_id: str = Field(..., description="ID of the resource")
    action: str = Field(..., description="Action being controlled")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")

class AccessControlCreate(AccessControlBase):
    """Schema for creating an access control rule."""
    pass

class AccessControlInDB(AccessControlBase):
    """Schema for access control rule in database."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Whether the rule is active")
    
    class Config:
        orm_mode = True

class EncryptionKeyBase(BaseModel):
    """Base schema for encryption keys."""
    key: str = Field(..., description="Encryption key")
    salt: str = Field(..., description="Salt used for key derivation")

class EncryptionKeyCreate(EncryptionKeyBase):
    """Schema for creating an encryption key."""
    pass

class EncryptionKeyInDB(EncryptionKeyBase):
    """Schema for encryption key in database."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Whether the key is active")
    
    class Config:
        orm_mode = True

class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    start_time: Optional[datetime] = Field(None, description="Start time for filtering")
    end_time: Optional[datetime] = Field(None, description="End time for filtering")
    event_type: Optional[str] = Field(None, description="Event type for filtering")
    user_id: Optional[str] = Field(None, description="User ID for filtering")

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    logs: List[AuditLogInDB] = Field(..., description="List of audit log entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of entries per page")

class AccessControlResponse(BaseModel):
    """Schema for access control response."""
    has_access: bool = Field(..., description="Whether access is granted")
    reason: Optional[str] = Field(None, description="Reason for access decision")
    expires_at: Optional[datetime] = Field(None, description="When access expires")

class EncryptionResponse(BaseModel):
    """Schema for encryption response."""
    encrypted_data: str = Field(..., description="Encrypted data")
    key_id: str = Field(..., description="ID of the encryption key used")
    timestamp: datetime = Field(..., description="Encryption timestamp") 