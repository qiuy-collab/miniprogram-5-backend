import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.app_user_repository import AppUserRepository
from app.services.utils import ensure_str_uuid

security = HTTPBearer(auto_error=False)


async def get_current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    if credentials is None or not credentials.credentials:
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "未提供有效登录凭证", 401)

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = ensure_str_uuid(str(payload.get("sub", "")))
    except (ExpiredSignatureError, InvalidTokenError, ValueError):
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录状态已失效", 401)

    try:
        with SessionLocal() as db:
            user = AppUserRepository(db).get_by_id(user_id)
        if user is None:
            raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录状态已失效", 401)
        return user_id
    except AppError:
        raise
    except SQLAlchemyError:
        raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录状态已失效", 401)
