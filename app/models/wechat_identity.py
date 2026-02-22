import uuid

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WechatIdentity(Base):
    __tablename__ = "wechat_identities"

    openid: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
