import uuid

from sqlalchemy import BigInteger, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AppSession(Base):
    __tablename__ = "app_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    session_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    session_expires_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
