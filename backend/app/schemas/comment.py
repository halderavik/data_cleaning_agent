from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    """Base schema for comments."""
    content: str = Field(..., description="Comment content")

class CommentCreate(CommentBase):
    """Schema for creating a comment."""
    pass

class CommentUpdate(CommentBase):
    """Schema for updating a comment."""
    pass

class CommentInDB(CommentBase):
    """Schema for comment in database."""
    id: str
    issue_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 