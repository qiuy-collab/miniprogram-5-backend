from fastapi import APIRouter, Depends

from app.auth.admin_deps import get_current_admin_user_id
from app.auth.deps import get_current_user_id
from app.schemas.booking import (
    AdminGetBookingDetailResponse,
    AdminListBookingsResponse,
    AdminUpdateBookingRequest,
    CreateBookingRequest,
    CreateBookingResponse,
    ListBookingsResponse,
)
from app.services.booking_service import BookingService

router = APIRouter()


@router.post("/bookings", response_model=CreateBookingResponse)
def create_booking(payload: CreateBookingRequest, user_id: str = Depends(get_current_user_id)):
    return BookingService.create_booking(user_id, payload.model_dump())


@router.get("/bookings", response_model=ListBookingsResponse)
def list_bookings(user_id: str = Depends(get_current_user_id)):
    return BookingService.list_bookings(user_id)


@router.get("/admin/bookings", response_model=AdminListBookingsResponse)
def admin_list_bookings(admin_user_id: str = Depends(get_current_admin_user_id)):
    return BookingService.admin_list_bookings()


@router.get("/admin/bookings/{booking_id}", response_model=AdminGetBookingDetailResponse)
def admin_get_booking_detail(booking_id: str, admin_user_id: str = Depends(get_current_admin_user_id)):
    return BookingService.admin_get_booking_detail(booking_id)


@router.put("/admin/bookings/{booking_id}", response_model=AdminGetBookingDetailResponse)
def admin_update_booking(
    booking_id: str,
    payload: AdminUpdateBookingRequest,
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return BookingService.admin_update_booking(booking_id, payload.status_code, payload.internal_note, admin_user_id)
