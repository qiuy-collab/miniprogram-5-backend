from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.errors.exceptions import AppError
from app.errors.handlers import app_error_handler, unknown_error_handler, validation_error_handler

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

uploads_path = settings.uploads_path
if not uploads_path.is_absolute():
    uploads_path = Path(__file__).resolve().parents[2] / uploads_path
uploads_path.mkdir(parents=True, exist_ok=True)

app.mount(settings.media_url_path, StaticFiles(directory=uploads_path), name="uploads")
app.include_router(api_router)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unknown_error_handler)


@app.get("/healthz")
def healthz():
    return {"ok": True}
