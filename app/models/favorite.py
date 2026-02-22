import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (CheckConstraint("count >= 1", name="favorites_count_check"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
