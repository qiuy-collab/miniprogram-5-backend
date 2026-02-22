from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.services.product_mapper import to_product_payload
from app.services.utils import ensure_str_uuid, now_ms


class FavoriteService:
    @staticmethod
    def list_favorites(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                favorite_rows = FavoriteRepository(db).list_by_user_id(user_id)
                product_ids = [str(r.product_id) for r in favorite_rows]
                products = ProductRepository(db).list_by_ids(product_ids)

            product_map = {str(p.id): to_product_payload(p) for p in products}
            items = []
            for row in favorite_rows:
                product_id = str(row.product_id)
                product = product_map.get(product_id)
                if not product:
                    continue
                items.append(
                    {
                        "product": product,
                        "count": int(row.count),
                        "addedAt": int(row.added_at),
                    }
                )
            return {"items": items}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "收藏服务暂不可用", 503)

    @staticmethod
    def add_favorite(user_id: str, product_id: str, count_delta: int) -> dict:
        try:
            product_id = ensure_str_uuid(product_id)
            now = now_ms()
            with SessionLocal() as db:
                product_repo = ProductRepository(db)
                favorite_repo = FavoriteRepository(db)

                product_row = product_repo.get_by_id(product_id)
                if not product_row:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "商品不存在", 404)
                product_payload = to_product_payload(product_row)

                existing = favorite_repo.get_one(user_id, product_id)
                new_count = (int(existing.count) if existing else 0) + count_delta
                favorite_repo.upsert_count(user_id, product_id, new_count, now)
                total_count = favorite_repo.get_total_count(user_id)
                db.commit()

            return {
                "item": {"product": product_payload, "count": new_count, "addedAt": now},
                "totalCount": total_count,
            }
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "收藏写入失败", 500)

    @staticmethod
    def remove_favorite(user_id: str, product_id: str) -> dict:
        try:
            product_id = ensure_str_uuid(product_id)
            with SessionLocal() as db:
                removed = FavoriteRepository(db).delete_one(user_id, product_id)
                db.commit()
            return {"removed": removed}
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "移除收藏失败", 500)

    @staticmethod
    def clear_favorites(user_id: str) -> dict:
        try:
            with SessionLocal() as db:
                FavoriteRepository(db).clear_by_user(user_id)
                db.commit()
            return {"cleared": True}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "清空收藏失败", 500)

    @staticmethod
    def batch_remove_favorites(user_id: str, product_ids: list[str]) -> dict:
        if not product_ids:
            return {"removedIds": []}

        try:
            safe_ids = [ensure_str_uuid(pid) for pid in product_ids]
            with SessionLocal() as db:
                removed_ids = FavoriteRepository(db).batch_delete_by_product_ids(user_id, safe_ids)
                db.commit()
            return {"removedIds": removed_ids}
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "批量移除收藏失败", 500)
