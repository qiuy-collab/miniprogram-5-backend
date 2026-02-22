from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wechat_identity import WechatIdentity
from app.models.wechat_payment_prepare import WechatPaymentPrepare


class WechatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_identity_by_openid(self, openid: str) -> WechatIdentity | None:
        stmt = select(WechatIdentity).where(WechatIdentity.openid == openid).limit(1)
        return self.db.scalars(stmt).first()

    def get_identity_by_user_id(self, user_id: str) -> WechatIdentity | None:
        uid = uuid.UUID(user_id)
        stmt = select(WechatIdentity).where(WechatIdentity.user_id == uid).limit(1)
        return self.db.scalars(stmt).first()

    def upsert_identity(self, openid: str, user_id: str, created_at: int) -> WechatIdentity:
        uid = uuid.UUID(user_id)
        row = self.get_identity_by_openid(openid)
        if row is None:
            row = WechatIdentity(openid=openid, user_id=uid, created_at=created_at)
            self.db.add(row)
            self.db.flush()
            return row

        row.user_id = uid
        row.created_at = created_at
        self.db.flush()
        return row

    def get_payment_prepare(self, out_trade_no: str) -> WechatPaymentPrepare | None:
        stmt = (
            select(WechatPaymentPrepare)
            .where(WechatPaymentPrepare.out_trade_no == out_trade_no)
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def upsert_payment_prepare(
        self,
        *,
        out_trade_no: str,
        user_id: str,
        checkout_created_at: int,
        created_at: int,
    ) -> WechatPaymentPrepare:
        uid = uuid.UUID(user_id)
        row = self.get_payment_prepare(out_trade_no)
        if row is None:
            row = WechatPaymentPrepare(
                out_trade_no=out_trade_no,
                user_id=uid,
                checkout_created_at=checkout_created_at,
                created_at=created_at,
            )
            self.db.add(row)
            self.db.flush()
            return row

        row.user_id = uid
        row.checkout_created_at = checkout_created_at
        row.created_at = created_at
        self.db.flush()
        return row

