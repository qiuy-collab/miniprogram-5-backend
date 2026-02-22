from pydantic import BaseModel, Field

from app.schemas.catalog import Product


class FavoriteItem(BaseModel):
    product: Product
    count: int = Field(ge=1)
    addedAt: int


class ListFavoritesResponse(BaseModel):
    items: list[FavoriteItem]


class AddFavoriteRequest(BaseModel):
    productId: str
    countDelta: int = Field(default=1, ge=1)


class AddFavoriteResponse(BaseModel):
    item: FavoriteItem
    totalCount: int


class RemoveFavoriteResponse(BaseModel):
    removed: bool


class ClearFavoritesResponse(BaseModel):
    cleared: bool


class BatchRemoveFavoritesRequest(BaseModel):
    productIds: list[str]


class BatchRemoveFavoritesResponse(BaseModel):
    removedIds: list[str]
