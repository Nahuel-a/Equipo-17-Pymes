from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .user import User
    from .credits import Credits

class Reviews(BaseModel):
    __tablename__ = "reviews"

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys for many-to-many relationship
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    credits_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("credits.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="reviews")
    credits: Mapped["Credits"] = relationship(back_populates="reviews")

