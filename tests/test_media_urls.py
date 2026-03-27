import uuid

from fastapi.testclient import TestClient
from starlette.staticfiles import StaticFiles

from app.main import app
from app.models.product import Product
from app.services.product_mapper import normalize_product_image_url


def make_product(img: str) -> Product:
    return Product(
        id=uuid.uuid4(),
        name="龙井",
        price="88.00",
        img=img,
        description="desc",
        category="tea",
    )


def test_normalize_product_image_url_keeps_absolute_url():
    assert normalize_product_image_url("https://cdn.example.com/products/a.jpg") == "https://cdn.example.com/products/a.jpg"


def test_normalize_product_image_url_prefixes_uploads_path():
    assert normalize_product_image_url("products/a.jpg") == "https://api.longxingtea.xyz/uploads/products/a.jpg"


def test_normalize_product_image_url_keeps_local_assets():
    assert normalize_product_image_url("/images/local.png") == "/images/local.png"


def test_to_product_api_response_returns_normalized_image(monkeypatch):
    from app.services import catalog_service

    product = make_product("products/a.jpg")

    class FakeSession:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeRepository:
        def __init__(self, _db):
            pass

        def list(self, category=None):
            return [product]

    monkeypatch.setattr(catalog_service, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(catalog_service, "ProductRepository", FakeRepository)

    client = TestClient(app)
    response = client.get("/api/v1/catalog/products")

    assert response.status_code == 200
    payload = response.json()
    assert payload["products"][0]["img"] == "https://api.longxingtea.xyz/uploads/products/a.jpg"


def test_staticfiles_serves_upload_file(tmp_path):
    uploads_dir = tmp_path / "uploads"
    products_dir = uploads_dir / "products"
    products_dir.mkdir(parents=True)
    image_file = products_dir / "test.txt"
    image_file.write_text("ok", encoding="utf-8")

    static_app = StaticFiles(directory=uploads_dir)
    client = TestClient(static_app)
    response = client.get("/products/test.txt")

    assert response.status_code == 200
    assert response.text == "ok"
