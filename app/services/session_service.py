import json
from datetime import datetime, timedelta, timezone
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import jwt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.app_user_repository import AppUserRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.wechat_repository import WechatRepository
from app.services.utils import now_ms


class SessionService:
    @staticmethod
    def acquire_session(login_code: str) -> dict:
        try:
            openid = SessionService._exchange_code_for_openid(login_code)
            user_id = SessionService._resolve_user_id(openid)

            now = now_ms()
            expires_at = now + settings.session_ttl_seconds * 1000
            access_token = SessionService._sign_access_token(user_id)

            with SessionLocal() as db:
                SessionRepository(db).upsert_login_session(login_code, expires_at, now)
                db.commit()

            return {
                "sessionReady": True,
                "sessionExpiresAt": expires_at,
                "accessToken": access_token,
            }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "会话服务暂不可用", 503)
        except Exception:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "会话服务暂不可用", 503)

    @staticmethod
    def _exchange_code_for_openid(login_code: str) -> str:
        query = urlencode(
            {
                "appid": settings.wechat_app_id,
                "secret": settings.wechat_app_secret,
                "js_code": login_code,
                "grant_type": "authorization_code",
            }
        )
        url = f"https://api.weixin.qq.com/sns/jscode2session?{query}"

        try:
            with urlopen(url, timeout=settings.wechat_login_timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError):
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "微信登录服务暂不可用", 503)

        if payload.get("errcode"):
            raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录凭证无效或已过期", 401)

        openid = str(payload.get("openid", "")).strip()
        if not openid:
            raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录凭证无效或已过期", 401)
        return openid

    @staticmethod
    def _resolve_user_id(openid: str) -> str:
        now = now_ms()
        with SessionLocal() as db:
            wechat_repo = WechatRepository(db)
            app_user_repo = AppUserRepository(db)

            mapped = wechat_repo.get_identity_by_openid(openid)
            if mapped:
                return str(mapped.user_id)

            user = app_user_repo.create(now)
            wechat_repo.upsert_identity(openid, str(user.id), now)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                mapped = wechat_repo.get_identity_by_openid(openid)
                if mapped:
                    return str(mapped.user_id)
                raise
            return str(user.id)

    @staticmethod
    def _sign_access_token(user_id: str) -> str:
        exp = datetime.now(tz=timezone.utc) + timedelta(seconds=settings.session_ttl_seconds)
        payload = {
            "sub": user_id,
            "exp": exp,
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return str(token)
