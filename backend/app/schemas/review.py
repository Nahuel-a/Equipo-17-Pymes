from pydantic import BaseModel
from models.enums import StatusCredit
from uuid import UUID
from datetime import datetime
from typing import Optional

class ReviewBase(BaseModel): 
    # review_comments: Optional[str] = None
    pass

class ReviewCreate(ReviewBase):
    credits_id: UUID

class ReviewUpdate(BaseModel):
    decision: Optional[str] = None  
    review_comments: Optional[str] = None

class ReviewSchema(ReviewBase):
    id: UUID
    reviewer_id: UUID
    credits_id: UUID
    review_comments: Optional[str] = None
    decision: Optional[str] = None  
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewDecision(BaseModel):
    """Schema for making a review decision - uses enum but stores as string"""
    decision: StatusCredit
    review_comments: Optional[str] = None