from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.booking_repository import BookingRepository
from app.services.utils import now_ms

DEFAULT_BOOKING_LOCATION = "锦绣路12号·龙兴茶馆"
DEFAULT_BOOKING_STATUS = "待确认"


def _to_booking_record(row) -> dict:
    return {
        "id": str(row.id),
        "typeKey": row.type_key,
        "typeLabel": row.type_label,
        "typeDesc": row.type_desc,
        "datetime": row.datetime,
        "name": row.name,
        "phone": row.phone,
        "notes": row.notes,
        "location": row.location,
        "status": row.status,
        "createdAt": int(row.created_at),
    }


def _to_admin_booking_record(row) -> dict:
    return {
        **_to_booking_record(row),
        "status_code": row.status_code,
        "internal_note": row.internal_note,
        "assigned_admin_id": str(row.assigned_admin_id) if row.assigned_admin_id else None,
        "updated_at": int(row.updated_at) if row.updated_at else None,
    }


class BookingService:
    @staticmethod
    def create_booking(user_id: str, payload: dict) -> dict:
        now = now_ms()
        try:
            with SessionLocal() as db:
                row = BookingRepository(db).create(
                    user_id=user_id,
                    type_key=payload["typeKey"],
                    type_label=payload["typeLabel"],
                    type_desc=payload["typeDesc"],
                    datetime=payload["datetime"],
                    name=payload["name"].strip(),
                    phone=payload["phone"].strip(),
                    notes=payload.get("notes", "").strip(),
                    location=DEFAULT_BOOKING_LOCATION,
                    status=DEFAULT_BOOKING_STATUS,
                    created_at=now,
                )
                db.commit()
            return {"record": _to_booking_record(row)}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "预约创建失败", 500)

    @staticmethod
    def list_bookings(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                rows = BookingRepository(db).list_by_user_id(user_id)
            return {"records": [_to_booking_record(r) for r in rows]}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "预约服务暂不可用", 503)

    @staticmethod
    def admin_list_bookings() -> dict:
        try:
            with SessionLocal() as db:
                rows = BookingRepository(db).list_admin()
            return {"records": [_to_admin_booking_record(r) for r in rows]}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "预约服务暂不可用", 503)

    @staticmethod
    def admin_get_booking_detail(booking_id: str) -> dict:
        try:
            with SessionLocal() as db:
                row = BookingRepository(db).get_admin_by_id(booking_id)
            if not row:
                raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "预约不存在", 404)
            return {"record": _to_admin_booking_record(row)}
        except AppError:
            raise
        except (SQLAlchemyError, ValueError):
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "预约服务暂不可用", 503)

    @staticmethod
    def admin_update_booking(booking_id: str, status_code: str, internal_note: str, admin_user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                repo = BookingRepository(db)
                row = repo.get_admin_by_id(booking_id)
                if not row:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "预约不存在", 404)
                row = repo.update_admin_fields(
                    row,
                    status_code=status_code.strip(),
                    internal_note=internal_note.strip(),
                    assigned_admin_id=admin_user_id,
                    updated_at=now_ms(),
                )
                db.commit()
            return {"record": _to_admin_booking_record(row)}
        except AppError:
            raise
        except (SQLAlchemyError, ValueError):
            raise AppError(ErrorCode.E_WRITE_FAILED, "预约更新失败", 500)
