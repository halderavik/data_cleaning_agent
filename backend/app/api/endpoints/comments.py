from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentInDB
from app.core.auth import get_current_user
import uuid

router = APIRouter()

@router.post("/{issue_id}/comments", response_model=CommentInDB)
async def create_comment(
    issue_id: str,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new comment."""
    db_comment = Comment(
        id=str(uuid.uuid4()),
        issue_id=issue_id,
        user_id=current_user,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/{issue_id}/comments", response_model=List[CommentInDB])
async def list_comments(
    issue_id: str,
    db: Session = Depends(get_db)
):
    """List all comments for an issue."""
    return db.query(Comment).filter(Comment.issue_id == issue_id).all()

@router.put("/comments/{comment_id}", response_model=CommentInDB)
async def update_comment(
    comment_id: str,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update a comment."""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the comment owner
    if db_comment.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Delete a comment."""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the comment owner
    if db_comment.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted"} 