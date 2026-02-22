from fastapi import APIRouter, Depends

from app.auth.deps import get_current_user_id
from app.schemas.booking import CreateBookingRequest, CreateBookingResponse, ListBookingsResponse
from app.services.booking_service import BookingService

router = APIRouter()


@router.post("/bookings", response_model=CreateBookingResponse)
def create_booking(payload: CreateBookingRequest, user_id: str = Depends(get_current_user_id)):
    return BookingService.create_booking(user_id, payload.model_dump())


@router.get("/bookings", response_model=ListBookingsResponse)
def list_bookings(user_id: str = Depends(get_current_user_id)):
    return BookingService.list_bookings(user_id)
