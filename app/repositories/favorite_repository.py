from __future__ import annotations
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user_id(self, user_id: str) -> list[Favorite]:
        uid = uuid.UUID(user_id)
        stmt = select(Favorite).where(Favorite.user_id == uid)
        return list(self.db.scalars(stmt).all())

    def get_one(self, user_id: str, product_id: str) -> Favorite | None:
        uid = uuid.UUID(user_id)
        pid = uuid.UUID(product_id)
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == uid)
            .where(Favorite.product_id == pid)
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def upsert_count(self, user_id: str, product_id: str, count: int, added_at: int) -> Favorite:
        uid = uuid.UUID(user_id)
        pid = uuid.UUID(product_id)
        row = self.get_one(user_id, product_id)
        if row is None:
            row = Favorite(user_id=uid, product_id=pid, count=count, added_at=added_at)
            self.db.add(row)
            self.db.flush()
            return row

        row.count = count
        row.added_at = added_at
        self.db.flush()
        return row

    def get_total_count(self, user_id: str) -> int:
        uid = uuid.UUID(user_id)
        stmt = select(func.coalesce(func.sum(Favorite.count), 0)).where(Favorite.user_id == uid)
        value = self.db.execute(stmt).scalar_one()
        return int(value)

    def delete_one(self, user_id: str, product_id: str) -> bool:
        uid = uuid.UUID(user_id)
        pid = uuid.UUID(product_id)
        stmt = (
            delete(Favorite)
            .where(Favorite.user_id == uid)
            .where(Favorite.product_id == pid)
            .returning(Favorite.product_id)
        )
        removed = self.db.execute(stmt).all()
        return bool(removed)

    def clear_by_user(self, user_id: str) -> int:
        uid = uuid.UUID(user_id)
        stmt = delete(Favorite).where(Favorite.user_id == uid).returning(Favorite.product_id)
        removed = self.db.execute(stmt).all()
        return len(removed)

    def batch_delete_by_product_ids(self, user_id: str, product_ids: list[str]) -> list[str]:
        if not product_ids:
            return []
        uid = uuid.UUID(user_id)
        pids = [uuid.UUID(pid) for pid in product_ids]
        stmt = (
            delete(Favorite)
            .where(Favorite.user_id == uid)
            .where(Favorite.product_id.in_(pids))
            .returning(Favorite.product_id)
        )
        rows = self.db.execute(stmt).all()
        return [str(row[0]) for row in rows]

