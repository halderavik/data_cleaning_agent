from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class IntegrationBase(BaseModel):
    """Base schema for integrations."""
    name: str = Field(..., description="Name of the integration")
    integration_type: str = Field(..., description="Type of integration (e.g., 'api', 'webhook')")
    config: Dict[str, Any] = Field(..., description="Integration configuration")

class IntegrationCreate(IntegrationBase):
    """Schema for creating an integration."""
    pass

class IntegrationUpdate(BaseModel):
    """Schema for updating an integration."""
    config: Dict[str, Any] = Field(..., description="New integration configuration")

class IntegrationInDB(IntegrationBase):
    """Schema for integration in database."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        orm_mode = True

class IntegrationLogBase(BaseModel):
    """Base schema for integration logs."""
    integration_id: str = Field(..., description="ID of the integration")
    request_method: str = Field(..., description="HTTP method used")
    request_url: str = Field(..., description="Request URL")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    response_status: int = Field(..., description="HTTP response status code")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class IntegrationLogInDB(IntegrationLogBase):
    """Schema for integration log in database."""
    id: str = Field(..., description="Unique identifier")
    timestamp: datetime = Field(..., description="Log timestamp")
    
    class Config:
        orm_mode = True

class IntegrationLogFilter(BaseModel):
    """Schema for filtering integration logs."""
    start_time: Optional[datetime] = Field(None, description="Start time for filtering")
    end_time: Optional[datetime] = Field(None, description="End time for filtering")

class IntegrationLogResponse(BaseModel):
    """Schema for integration log response."""
    logs: List[IntegrationLogInDB] = Field(..., description="List of integration logs")
    total: int = Field(..., description="Total number of logs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of logs per page")

class ApiRequest(BaseModel):
    """Schema for making API requests."""
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")
    endpoint: str = Field(..., description="API endpoint")
    data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")

class ApiResponse(BaseModel):
    """Schema for API responses."""
    data: Dict[str, Any] = Field(..., description="Response data")
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(..., description="Response headers")

class WebhookBase(BaseModel):
    """Base schema for webhooks."""
    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="List of events to trigger webhook")

class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass

class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[HttpUrl] = Field(None, description="Webhook URL")
    events: Optional[List[str]] = Field(None, description="List of events to trigger webhook")

class WebhookInDB(WebhookBase):
    """Schema for webhook in database."""
    id: str
    integration_id: str
    secret: str
    last_triggered: Optional[datetime]
    last_status: Optional[int]
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 