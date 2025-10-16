from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from app.models.models import BaseModel
from datetime import datetime


class Document(BaseModel):
    """Model to store signed documents linked to a Pyme."""
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pyme_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    contenido: Mapped[str] = mapped_column(String, nullable=False)
    firma_digital: Mapped[str] = mapped_column(String, nullable=True)
    fecha_firma: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
"""Document model for storing signed documents.

This model stores the document content together with a base64
signature and references the owning `Pymes` record via `pyme_id`.
It inherits `BaseModel` which provides a UUID primary key and
timestamp fields.
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from core.database import Base
from models.models import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    # Foreign key to the owning Pyme
    pyme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pymes.id"), nullable=False)

    # Raw document content (text) and signature
    contenido: Mapped[str] = mapped_column(String, nullable=False)
    firma_digital: Mapped[str] = mapped_column(String, nullable=True)
    fecha_firma: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Optional relationship, can be enabled if needed
    # pyme = relationship("Pymes", back_populates="documents")
