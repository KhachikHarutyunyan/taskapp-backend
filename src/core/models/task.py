from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.utils.dates_util import get_utc_date
from src.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_date)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_date)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    author_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    author: Mapped["User"] = relationship(  # type: ignore
        "User",
        back_populates="authored_tasks",
        foreign_keys=[author_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"< Task id: {self.id}, name: {self.name} >"
