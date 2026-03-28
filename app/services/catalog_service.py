from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.product_repository import ProductRepository
from app.services.product_mapper import to_admin_product_payload, to_product_payload
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

    @staticmethod
    def admin_list_products() -> dict:
        try:
            with SessionLocal() as db:
                rows = ProductRepository(db).list_admin()
            return {"products": [to_admin_product_payload(r) for r in rows]}
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "商品服务暂不可用", 503)

    @staticmethod
    def admin_get_product_detail(product_id: str) -> dict:
        try:
            pid = ensure_str_uuid(product_id)
            with SessionLocal() as db:
                row = ProductRepository(db).get_admin_by_id(pid)
            if not row:
                raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "商品不存在", 404)
            return {"product": to_admin_product_payload(row)}
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "商品ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "商品服务暂不可用", 503)

    @staticmethod
    def admin_save_product(
        product_id: str | None,
        name: str,
        price: str,
        img: str,
        description: str,
        category: str,
        status: str,
        sort_order: int,
        admin_user_id: str,
    ) -> dict:
        from app.services.utils import ensure_str_uuid
        import uuid

        try:
            uid = uuid.UUID(admin_user_id)
            with SessionLocal() as db:
                repo = ProductRepository(db)
                if product_id:
                    pid = uuid.UUID(product_id)
                    product = repo.get_admin_by_id(product_id)
                    if not product:
                        raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "商品不存在", 404)
                    product = repo.update(
                        product,
                        name=name,
                        price=price,
                        img=img,
                        description=description,
                        category=category,
                        status=status,
                        sort_order=sort_order,
                        updated_by_admin_id=uid,
                    )
                else:
                    product = repo.create(
                        name=name,
                        price=price,
                        img=img,
                        description=description,
                        category=category,
                        status=status,
                        sort_order=sort_order,
                        created_by_admin_id=uid,
                    )
                db.commit()
                return {"product": to_admin_product_payload(product)}
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "商品保存失败", 500)

    @staticmethod
    def admin_update_product_status(product_id: str, status: str, admin_user_id: str) -> dict:
        import uuid

        try:
            uid = uuid.UUID(admin_user_id)
            pid = uuid.UUID(product_id)
            with SessionLocal() as db:
                repo = ProductRepository(db)
                product = repo.get_admin_by_id(product_id)
                if not product:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "商品不存在", 404)
                product = repo.update_status(product, status, uid)
                db.commit()
                return {"product": to_admin_product_payload(product)}
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_WRITE_FAILED, "商品状态更新失败", 500)
