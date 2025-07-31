from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.database import get_db
from ...models.emoji import Emoji
from ...schemas.emoji import EmojiCreate, EmojiResponse, EmojiUpdate

router = APIRouter(prefix="/emojis", tags=["emojis"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[EmojiResponse])
def get_emojis(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve all emojis with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        active_only: Filter for active emojis only
        db: Database session
        
    Returns:
        List of emoji objects
    """
    query = db.query(Emoji)
    if active_only:
        query = query.filter(Emoji.is_active == True)
    emojis = query.offset(skip).limit(limit).all()
    return emojis

# PUBLIC_INTERFACE
@router.get("/{emoji_id}", response_model=EmojiResponse)
def get_emoji(emoji_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific emoji by ID.
    
    Args:
        emoji_id: Unique identifier for the emoji
        db: Database session
        
    Returns:
        Emoji object
        
    Raises:
        HTTPException: 404 if emoji not found
    """
    emoji = db.query(Emoji).filter(Emoji.id == emoji_id).first()
    if not emoji:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emoji not found"
        )
    return emoji

# PUBLIC_INTERFACE
@router.post("/", response_model=EmojiResponse, status_code=status.HTTP_201_CREATED)
def create_emoji(emoji: EmojiCreate, db: Session = Depends(get_db)):
    """
    Create a new emoji asset.
    
    Args:
        emoji: Emoji creation data
        db: Database session
        
    Returns:
        Created emoji object
        
    Raises:
        HTTPException: 400 if emoji name already exists
    """
    # Check if emoji name already exists
    existing_emoji = db.query(Emoji).filter(Emoji.name == emoji.name).first()
    if existing_emoji:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emoji name already exists"
        )
    
    db_emoji = Emoji(**emoji.dict())
    db.add(db_emoji)
    db.commit()
    db.refresh(db_emoji)
    return db_emoji

# PUBLIC_INTERFACE
@router.put("/{emoji_id}", response_model=EmojiResponse)
def update_emoji(emoji_id: int, emoji_update: EmojiUpdate, db: Session = Depends(get_db)):
    """
    Update an existing emoji.
    
    Args:
        emoji_id: Unique identifier for the emoji
        emoji_update: Updated emoji data
        db: Database session
        
    Returns:
        Updated emoji object
        
    Raises:
        HTTPException: 404 if emoji not found, 400 if name conflict
    """
    db_emoji = db.query(Emoji).filter(Emoji.id == emoji_id).first()
    if not db_emoji:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emoji not found"
        )
    
    # Check for name conflicts if name is being updated
    if emoji_update.name and emoji_update.name != db_emoji.name:
        existing = db.query(Emoji).filter(Emoji.name == emoji_update.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Emoji name already exists"
            )
    
    # Update fields
    update_data = emoji_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_emoji, field, value)
    
    db.commit()
    db.refresh(db_emoji)
    return db_emoji

# PUBLIC_INTERFACE
@router.delete("/{emoji_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emoji(emoji_id: int, db: Session = Depends(get_db)):
    """
    Delete an emoji (soft delete by setting is_active=False).
    
    Args:
        emoji_id: Unique identifier for the emoji
        db: Database session
        
    Raises:
        HTTPException: 404 if emoji not found
    """
    db_emoji = db.query(Emoji).filter(Emoji.id == emoji_id).first()
    if not db_emoji:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emoji not found"
        )
    
    # Soft delete
    db_emoji.is_active = False
    db.commit()
