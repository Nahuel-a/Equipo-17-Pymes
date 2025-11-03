from typing import Optional, TYPE_CHECKING, List
from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .enums import RoleUser
from sqlalchemy import Enum as SAEnum

if TYPE_CHECKING:
    from .pyme import Pymes
    from .review import Reviews

class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleUser] = mapped_column(
            SAEnum(RoleUser, name="role_enum"),
            default=RoleUser.USER,
            nullable=False,
    )
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    
    # relationship one-to-one with Pymes
    pyme: Mapped[Optional["Pymes"]] = relationship(back_populates="user", uselist=False)

    # relationship one-to-many with Reviews (for admin/reviewer users)
    reviews: Mapped[Optional[List["Reviews"]]] = relationship(back_populates="reviewer")
    