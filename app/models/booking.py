import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("char_length(name) >= 1 and char_length(name) <= 12", name="bookings_name_check"),
        CheckConstraint("phone ~ '^1[0-9]{10}$'", name="bookings_phone_check"),
        CheckConstraint("char_length(notes) <= 60", name="bookings_notes_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type_key: Mapped[str] = mapped_column(Text, nullable=False)
    type_label: Mapped[str] = mapped_column(Text, nullable=False)
    type_desc: Mapped[str] = mapped_column(Text, nullable=False)
    datetime: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    location: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
