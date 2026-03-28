from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status

from app.auth.admin_deps import get_current_admin_user_id
from app.schemas.admin import (
    AdminCurrentUserResponse,
    AdminDashboardResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMediaListResponse,
    AdminUploadMediaResponse,
)
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


@router.get(
    "/media",
    response_model=AdminMediaListResponse,
    responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def list_media_assets(admin_user_id: str = Depends(get_current_admin_user_id)):
    return AdminService.list_media_assets()


@router.post(
    "/media/upload",
    response_model=AdminUploadMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_media_asset(
    file: UploadFile = File(...),
    alt_text: str = Form(default=""),
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return await AdminService.upload_media_asset(file, admin_user_id, alt_text)


@router.delete(
    "/media/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def delete_media_asset(asset_id: str, admin_user_id: str = Depends(get_current_admin_user_id)):
    AdminService.delete_media_asset(asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
