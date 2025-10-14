from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.credits import Credits
else:
    Credits = "Credits"
    User = "User"

class Pymes(BaseModel):
    __tablename__ = "pymes"

    name_company: Mapped[str] = mapped_column(nullable=False)
    cuit: Mapped[str] = mapped_column(unique=True, nullable=False)
    legal_form: Mapped[str] = mapped_column(nullable=False)
    activity: Mapped[str] = mapped_column(nullable=False)
    corporate_email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    postal_code: Mapped[str] = mapped_column(nullable=False)


    # Relationship one-to-one with User
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped[User] = relationship(back_populates="pyme")
    
    # Relationship one-to-many with Credits
    credits: Mapped[List[Credits]] = relationship(back_populates="pyme")