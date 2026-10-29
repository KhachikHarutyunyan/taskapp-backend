from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.utils import get_utc_date
from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_date)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)


    authored_tasks: Mapped[list["Task"]] = relationship(  # type: ignore
        "Task",
        back_populates="author",
        foreign_keys="Task.author_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id: {self.id}, email: {self.email}>"

    def get_context_string(self, context: str):
        return f"\
        {context}{self.password[-6:]}\
        {self.created_at.strftime('%m%d%Y%H%M%S')}".strip()

