from pydantic import BaseModel, Field, field_validator


class ProfileInfo(BaseModel):
    name: str = Field(min_length=1, max_length=10)
    city: str = Field(default="", max_length=12)
    phone: str
    motto: str = Field(default="", max_length=40)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if len(v) != 11 or not v.isdigit() or not v.startswith("1"):
            raise ValueError("invalid phone")
        return v


class GetProfileResponse(BaseModel):
    profile: ProfileInfo


class UpdateProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=10)
    city: str = Field(default="", max_length=12)
    phone: str
    motto: str = Field(default="", max_length=40)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if len(v) != 11 or not v.isdigit() or not v.startswith("1"):
            raise ValueError("invalid phone")
        return v


class UpdateProfileResponse(BaseModel):
    profile: ProfileInfo
    updatedAt: int


class AdminUserProfileItem(BaseModel):
    user_id: str
    created_at: int
    profile: ProfileInfo


class AdminListUsersResponse(BaseModel):
    records: list[AdminUserProfileItem]


class AdminGetUserDetailResponse(BaseModel):
    record: AdminUserProfileItem
