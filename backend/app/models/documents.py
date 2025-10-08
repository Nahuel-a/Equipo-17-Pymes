from core.database import Base
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime


  
    # Assuming external model for Application (minimal stub)
class Application(Base):
    __tablename__ = 'applications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
      # Other fields...
      # documents = relationship("ApplicationDocument", back_populates="application")  # Uncomment if using back_populates
  
    # Model for application_documents
class ApplicationDocument(Base):
    __tablename__ = 'application_documents'
      
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)  # e.g., S3 URL or local path
    hash = Column(String(64), nullable=False)  # e.g., SHA256 hash for integrity
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
      
      # Relationship (optional)
    application = relationship("Application", back_populates="documents")
  