from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

import jwt
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.admin_repository import AdminRepository


def hash_admin_password(password: str) -> str:
    salt = settings.jwt_secret.encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return base64.b64encode(digest).decode("utf-8")


def verify_admin_password(password: str, password_hash: str) -> bool:
    expected = hash_admin_password(password)
    return hmac.compare_digest(expected, password_hash)


def create_admin_access_token(admin_user_id: str, roles: list[str]) -> str:
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": admin_user_id,
        "roles": roles,
        "scope": "admin",
        "iat": now,
        "exp": now + settings.session_ttl_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class AdminService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        if not username or not password:
            raise AppError(ErrorCode.E_INPUT_REQUIRED, "账号和密码不能为空", 400)

        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                admin_user = repo.get_admin_user_by_username(username)
                if admin_user is None or not verify_admin_password(password, admin_user.password_hash):
                    raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "账号或密码错误", 401)
                if admin_user.status != "active":
                    raise AppError(ErrorCode.E_STATE_CONFLICT, "当前管理员账号不可用", 403)
                roles = repo.list_roles_for_admin_user(str(admin_user.id))
                role_codes = [role.code for role in roles]
                access_token = create_admin_access_token(str(admin_user.id), role_codes)
                return {
                    "accessToken": access_token,
                    "admin_user": {
                        "id": str(admin_user.id),
                        "username": admin_user.username,
                        "display_name": admin_user.display_name,
                        "status": admin_user.status,
                        "roles": [
                            {
                                "id": str(role.id),
                                "code": role.code,
                                "name": role.name,
                            }
                            for role in roles
                        ],
                    },
                }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "后台登录服务暂不可用", 503)

    @staticmethod
    def get_current_admin(admin_user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                admin_user = repo.get_admin_user_by_id(admin_user_id)
                if admin_user is None:
                    raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "后台登录状态已失效", 401)
                roles = repo.list_roles_for_admin_user(str(admin_user.id))
                return {
                    "admin_user": {
                        "id": str(admin_user.id),
                        "username": admin_user.username,
                        "display_name": admin_user.display_name,
                        "status": admin_user.status,
                        "roles": [
                            {
                                "id": str(role.id),
                                "code": role.code,
                                "name": role.name,
                            }
                            for role in roles
                        ],
                    }
                }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "后台用户信息暂不可用", 503)

    @staticmethod
    def get_dashboard_summary() -> dict:
        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                return {
                    "summary": {
                        "draft_article_count": repo.count_articles_by_status("draft"),
                        "published_article_count": repo.count_articles_by_status("published"),
                        "active_product_count": repo.count_products_by_status("published"),
                        "pending_booking_count": repo.count_bookings_by_status_code("new"),
                        "media_asset_count": repo.count_media_assets(),
                    }
                }
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "后台概览暂不可用", 503)
