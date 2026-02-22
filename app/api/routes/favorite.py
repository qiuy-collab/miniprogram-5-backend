from fastapi import APIRouter, Depends

from app.auth.deps import get_current_user_id
from app.schemas.favorite import (
    AddFavoriteRequest,
    AddFavoriteResponse,
    BatchRemoveFavoritesRequest,
    BatchRemoveFavoritesResponse,
    ClearFavoritesResponse,
    ListFavoritesResponse,
    RemoveFavoriteResponse,
)
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.get("/favorites", response_model=ListFavoritesResponse)
def list_favorites(user_id: str = Depends(get_current_user_id)):
    return FavoriteService.list_favorites(user_id)


@router.post("/favorites", response_model=AddFavoriteResponse)
def add_favorite(payload: AddFavoriteRequest, user_id: str = Depends(get_current_user_id)):
    return FavoriteService.add_favorite(user_id, payload.productId, payload.countDelta)


@router.delete("/favorites/{product_id}", response_model=RemoveFavoriteResponse)
def remove_favorite(product_id: str, user_id: str = Depends(get_current_user_id)):
    return FavoriteService.remove_favorite(user_id, product_id)


@router.delete("/favorites", response_model=ClearFavoritesResponse)
def clear_favorites(user_id: str = Depends(get_current_user_id)):
    return FavoriteService.clear_favorites(user_id)


@router.post("/favorites/batch-remove", response_model=BatchRemoveFavoritesResponse)
def batch_remove_favorites(payload: BatchRemoveFavoritesRequest, user_id: str = Depends(get_current_user_id)):
    return FavoriteService.batch_remove_favorites(user_id, payload.productIds)
