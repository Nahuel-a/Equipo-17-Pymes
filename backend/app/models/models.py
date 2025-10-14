from core.database import Base
from datetime import datetime
from typing import Optional
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), # Set default value to current timestamp
        nullable=False,
        default=datetime.utcnow,  # Python-side default for SQLAlchemy ORM
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),  # Only updated in ORM
        nullable=False,
        default=datetime.utcnow,  # Python-side default for SQLAlchemy ORM
    )








