from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ApplicationDocumentBase(BaseModel):
    application_id: UUID
    file_name: str
    file_url: str
    hash: str


class ApplicationDocumentSchema(ApplicationDocumentBase):
    id: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True
