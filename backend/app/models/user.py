from typing import Optional, TYPE_CHECKING
from .models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .enums import RoleUser
from sqlalchemy import Enum as SAEnum

if TYPE_CHECKING:
    from .pyme import Pymes
else:
    Pymes = "Pymes"

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
    
    # Relación uno a uno con Pyme
    pyme: Mapped[Pymes] = relationship(back_populates="user", uselist=False)
    