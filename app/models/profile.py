import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint("char_length(name) >= 1 and char_length(name) <= 10", name="profiles_name_check"),
        CheckConstraint("char_length(city) <= 12", name="profiles_city_check"),
        CheckConstraint("phone ~ '^1[0-9]{10}$'", name="profiles_phone_check"),
        CheckConstraint("char_length(motto) <= 40", name="profiles_motto_check"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False, default="")
    phone: Mapped[str] = mapped_column(Text, nullable=False)
    motto: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
