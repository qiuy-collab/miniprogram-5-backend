from fastapi import APIRouter, Depends, status

from app.auth.admin_deps import get_current_admin_user_id
from app.schemas.admin import AdminCurrentUserResponse, AdminDashboardResponse, AdminLoginRequest, AdminLoginResponse
from app.schemas.common import ErrorResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/auth/login",
    response_model=AdminLoginResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_login(payload: AdminLoginRequest):
    return AdminService.login(payload.username, payload.password)


@router.get(
    "/me",
    response_model=AdminCurrentUserResponse,
    responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_admin_me(admin_user_id: str = Depends(get_current_admin_user_id)):
    return AdminService.get_current_admin(admin_user_id)


@router.get(
    "/dashboard/summary",
    response_model=AdminDashboardResponse,
    responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_dashboard_summary(admin_user_id: str = Depends(get_current_admin_user_id)):
    return AdminService.get_dashboard_summary()
