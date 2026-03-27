from fastapi import APIRouter

from app.api.routes import admin, article, booking, catalog, checkout, favorite, payment, profile, session

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(session.router, tags=["session"])
api_router.include_router(catalog.router, tags=["catalog"])
api_router.include_router(article.router, tags=["article"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(favorite.router, tags=["favorite"])
api_router.include_router(booking.router, tags=["booking"])
api_router.include_router(checkout.router, tags=["checkout"])
api_router.include_router(payment.router, tags=["payment"])
api_router.include_router(admin.router, tags=["admin"])
