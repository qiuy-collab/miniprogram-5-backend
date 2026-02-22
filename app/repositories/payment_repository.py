from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_checkout(self, user_id: str, checkout_created_at: int) -> Payment | None:
        uid = uuid.UUID(user_id)
        stmt = (
            select(Payment)
            .where(Payment.user_id == uid)
            .where(Payment.checkout_created_at == int(checkout_created_at))
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        *,
        user_id: str,
        checkout_created_at: int,
        pay_method: str,
        source: str,
        paid: bool,
        paid_product_ids: list[str],
        created_at: int,
    ) -> Payment:
        row = Payment(
            user_id=uuid.UUID(user_id),
            checkout_created_at=int(checkout_created_at),
            pay_method=pay_method,
            source=source,
            paid=paid,
            paid_product_ids=[uuid.UUID(pid) for pid in paid_product_ids],
            created_at=created_at,
        )
        self.db.add(row)
        self.db.flush()
        return row

