from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rule_validator import RuleValidator
from app.services.rule_tester import RuleTester
from app.services.rule_version_control import RuleVersionControl
from app.schemas.rule import (
    RuleCreate, RuleUpdate, RuleInDB, RuleValidation,
    RuleTestResult, RuleVersionInfo, RuleVersionDetail,
    VersionComparison
)
from app.models.rule import Rule
from app.core.auth import get_current_user
import uuid

router = APIRouter()

@router.post("/", response_model=RuleInDB)
async def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new rule."""
    # Validate rule
    validator = RuleValidator(db)
    validation = validator.validate_rule(rule.dict())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.message)

    # Create rule
    db_rule = Rule(
        id=str(uuid.uuid4()),
        **rule.dict(),
        created_by=current_user,
        updated_by=current_user
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    # Create initial version
    version_control = RuleVersionControl(db)
    version_control.create_version(
        rule=db_rule.__dict__,
        user_id=current_user,
        comment="Initial version"
    )

    return db_rule

@router.get("/", response_model=List[RuleInDB])
async def list_rules(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List all rules with optional filtering."""
    query = db.query(Rule)
    if category:
        query = query.filter(Rule.category == category)
    if is_active is not None:
        query = query.filter(Rule.is_active == is_active)
    return query.offset(skip).limit(limit).all()

@router.get("/{rule_id}", response_model=RuleInDB)
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=RuleInDB)
async def update_rule(
    rule_id: str,
    rule: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update a rule."""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Validate rule
    validator = RuleValidator(db)
    validation = validator.validate_rule(rule.dict())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.message)

    # Update rule
    for key, value in rule.dict().items():
        setattr(db_rule, key, value)
    db_rule.updated_by = current_user
    db.commit()
    db.refresh(db_rule)

    # Create new version
    version_control = RuleVersionControl(db)
    version_control.create_version(
        rule=db_rule.__dict__,
        user_id=current_user,
        comment="Rule updated"
    )

    return db_rule

@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Delete a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}

@router.post("/{rule_id}/validate", response_model=RuleValidation)
async def validate_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """Validate a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    validator = RuleValidator(db)
    return validator.validate_rule(rule.__dict__)

@router.post("/{rule_id}/test", response_model=RuleTestResult)
async def test_rule(
    rule_id: str,
    sample_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Test a rule against sample data."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    tester = RuleTester(db)
    return tester.test_rule(rule.__dict__, sample_size)

@router.get("/{rule_id}/versions", response_model=List[RuleVersionInfo])
async def list_rule_versions(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """List all versions of a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    version_control = RuleVersionControl(db)
    return version_control.get_version_history(rule_id)

@router.get("/{rule_id}/versions/{version_number}", response_model=RuleVersionDetail)
async def get_rule_version(
    rule_id: str,
    version_number: int,
    db: Session = Depends(get_db)
):
    """Get a specific version of a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    version_control = RuleVersionControl(db)
    version = version_control.get_version(rule_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return version

@router.get("/{rule_id}/compare", response_model=VersionComparison)
async def compare_versions(
    rule_id: str,
    version1: int = Query(..., description="First version number"),
    version2: int = Query(..., description="Second version number"),
    db: Session = Depends(get_db)
):
    """Compare two versions of a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    version_control = RuleVersionControl(db)
    try:
        return version_control.compare_versions(rule_id, version1, version2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{rule_id}/rollback/{version_number}", response_model=RuleInDB)
async def rollback_rule(
    rule_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Rollback a rule to a specific version."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    version_control = RuleVersionControl(db)
    try:
        return version_control.rollback_to_version(rule_id, version_number, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 