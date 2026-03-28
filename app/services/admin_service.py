from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from pathlib import Path
from typing import Any

import jwt
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.admin_repository import AdminRepository


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


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


def _media_file_url(storage_key: str) -> str:
    public_base_url = settings.public_base_url.rstrip("/")
    media_url_path = settings.media_url_path.rstrip("/")
    return f"{public_base_url}{media_url_path}/{storage_key}"


def _serialize_media_asset(asset) -> dict:
    created_at = asset.created_at.isoformat() if getattr(asset, "created_at", None) else None
    return {
        "id": str(asset.id),
        "storage_key": asset.storage_key,
        "url": asset.url,
        "media_type": asset.media_type,
        "mime_type": asset.mime_type,
        "size_bytes": asset.size_bytes,
        "width": asset.width,
        "height": asset.height,
        "alt_text": asset.alt_text,
        "status": asset.status,
        "created_at": created_at,
    }


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

    @staticmethod
    def list_media_assets() -> dict:
        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                assets = repo.list_media_assets()
                return {"assets": [_serialize_media_asset(asset) for asset in assets]}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "媒体库暂不可用", 503)

    @staticmethod
    async def upload_media_asset(file: UploadFile, admin_user_id: str, alt_text: str = "") -> dict:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "仅支持 JPG、PNG、WEBP、GIF 图片", 400)

        extension = ALLOWED_IMAGE_TYPES[file.content_type or ""]
        storage_key = f"media/{time.strftime('%Y/%m')}/{uuid.uuid4().hex}{extension}"
        uploads_root = settings.uploads_path
        if not uploads_root.is_absolute():
            uploads_root = Path(__file__).resolve().parents[2] / uploads_root
        target_path = uploads_root / storage_key
        target_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        if not content:
            raise AppError(ErrorCode.E_INPUT_REQUIRED, "上传文件不能为空", 400)

        target_path.write_bytes(content)
        size_bytes = len(content)
        asset_url = _media_file_url(storage_key)

        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                asset = repo.create_media_asset(
                    storage_key=storage_key,
                    url=asset_url,
                    media_type="image",
                    mime_type=file.content_type or "",
                    size_bytes=size_bytes,
                    width=None,
                    height=None,
                    alt_text=alt_text.strip(),
                    status="active",
                    created_by_admin_id=admin_user_id,
                )
                db.commit()
                return {"asset": _serialize_media_asset(asset)}
        except SQLAlchemyError:
            if target_path.exists():
                target_path.unlink(missing_ok=True)
            raise AppError(ErrorCode.E_WRITE_FAILED, "媒体上传失败", 500)

    @staticmethod
    def delete_media_asset(asset_id: str) -> None:
        try:
            with SessionLocal() as db:
                repo = AdminRepository(db)
                asset = repo.get_media_asset_by_id(asset_id)
                if asset is None:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "媒体资源不存在", 404)
                repo.delete_media_asset(asset)
                db.commit()
                uploads_root = settings.uploads_path
                if not uploads_root.is_absolute():
                    uploads_root = Path(__file__).resolve().parents[2] / uploads_root
                target_path = uploads_root / asset.storage_key
                target_path.unlink(missing_ok=True)
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "媒体删除失败", 500)
