from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class RuleCondition(BaseModel):
    """Schema for rule conditions."""
    field: str = Field(..., description="Field to check")
    operator: str = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")

class RuleAction(BaseModel):
    """Schema for rule actions."""
    type: str = Field(..., description="Action type")
    value: Optional[Any] = Field(None, description="Action value if applicable")

class RuleBase(BaseModel):
    """Base schema for rules."""
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    category: str = Field(..., description="Rule category")
    severity: str = Field(..., description="Rule severity level")
    conditions: List[RuleCondition] = Field(..., description="Rule conditions")
    actions: List[RuleAction] = Field(..., description="Rule actions")
    is_active: bool = Field(True, description="Whether the rule is active")

class RuleCreate(RuleBase):
    """Schema for creating a rule."""
    pass

class RuleUpdate(RuleBase):
    """Schema for updating a rule."""
    pass

class RuleInDB(RuleBase):
    """Schema for rule in database."""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    class Config:
        orm_mode = True

class RuleVersionInfo(BaseModel):
    """Schema for rule version information."""
    version_number: int = Field(..., description="Version number")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="User who created the version")
    comment: Optional[str] = Field(None, description="Version comment")

class RuleVersionDetail(RuleVersionInfo):
    """Schema for detailed rule version information."""
    rule_data: Dict[str, Any] = Field(..., description="Rule data at this version")

class VersionComparison(BaseModel):
    """Schema for version comparison results."""
    version1: int = Field(..., description="First version number")
    version2: int = Field(..., description="Second version number")
    changes: Dict[str, List[Dict[str, Any]]] = Field(..., description="Changes between versions")
    timestamp: datetime = Field(..., description="Comparison timestamp")

class RuleValidation(BaseModel):
    """Schema for rule validation results."""
    is_valid: bool = Field(..., description="Whether the rule is valid")
    message: str = Field(..., description="Validation message")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="Validation details")

class RuleTestResult(BaseModel):
    """Schema for rule test results."""
    execution_time: float = Field(..., description="Test execution time in seconds")
    matches: int = Field(..., description="Number of matching rows")
    total_rows: int = Field(..., description="Total number of rows tested")
    match_percentage: float = Field(..., description="Percentage of rows that matched")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Any errors encountered")
    sample_results: Optional[List[Dict[str, Any]]] = Field(None, description="Sample of results") 