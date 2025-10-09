from pydantic import BaseModel
from datetime import datetime


class ApplicationDocumentBase(BaseModel):
    application_id: int
    file_name: str
    file_url: str
    hash: str


class ApplicationDocumentSchema(ApplicationDocumentBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
