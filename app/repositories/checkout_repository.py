from __future__ import annotations
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.checkout_session import CheckoutSession
from app.models.checkout_session_item import CheckoutSessionItem


class CheckoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_session(self, user_id: str, source: str, created_at: int) -> CheckoutSession:
        uid = uuid.UUID(user_id)
        row = self.get_session(user_id)
        if row is None:
            row = CheckoutSession(user_id=uid, source=source, created_at=created_at)
            self.db.add(row)
            self.db.flush()
            return row

        row.source = source
        row.created_at = created_at
        self.db.flush()
        return row

    def get_session(self, user_id: str) -> CheckoutSession | None:
        uid = uuid.UUID(user_id)
        stmt = select(CheckoutSession).where(CheckoutSession.user_id == uid).limit(1)
        return self.db.scalars(stmt).first()

    def replace_items(self, user_id: str, items: list[dict]) -> list[CheckoutSessionItem]:
        uid = uuid.UUID(user_id)
        self.db.execute(delete(CheckoutSessionItem).where(CheckoutSessionItem.user_id == uid))

        rows: list[CheckoutSessionItem] = []
        for item in items:
            row = CheckoutSessionItem(
                user_id=uid,
                product_id=uuid.UUID(item["product_id"]),
                count=int(item["count"]),
            )
            self.db.add(row)
            rows.append(row)
        self.db.flush()
        return rows

    def list_items(self, user_id: str) -> list[CheckoutSessionItem]:
        uid = uuid.UUID(user_id)
        stmt = select(CheckoutSessionItem).where(CheckoutSessionItem.user_id == uid)
        return list(self.db.scalars(stmt).all())

    def delete_session(self, user_id: str) -> bool:
        uid = uuid.UUID(user_id)
        stmt = delete(CheckoutSession).where(CheckoutSession.user_id == uid).returning(CheckoutSession.user_id)
        rows = self.db.execute(stmt).all()
        return bool(rows)

