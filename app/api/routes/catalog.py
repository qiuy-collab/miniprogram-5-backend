from typing import Literal

from fastapi import APIRouter, Query

from app.schemas.catalog import GetProductDetailResponse, ListProductsResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/catalog/products", response_model=ListProductsResponse)
def list_products(category: Literal["tea", "orchid", "course"] | None = Query(default=None)):
    return CatalogService.list_products(category)


@router.get("/catalog/products/{product_id}", response_model=GetProductDetailResponse)
def get_product_detail(product_id: str):
    return CatalogService.get_product_detail(product_id)
