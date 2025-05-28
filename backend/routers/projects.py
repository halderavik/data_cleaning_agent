from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.base import get_db
from backend.models import User, Project
from backend.schemas import ProjectCreate, ProjectUpdate, ProjectInDB
from backend.security import get_current_active_user

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ProjectInDB)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new project.
    
    Args:
        project (ProjectCreate): Project data
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        ProjectInDB: Created project
    """
    db_project = Project(
        **project.dict(),
        owner_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectInDB])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of projects.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        List[ProjectInDB]: List of projects
    """
    projects = db.query(Project).filter(
        Project.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectInDB)
async def read_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get project by ID.
    
    Args:
        project_id (str): Project ID
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        ProjectInDB: Project information
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return project

@router.put("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update project information.
    
    Args:
        project_id (str): Project ID
        project_update (ProjectUpdate): Updated project data
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        ProjectInDB: Updated project information
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in project_update.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a project.
    
    Args:
        project_id (str): Project ID
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(project)
    db.commit() 