from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class AdminRoleItem(BaseModel):
    id: str
    code: str
    name: str


class AdminUserItem(BaseModel):
    id: str
    username: str
    display_name: str
    status: str
    roles: list[AdminRoleItem]


class AdminLoginResponse(BaseModel):
    accessToken: str
    admin_user: AdminUserItem


class AdminCurrentUserResponse(BaseModel):
    admin_user: AdminUserItem


class AdminDashboardSummary(BaseModel):
    draft_article_count: int
    published_article_count: int
    active_product_count: int
    pending_booking_count: int
    media_asset_count: int


class AdminDashboardResponse(BaseModel):
    summary: AdminDashboardSummary


class AdminMediaAssetItem(BaseModel):
    id: str
    storage_key: str
    url: str
    media_type: str
    mime_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None
    alt_text: str
    status: str
    created_at: str | None = None


class AdminMediaListResponse(BaseModel):
    assets: list[AdminMediaAssetItem]


class AdminUploadMediaResponse(BaseModel):
    asset: AdminMediaAssetItem
