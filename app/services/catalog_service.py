from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.product_repository import ProductRepository
from app.services.product_mapper import to_product_payload
from app.services.utils import ensure_str_uuid


class CatalogService:
    @staticmethod
    def list_products(category: str | None = None) -> dict:
        try:
            with SessionLocal() as db:
                rows = ProductRepository(db).list(category)
            return {"products": [to_product_payload(r) for r in rows]}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "商品服务暂不可用", 503)

    @staticmethod
    def get_product_detail(product_id: str) -> dict:
        try:
            product_id = ensure_str_uuid(product_id)
            with SessionLocal() as db:
                row = ProductRepository(db).get_by_id(product_id)
            if not row:
                raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "商品不存在", 404)
            return {"product": to_product_payload(row)}
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "商品服务暂不可用", 503)
