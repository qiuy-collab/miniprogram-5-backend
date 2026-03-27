import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.admin_repository import AdminRepository
from app.services.utils import ensure_str_uuid

admin_security = HTTPBearer(auto_error=False)


async def get_current_admin_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_security),
) -> str:
    if credentials is None or not credentials.credentials:
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "未提供有效后台登录凭证", 401)

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("scope") != "admin":
            raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "后台登录状态已失效", 401)
        admin_user_id = ensure_str_uuid(str(payload.get("sub", "")))
    except AppError:
        raise
    except (ExpiredSignatureError, InvalidTokenError, ValueError):
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "后台登录状态已失效", 401)

    try:
        with SessionLocal() as db:
            admin_user = AdminRepository(db).get_admin_user_by_id(admin_user_id)
        if admin_user is None or admin_user.status != "active":
            raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "后台登录状态已失效", 401)
        return admin_user_id
    except AppError:
        raise
    except SQLAlchemyError:
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "后台登录状态已失效", 401)
