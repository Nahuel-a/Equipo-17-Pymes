from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ApplicationReviewBase(BaseModel):
    application_id: UUID
    operator_id: UUID
    decision: str
    comments: Optional[str] = None


class ApplicationReviewSchema(ApplicationReviewBase):
    id: UUID
    reviewed_at: datetime

    class Config:
        from_attributes = True
