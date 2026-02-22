from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
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
