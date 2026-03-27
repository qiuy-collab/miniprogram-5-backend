from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "contract-backend"
    app_env: str = "dev"
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    wechat_app_id: str
    wechat_app_secret: str
    wechat_login_timeout_seconds: int = 8
    wechat_mch_id: str | None = None
    wechat_mch_key: str | None = None
    wechat_pay_notify_url: str | None = None
    wechat_pay_body: str = "Long Xing Tea Order"
    session_ttl_seconds: int = 86400
    cors_allow_origins: str = "https://servicewechat.com"
    cors_allow_origin_regex: str = r"^https?://(127\.0\.0\.1|localhost):\d+$"
    public_base_url: str = "https://api.longxingtea.xyz"
    media_url_path: str = "/uploads"
    uploads_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig", extra="ignore")

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def uploads_path(self) -> Path:
        return Path(self.uploads_dir)


settings = Settings()
