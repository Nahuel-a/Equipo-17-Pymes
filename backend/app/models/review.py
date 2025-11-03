from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text
from typing import TYPE_CHECKING, Optional
import uuid

if TYPE_CHECKING:
    from .user import User
    from .credits import Credits

class Reviews(BaseModel):
    __tablename__ = "reviews"

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    review_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reviewer: Mapped["User"] = relationship(back_populates="reviews")

    credits_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("credits.id"), nullable=False)
    credits: Mapped["Credits"] = relationship(back_populates="reviews")

