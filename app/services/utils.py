import uuid
from datetime import datetime, timezone


def now_ms() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)


def new_uuid() -> str:
    return str(uuid.uuid4())


def ensure_str_uuid(value: str) -> str:
    return str(uuid.UUID(str(value)))
