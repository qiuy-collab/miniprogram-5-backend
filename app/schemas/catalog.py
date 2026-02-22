from typing import Literal

from pydantic import BaseModel


ProductCategory = Literal["tea", "orchid", "course"]


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
