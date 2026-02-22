from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.booking_repository import BookingRepository
from app.services.utils import now_ms

DEFAULT_BOOKING_LOCATION = "锦绣路12号·龙兴茶馆"
DEFAULT_BOOKING_STATUS = "待确认"


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
            return {
                "record": {
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
            }
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "预约创建失败", 500)

    @staticmethod
    def list_bookings(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                rows = BookingRepository(db).list_by_user_id(user_id)
            records = [
                {
                    "id": str(r.id),
                    "typeKey": r.type_key,
                    "typeLabel": r.type_label,
                    "typeDesc": r.type_desc,
                    "datetime": r.datetime,
                    "name": r.name,
                    "phone": r.phone,
                    "notes": r.notes,
                    "location": r.location,
                    "status": r.status,
                    "createdAt": int(r.created_at),
                }
                for r in rows
            ]
            return {"records": records}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "预约服务暂不可用", 503)
