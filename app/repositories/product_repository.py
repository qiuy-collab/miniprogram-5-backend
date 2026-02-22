from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, category: str | None = None) -> list[Product]:
        stmt = select(Product)
        if category:
            stmt = stmt.where(Product.category == category)
        stmt = stmt.order_by(Product.id)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, product_id: str) -> Product | None:
        pid = uuid.UUID(product_id)
        stmt = select(Product).where(Product.id == pid).limit(1)
        return self.db.scalars(stmt).first()

    def list_by_ids(self, product_ids: list[str]) -> list[Product]:
        if not product_ids:
            return []
        ids = [uuid.UUID(pid) for pid in product_ids]
        stmt = select(Product).where(Product.id.in_(ids))
        return list(self.db.scalars(stmt).all())

