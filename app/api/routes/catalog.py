from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.auth.admin_deps import get_current_admin_user_id
from app.schemas.catalog import (
    AdminGetProductDetailResponse,
    AdminListProductsResponse,
    AdminUpdateProductStatusRequest,
    AdminUpsertProductRequest,
    GetProductDetailResponse,
    ListProductsResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/catalog/products", response_model=ListProductsResponse)
def list_products(category: Literal["tea", "orchid", "course"] | None = Query(default=None)):
    return CatalogService.list_products(category)


@router.get("/catalog/products/{product_id}", response_model=GetProductDetailResponse)
def get_product_detail(product_id: str):
    return CatalogService.get_product_detail(product_id)


@router.get("/admin/products", response_model=AdminListProductsResponse)
def admin_list_products(admin_user_id: str = Depends(get_current_admin_user_id)):
    return CatalogService.admin_list_products()


@router.get("/admin/products/{product_id}", response_model=AdminGetProductDetailResponse)
def admin_get_product_detail(product_id: str, admin_user_id: str = Depends(get_current_admin_user_id)):
    return CatalogService.admin_get_product_detail(product_id)


@router.post("/admin/products", response_model=AdminGetProductDetailResponse)
def admin_create_product(payload: AdminUpsertProductRequest, admin_user_id: str = Depends(get_current_admin_user_id)):
    return CatalogService.admin_save_product(
        product_id=None,
        name=payload.name,
        price=payload.price,
        img=payload.img,
        description=payload.desc,
        category=payload.category,
        status=payload.status,
        sort_order=payload.sort_order,
        admin_user_id=admin_user_id,
    )


@router.put("/admin/products/{product_id}", response_model=AdminGetProductDetailResponse)
def admin_update_product(
    product_id: str,
    payload: AdminUpsertProductRequest,
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return CatalogService.admin_save_product(
        product_id=product_id,
        name=payload.name,
        price=payload.price,
        img=payload.img,
        description=payload.desc,
        category=payload.category,
        status=payload.status,
        sort_order=payload.sort_order,
        admin_user_id=admin_user_id,
    )


@router.patch("/admin/products/{product_id}/status", response_model=AdminGetProductDetailResponse)
def admin_update_product_status(
    product_id: str,
    payload: AdminUpdateProductStatusRequest,
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return CatalogService.admin_update_product_status(product_id, payload.status, admin_user_id)
