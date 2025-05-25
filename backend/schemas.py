from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "analyst"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: UUID4
    owner_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Data file schemas
class DataFileBase(BaseModel):
    original_filename: str
    file_type: Optional[str] = None

class DataFileCreate(DataFileBase):
    project_id: UUID4

class DataFileUpdate(BaseModel):
    upload_status: Optional[str] = None

class DataFileInDB(DataFileBase):
    id: UUID4
    project_id: UUID4
    file_size: Optional[int] = None
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Cleaning check schemas
class CleaningCheckBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_standard: bool = True
    check_function: Optional[str] = None

class CleaningCheckCreate(CleaningCheckBase):
    pass

class CleaningCheckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_standard: Optional[bool] = None
    check_function: Optional[str] = None

class CleaningCheckInDB(CleaningCheckBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# Cleaning result schemas
class CleaningResultBase(BaseModel):
    project_id: UUID4
    data_file_id: UUID4
    check_id: UUID4
    status: str = "pending"
    issues_found: int = 0
    details: Optional[Dict[str, Any]] = None

class CleaningResultCreate(CleaningResultBase):
    pass

class CleaningResultUpdate(BaseModel):
    status: Optional[str] = None
    issues_found: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

class CleaningResultInDB(CleaningResultBase):
    id: UUID4
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response schemas
class ResponseBase(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(ResponseBase):
    status: str = "error"
    error_code: str
    details: Optional[Dict[str, Any]] = None

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID4] = None 