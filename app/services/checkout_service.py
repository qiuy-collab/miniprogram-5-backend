from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.checkout_repository import CheckoutRepository
from app.repositories.product_repository import ProductRepository
from app.services.product_mapper import to_product_payload
from app.services.utils import ensure_str_uuid, now_ms


class CheckoutService:
    @staticmethod
    def create_session(user_id: str, source: str, items: list[dict]) -> dict:
        if not items:
            raise AppError(ErrorCode.E_CHECKOUT_SELECTION_EMPTY, "结算条目为空", 400)

        try:
            safe_ids = [ensure_str_uuid(item["productId"]) for item in items]
            with SessionLocal() as db:
                product_repo = ProductRepository(db)
                checkout_repo = CheckoutRepository(db)

                products = product_repo.list_by_ids(safe_ids)
                product_map = {str(p.id): to_product_payload(p) for p in products}
                if len(product_map) != len(set(safe_ids)):
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "部分商品不存在", 404)

                created_at = now_ms()
                checkout_repo.upsert_session(user_id, source, created_at)
                checkout_repo.replace_items(
                    user_id,
                    [
                        {"product_id": ensure_str_uuid(item["productId"]), "count": int(item["count"])}
                        for item in items
                    ],
                )
                db.commit()

            session_items = [
                {
                    "product": product_map[ensure_str_uuid(item["productId"])],
                    "count": int(item["count"]),
                }
                for item in items
            ]
            return {"session": {"source": source, "items": session_items, "createdAt": created_at}}
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "结算会话创建失败", 500)

    @staticmethod
    def get_active_session(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                checkout_repo = CheckoutRepository(db)
                product_repo = ProductRepository(db)

                session = checkout_repo.get_session(user_id)
                if not session:
                    return {"session": None}

                item_rows = checkout_repo.list_items(user_id)
                if not item_rows:
                    return {"session": None}

                product_ids = [str(i.product_id) for i in item_rows]
                products = product_repo.list_by_ids(product_ids)
                product_map = {str(p.id): to_product_payload(p) for p in products}
                if len(product_map) != len(set(product_ids)):
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "部分商品不存在", 404)

            session_items = [
                {
                    "product": product_map[str(i.product_id)],
                    "count": int(i.count),
                }
                for i in item_rows
            ]

            return {
                "session": {
                    "source": session.source,
                    "items": session_items,
                    "createdAt": int(session.created_at),
                }
            }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "结算服务暂不可用", 503)

    @staticmethod
    def clear_session(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                CheckoutRepository(db).delete_session(user_id)
                db.commit()
            return {"cleared": True}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "清理结算会话失败", 500)
