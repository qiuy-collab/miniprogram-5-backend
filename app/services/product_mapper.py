from app.core.config import settings
from app.models.product import Product


ABSOLUTE_URL_PREFIXES = ("http://", "https://")
LOCAL_ASSET_PREFIXES = ("/images/", "images/")


def normalize_product_image_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return raw
    if raw.startswith(ABSOLUTE_URL_PREFIXES) or raw.startswith(LOCAL_ASSET_PREFIXES):
        return raw

    public_base_url = settings.public_base_url.rstrip("/")
    media_url_path = settings.media_url_path.rstrip("/")

    if raw.startswith(f"{media_url_path}/"):
        return f"{public_base_url}{raw}"
    if raw.startswith("/"):
        return f"{public_base_url}{raw}"

    normalized_path = raw.lstrip("/")
    return f"{public_base_url}{media_url_path}/{normalized_path}"


def to_product_payload(row: Product) -> dict:
    return {
        "id": str(row.id),
        "name": row.name,
        "price": row.price,
        "img": normalize_product_image_url(row.img),
        "desc": row.description,
        "category": row.category,
    }
