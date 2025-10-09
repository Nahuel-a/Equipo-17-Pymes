from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ApplicationReviewBase(BaseModel):
    application_id: int
    operator_id: str
    decision: str
    comments: Optional[str] = None


class ApplicationReviewSchema(ApplicationReviewBase):
    id: int
    reviewed_at: datetime

    class Config:
        from_attributes = True
