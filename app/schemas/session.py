from pydantic import BaseModel, Field


class AcquireSessionRequest(BaseModel):
    loginCode: str = Field(min_length=1)


class AcquireSessionResponse(BaseModel):
    sessionReady: bool
    sessionExpiresAt: int
    accessToken: str
