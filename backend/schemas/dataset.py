from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class DatasetBase(BaseModel):
    """Base schema for dataset data."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    file_type: str = Field(..., regex="^(spss|csv|excel|json)$")

class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset."""
    project_id: UUID

class DatasetUpdate(BaseModel):
    """Schema for updating a dataset."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class DatasetInDB(DatasetBase):
    """Schema for dataset data as stored in database."""
    id: UUID
    project_id: UUID
    file_path: str
    file_size: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 