from fastapi import APIRouter, Depends

from app.auth.admin_deps import get_current_admin_user_id
from app.auth.deps import get_current_user_id
from app.schemas.profile import (
    AdminGetUserDetailResponse,
    AdminListUsersResponse,
    GetProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("/profile", response_model=GetProfileResponse)
def get_profile(user_id: str = Depends(get_current_user_id)):
    return ProfileService.get_profile(user_id)


@router.put("/profile", response_model=UpdateProfileResponse)
def update_profile(payload: UpdateProfileRequest, user_id: str = Depends(get_current_user_id)):
    return ProfileService.update_profile(user_id, payload.model_dump())


@router.get("/admin/users", response_model=AdminListUsersResponse)
def admin_list_users(admin_user_id: str = Depends(get_current_admin_user_id)):
    return ProfileService.admin_list_users()


@router.get("/admin/users/{user_id}", response_model=AdminGetUserDetailResponse)
def admin_get_user_detail(user_id: str, admin_user_id: str = Depends(get_current_admin_user_id)):
    return ProfileService.admin_get_user_detail(user_id)
