from app.models.product import Product


def to_product_payload(row: Product) -> dict:
    return {
        "id": str(row.id),
        "name": row.name,
        "price": row.price,
        "img": row.img,
        "desc": row.description,
        "category": row.category,
    }
