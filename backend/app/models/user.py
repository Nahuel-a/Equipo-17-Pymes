from typing import Optional
from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from datetime import UTC


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    is_superuser: Mapped[Optional[bool]] = mapped_column(default=False)


    