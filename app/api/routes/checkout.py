from fastapi import APIRouter, Depends

from app.auth.deps import get_current_user_id
from app.schemas.checkout import (
    ClearSessionResponse,
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse,
    GetActiveSessionResponse,
)
from app.services.checkout_service import CheckoutService

router = APIRouter()


@router.post("/checkout/session", response_model=CreateCheckoutSessionResponse)
def create_checkout_session(payload: CreateCheckoutSessionRequest, user_id: str = Depends(get_current_user_id)):
    return CheckoutService.create_session(user_id, payload.source, payload.model_dump()["items"])


@router.get("/checkout/session", response_model=GetActiveSessionResponse)
def get_active_session(user_id: str = Depends(get_current_user_id)):
    return CheckoutService.get_active_session(user_id)


@router.delete("/checkout/session", response_model=ClearSessionResponse)
def clear_checkout_session(user_id: str = Depends(get_current_user_id)):
    return CheckoutService.clear_session(user_id)
