from fastapi import APIRouter

from app.schemas.session import AcquireSessionRequest, AcquireSessionResponse
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/sessions/acquire", response_model=AcquireSessionResponse)
def acquire_session(payload: AcquireSessionRequest):
    return SessionService.acquire_session(payload.loginCode)
