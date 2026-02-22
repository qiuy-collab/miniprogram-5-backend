from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.app_session import AppSession


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_login_session(self, login_code: str, session_expires_at: int, now: int) -> AppSession:
        stmt = select(AppSession).where(AppSession.login_code == login_code).limit(1)
        row = self.db.scalars(stmt).first()
        if row is None:
            row = AppSession(
                login_code=login_code,
                session_ready=True,
                session_expires_at=session_expires_at,
                created_at=now,
                updated_at=now,
            )
            self.db.add(row)
            self.db.flush()
            return row

        row.session_ready = True
        row.session_expires_at = session_expires_at
        row.updated_at = now
        self.db.flush()
        return row

