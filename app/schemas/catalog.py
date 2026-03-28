from typing import Literal

from pydantic import BaseModel, Field


ProductCategory = Literal["tea", "orchid", "course"]
ProductStatus = Literal["draft", "published", "archived"]


class Product(BaseModel):
    id: str
    name: str
    price: str
    img: str
    desc: str
    category: ProductCategory


class ListProductsResponse(BaseModel):
    products: list[Product]


class GetProductDetailResponse(BaseModel):
    product: Product


class AdminProductItem(Product):
    status: ProductStatus
    sort_order: int
    published_at: int | None = None


class AdminListProductsResponse(BaseModel):
    products: list[AdminProductItem]


class AdminGetProductDetailResponse(BaseModel):
    product: AdminProductItem


class AdminUpsertProductRequest(BaseModel):
    name: str = Field(min_length=1)
    price: str = Field(min_length=1)
    img: str = Field(min_length=1)
    desc: str = Field(min_length=1)
    category: ProductCategory
    status: ProductStatus = "draft"
    sort_order: int = 0


class AdminUpdateProductStatusRequest(BaseModel):
    status: ProductStatus
