from fastapi import APIRouter

from app.schemas.article import GetArticleDetailResponse, ListArticlesResponse
from app.services.article_service import ArticleService

router = APIRouter()


@router.get("/articles", response_model=ListArticlesResponse)
def list_articles():
    return ArticleService.list_articles()


@router.get("/articles/{article_id}", response_model=GetArticleDetailResponse)
def get_article_detail(article_id: str):
    return ArticleService.get_article_detail(article_id)
