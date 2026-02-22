from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> Profile | None:
        uid = uuid.UUID(user_id)
        stmt = select(Profile).where(Profile.user_id == uid).limit(1)
        return self.db.scalars(stmt).first()

    def upsert(
        self,
        user_id: str,
        *,
        name: str,
        city: str,
        phone: str,
        motto: str,
        updated_at: int,
    ) -> Profile:
        uid = uuid.UUID(user_id)
        profile = self.get_by_user_id(user_id)
        if profile is None:
            profile = Profile(
                user_id=uid,
                name=name,
                city=city,
                phone=phone,
                motto=motto,
                updated_at=updated_at,
            )
            self.db.add(profile)
            self.db.flush()
            return profile

        profile.name = name
        profile.city = city
        profile.phone = phone
        profile.motto = motto
        profile.updated_at = updated_at
        self.db.flush()
        return profile

