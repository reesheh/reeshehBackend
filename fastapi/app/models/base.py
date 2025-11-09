from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

class Base(DeclarativeBase):
    pass

# Optional timestamp mixin (DB-level defaults)
class TimestampMixin:
    created_at: Mapped = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False
    )
