from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.app_user_repository import AppUserRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.utils import now_ms

DEFAULT_PROFILE = {
    "name": "茶友",
    "city": "上海",
    "phone": "13800138000",
    "motto": "一盏茶里，安放心神。",
}


class ProfileService:
    @staticmethod
    def get_profile(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                row = ProfileRepository(db).get_by_user_id(user_id)
            if not row:
                return {"profile": DEFAULT_PROFILE}
            return {
                "profile": {
                    "name": row.name,
                    "city": row.city,
                    "phone": row.phone,
                    "motto": row.motto,
                }
            }
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "资料服务暂不可用", 503)

    @staticmethod
    def update_profile(user_id: str, payload: dict) -> dict:
        now = now_ms()
        try:
            with SessionLocal() as db:
                row = ProfileRepository(db).upsert(
                    user_id,
                    name=payload["name"].strip(),
                    city=payload.get("city", "").strip(),
                    phone=payload["phone"].strip(),
                    motto=payload.get("motto", "").strip(),
                    updated_at=now,
                )
                db.commit()
            return {
                "profile": {
                    "name": row.name,
                    "city": row.city,
                    "phone": row.phone,
                    "motto": row.motto,
                },
                "updatedAt": now,
            }
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "资料保存失败", 500)

    @staticmethod
    def admin_list_users() -> dict:
        try:
            records = []
            with SessionLocal() as db:
                user_repo = AppUserRepository(db)
                profile_repo = ProfileRepository(db)
                users = user_repo.list_admin()
                for user in users:
                    profile = profile_repo.get_by_user_id(str(user.id))
                    records.append(
                        {
                            "user_id": str(user.id),
                            "created_at": int(user.created_at),
                            "profile": {
                                "name": profile.name,
                                "city": profile.city,
                                "phone": profile.phone,
                                "motto": profile.motto,
                            }
                            if profile
                            else DEFAULT_PROFILE,
                        }
                    )
            return {"records": records}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "用户数据暂不可用", 503)

    @staticmethod
    def admin_get_user_detail(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                user_repo = AppUserRepository(db)
                profile_repo = ProfileRepository(db)
                user = user_repo.get_admin_by_id(user_id)
                if not user:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "用户不存在", 404)
                profile = profile_repo.get_by_user_id(user_id)
            return {
                "record": {
                    "user_id": str(user.id),
                    "created_at": int(user.created_at),
                    "profile": {
                        "name": profile.name,
                        "city": profile.city,
                        "phone": profile.phone,
                        "motto": profile.motto,
                    }
                    if profile
                    else DEFAULT_PROFILE,
                }
            }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "用户数据暂不可用", 503)
