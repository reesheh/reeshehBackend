from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin

class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"            

    # Use the same UUID as auth.users.id (FK with cascade)
    id: Mapped = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True
    )

    email: Mapped[str | None] = mapped_column(String(255), index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    # avatar_url: Mapped[str | None] = mapped_column(String(2048))
