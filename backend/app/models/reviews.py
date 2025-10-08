from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

# Assuming external models for Application and Operator (minimal stubs)
class Application(Base):
    __tablename__ = 'applications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Other fields...

class Operator(Base):
    __tablename__ = 'operators'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Other fields...

# Model for application_reviews
class ApplicationReview(Base):
    __tablename__ = 'application_reviews'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    operator_id = Column(UUID(as_uuid=True), ForeignKey('operators.id'), nullable=False)
    decision = Column(String(255), nullable=False)  # e.g., 'approved', 'rejected'
    comments = Column(Text)  # Optional long text
    reviewed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships (optional, for querying)
    application = relationship("Application", back_populates="reviews")
    operator = relationship("Operator")

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

# In your main app, add back_populates to external models if needed:
# Application.reviews = relationship("ApplicationReview", back_populates="application")
# Application.documents = relationship("ApplicationDocument", back_populates="application")
