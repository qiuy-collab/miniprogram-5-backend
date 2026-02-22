import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CheckoutSessionItem(Base):
    __tablename__ = "checkout_session_items"
    __table_args__ = (CheckConstraint("count >= 1", name="checkout_session_items_count_check"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checkout_sessions.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False)
