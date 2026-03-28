from __future__ import annotations
import time
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

    def list_admin(self) -> list[Product]:
        stmt = select(Product).order_by(Product.sort_order.desc(), Product.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_admin_by_id(self, product_id: str) -> Product | None:
        pid = uuid.UUID(product_id)
        stmt = select(Product).where(Product.id == pid).limit(1)
        return self.db.scalars(stmt).first()

    def create(
        self,
        *,
        name: str,
        price: str,
        img: str,
        description: str,
        category: str,
        status: str,
        sort_order: int,
        created_by_admin_id: uuid.UUID,
    ) -> Product:
        now = int(time.time())
        product = Product(
            name=name,
            price=price,
            img=img,
            description=description,
            category=category,
            status=status,
            sort_order=sort_order,
            published_at=now if status == "published" else None,
            created_by_admin_id=created_by_admin_id,
            updated_by_admin_id=created_by_admin_id,
        )
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def update(
        self,
        product: Product,
        *,
        name: str,
        price: str,
        img: str,
        description: str,
        category: str,
        status: str,
        sort_order: int,
        updated_by_admin_id: uuid.UUID,
    ) -> Product:
        product.name = name
        product.price = price
        product.img = img
        product.description = description
        product.category = category
        product.status = status
        product.sort_order = sort_order
        product.updated_by_admin_id = updated_by_admin_id
        if status == "published" and not product.published_at:
            product.published_at = int(time.time())
        self.db.flush()
        self.db.refresh(product)
        return product

    def update_status(self, product: Product, status: str, updated_by_admin_id: uuid.UUID) -> Product:
        product.status = status
        product.updated_by_admin_id = updated_by_admin_id
        if status == "published" and not product.published_at:
            product.published_at = int(time.time())
        self.db.flush()
        self.db.refresh(product)
        return product
