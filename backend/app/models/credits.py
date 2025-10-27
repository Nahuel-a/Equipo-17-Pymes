from typing import Optional, TYPE_CHECKING, List
from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .enums import StatusCredit
from sqlalchemy import Enum as SAEnum, ForeignKey
import uuid

if TYPE_CHECKING:
    from .pyme import Pymes
    from .review import Reviews
else:
    Pymes = "Pymes"
    Reviews = "Reviews"

class Credits(BaseModel):
    __tablename__ = "credits"

    amount: Mapped[float] = mapped_column(nullable=False)
    employees:Mapped[int] = mapped_column(nullable=False)
    annual_sales: Mapped[float] = mapped_column(nullable=False)
    fiscal_year_closing: Mapped[str] = mapped_column(nullable=False)
    total_assets: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[StatusCredit] = mapped_column(
        SAEnum(StatusCredit, name="status_enum"),
        default=StatusCredit.PENDING,
        nullable=False,
    )
    # documents: Mapped[Optional[str]] = mapped_column()
    
    # Relationship many-to-one with Pymes
    pyme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pymes.id"))
    pyme: Mapped[Pymes] = relationship(back_populates="credits")

    # Relationship muchos-a-muchos con Users (reviewers) a través de Reviews
    reviews: Mapped[List["Reviews"]] = relationship(back_populates="credits")
