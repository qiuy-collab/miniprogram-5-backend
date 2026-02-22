import uuid

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("pay_method in ('wechat', 'alipay')", name="payments_pay_method_check"),
        CheckConstraint("source in ('favorites', 'product')", name="payments_source_check"),
        UniqueConstraint("user_id", "checkout_created_at", name="payments_user_checkout_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    checkout_created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pay_method: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    paid_product_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
