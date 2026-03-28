from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        user_id: str,
        type_key: str,
        type_label: str,
        type_desc: str,
        datetime: str,
        name: str,
        phone: str,
        notes: str,
        location: str,
        status: str,
        created_at: int,
    ) -> Booking:
        row = Booking(
            user_id=uuid.UUID(user_id),
            type_key=type_key,
            type_label=type_label,
            type_desc=type_desc,
            datetime=datetime,
            name=name,
            phone=phone,
            notes=notes,
            location=location,
            status=status,
            created_at=created_at,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_by_user_id(self, user_id: str) -> list[Booking]:
        uid = uuid.UUID(user_id)
        stmt = select(Booking).where(Booking.user_id == uid).order_by(Booking.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def list_admin(self) -> list[Booking]:
        stmt = select(Booking).order_by(Booking.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_admin_by_id(self, booking_id: str) -> Booking | None:
        bid = uuid.UUID(booking_id)
        stmt = select(Booking).where(Booking.id == bid).limit(1)
        return self.db.scalars(stmt).first()

    def update_admin_fields(
        self,
        booking: Booking,
        *,
        status_code: str,
        internal_note: str,
        assigned_admin_id: str,
        updated_at: int,
    ) -> Booking:
        booking.status_code = status_code
        booking.internal_note = internal_note
        booking.assigned_admin_id = uuid.UUID(assigned_admin_id)
        booking.updated_at = updated_at
        self.db.flush()
        self.db.refresh(booking)
        return booking
