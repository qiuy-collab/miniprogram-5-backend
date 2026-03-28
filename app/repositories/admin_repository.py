from __future__ import annotations
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.admin import AdminRole, AdminUser, AdminUserRole
from app.models.article import Article
from app.models.booking import Booking
from app.models.media_asset import MediaAsset
from app.models.product import Product


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_user_by_username(self, username: str) -> AdminUser | None:
        stmt = select(AdminUser).where(AdminUser.username == username).limit(1)
        return self.db.scalars(stmt).first()

    def get_admin_user_by_id(self, admin_user_id: str) -> AdminUser | None:
        uid = uuid.UUID(admin_user_id)
        stmt = select(AdminUser).where(AdminUser.id == uid).limit(1)
        return self.db.scalars(stmt).first()

    def list_roles_for_admin_user(self, admin_user_id: str) -> list[AdminRole]:
        uid = uuid.UUID(admin_user_id)
        stmt = (
            select(AdminRole)
            .join(AdminUserRole, AdminRole.id == AdminUserRole.admin_role_id)
            .where(AdminUserRole.admin_user_id == uid)
            .order_by(AdminRole.code)
        )
        return list(self.db.scalars(stmt).all())

    def count_articles_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(Article).where(Article.status == status)
        return int(self.db.scalar(stmt) or 0)

    def count_products_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(Product).where(Product.status == status)
        return int(self.db.scalar(stmt) or 0)

    def count_bookings_by_status_code(self, status_code: str) -> int:
        stmt = select(func.count()).select_from(Booking).where(Booking.status_code == status_code)
        return int(self.db.scalar(stmt) or 0)

    def count_media_assets(self) -> int:
        stmt = select(func.count()).select_from(MediaAsset)
        return int(self.db.scalar(stmt) or 0)

    def list_media_assets(self) -> list[MediaAsset]:
        stmt = select(MediaAsset).order_by(MediaAsset.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_media_asset_by_id(self, asset_id: str) -> MediaAsset | None:
        stmt = select(MediaAsset).where(MediaAsset.id == uuid.UUID(asset_id)).limit(1)
        return self.db.scalars(stmt).first()

    def create_media_asset(
        self,
        *,
        storage_key: str,
        url: str,
        media_type: str,
        mime_type: str,
        size_bytes: int,
        width: int | None,
        height: int | None,
        alt_text: str,
        status: str,
        created_by_admin_id: str | None,
    ) -> MediaAsset:
        asset = MediaAsset(
            storage_key=storage_key,
            url=url,
            media_type=media_type,
            mime_type=mime_type,
            size_bytes=size_bytes,
            width=width,
            height=height,
            alt_text=alt_text,
            status=status,
            created_by_admin_id=uuid.UUID(created_by_admin_id) if created_by_admin_id else None,
        )
        self.db.add(asset)
        self.db.flush()
        self.db.refresh(asset)
        return asset

    def delete_media_asset(self, asset: MediaAsset) -> None:
        self.db.delete(asset)
        self.db.flush()
