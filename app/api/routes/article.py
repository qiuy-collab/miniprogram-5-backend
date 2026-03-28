from fastapi import APIRouter, Depends, status

from app.auth.admin_deps import get_current_admin_user_id
from app.auth.deps import get_current_user_id
from app.schemas.article import (
    AdminArticleStatusRequest,
    AdminArticleStatusResponse,
    AdminGetArticleDetailResponse,
    AdminListArticlesResponse,
    AdminUpsertArticleRequest,
    AdminUpsertArticleResponse,
    GetArticleDetailResponse,
    ListArticlesResponse,
)
from app.schemas.common import ErrorResponse
from app.services.article_service import ArticleService

router = APIRouter()


@router.get("/articles", response_model=ListArticlesResponse)
def list_articles():
    return ArticleService.list_articles()


@router.get("/articles/{article_id}", response_model=GetArticleDetailResponse)
def get_article_detail(article_id: str):
    return ArticleService.get_article_detail(article_id)


@router.get(
    "/admin/articles",
    response_model=AdminListArticlesResponse,
    responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_list_articles(admin_user_id: str = Depends(get_current_admin_user_id)):
    return ArticleService.admin_list_articles()


@router.get(
    "/admin/articles/{article_id}",
    response_model=AdminGetArticleDetailResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_get_article_detail(article_id: str, admin_user_id: str = Depends(get_current_admin_user_id)):
    return ArticleService.admin_get_article_detail(article_id)


@router.post(
    "/admin/articles",
    response_model=AdminUpsertArticleResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_create_article(payload: AdminUpsertArticleRequest, admin_user_id: str = Depends(get_current_admin_user_id)):
    return ArticleService.admin_save_article(
        article_id=None,
        title=payload.title,
        desc=payload.desc,
        date=payload.date,
        content_markdown=payload.content_markdown,
        status=payload.status,
        admin_user_id=admin_user_id,
    )


@router.put(
    "/admin/articles/{article_id}",
    response_model=AdminUpsertArticleResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_update_article(
    article_id: str,
    payload: AdminUpsertArticleRequest,
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return ArticleService.admin_save_article(
        article_id=article_id,
        title=payload.title,
        desc=payload.desc,
        date=payload.date,
        content_markdown=payload.content_markdown,
        status=payload.status,
        admin_user_id=admin_user_id,
    )


@router.patch(
    "/admin/articles/{article_id}/status",
    response_model=AdminArticleStatusResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def admin_update_article_status(
    article_id: str,
    payload: AdminArticleStatusRequest,
    admin_user_id: str = Depends(get_current_admin_user_id),
):
    return ArticleService.admin_update_article_status(article_id, payload.status, admin_user_id)
