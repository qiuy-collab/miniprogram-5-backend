from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError


def _resolve_validation_code(exc: RequestValidationError) -> tuple[ErrorCode, str]:
    errors = exc.errors()
    if not errors:
        return ErrorCode.E_INPUT_FORMAT_INVALID, "请求参数不合法"

    first = errors[0]
    error_type = first.get("type", "")

    if "missing" in error_type:
        return ErrorCode.E_INPUT_REQUIRED, "缺少必填参数"
    if "enum" in error_type or "literal_error" in error_type:
        return ErrorCode.E_ENUM_VALUE_INVALID, "枚举参数不合法"
    if "too_long" in error_type or "too_short" in error_type:
        return ErrorCode.E_INPUT_LENGTH_EXCEEDED, "字段长度不合法"
    if "string_pattern_mismatch" in error_type:
        return ErrorCode.E_INPUT_FORMAT_INVALID, "字段格式不合法"

    return ErrorCode.E_INPUT_FORMAT_INVALID, "请求参数不合法"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code.value, "message": exc.message})


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    code, message = _resolve_validation_code(exc)
    return JSONResponse(status_code=400, content={"code": code.value, "message": message})


async def unknown_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"code": ErrorCode.E_SERVICE_UNAVAILABLE.value, "message": "服务暂不可用"},
    )
