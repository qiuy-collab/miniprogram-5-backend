from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.catalog import Product


CheckoutSource = Literal["favorites", "product"]


class CheckoutItem(BaseModel):
    product: Product
    count: int = Field(ge=1)


class CheckoutSession(BaseModel):
    source: CheckoutSource
    items: list[CheckoutItem]
    createdAt: int


class CreateCheckoutItemRequest(BaseModel):
    productId: str
    count: int = Field(ge=1)


class CreateCheckoutSessionRequest(BaseModel):
    source: CheckoutSource
    items: list[CreateCheckoutItemRequest]


class CreateCheckoutSessionResponse(BaseModel):
    session: CheckoutSession


class GetActiveSessionResponse(BaseModel):
    session: CheckoutSession | None


class ClearSessionResponse(BaseModel):
    cleared: bool
