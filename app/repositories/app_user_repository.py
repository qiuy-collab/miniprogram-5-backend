from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.app_user import AppUser


class AppUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, created_at: int) -> AppUser:
        user = AppUser(created_at=created_at)
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id(self, user_id: str) -> AppUser | None:
        uid = uuid.UUID(user_id)
        stmt = select(AppUser).where(AppUser.id == uid).limit(1)
        return self.db.scalars(stmt).first()

