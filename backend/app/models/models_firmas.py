from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from datetime import timezone
from .models import BaseModel


class DigitalSignature(BaseModel):
    __tablename__ = 'digital_signatures'
    id = Column(Integer, primary_key=True)
    signature = Column(String)  # Stores the signature as an encoded string (e.g. base64)
    signature_date = Column(DateTime, default=datetime.now(timezone.utc))  # UTC timestamp when signed
    document_id = Column(Integer, ForeignKey('documents.id'))  # FK to the documents table