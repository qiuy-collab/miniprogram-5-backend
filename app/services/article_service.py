from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.article_repository import ArticleRepository
from app.services.utils import ensure_str_uuid


class ArticleService:
    @staticmethod
    def list_articles() -> dict:
        try:
            with SessionLocal() as db:
                rows = ArticleRepository(db).list_articles()
            return {
                "articles": [
                    {
                        "id": str(r.id),
                        "date": r.date,
                        "title": r.title,
                        "desc": r.description,
                    }
                    for r in rows
                ]
            }
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "文章服务暂不可用", 503)

    @staticmethod
    def get_article_detail(article_id: str) -> dict:
        try:
            article_id = ensure_str_uuid(article_id)
            with SessionLocal() as db:
                repo = ArticleRepository(db)
                article = repo.get_article_by_id(article_id)
                if not article:
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "文章不存在", 404)
                paragraphs = repo.list_contents(article_id)

            return {
                "article": {
                    "id": str(article.id),
                    "date": article.date,
                    "title": article.title,
                    "desc": article.description,
                    "content": [p.content for p in paragraphs],
                }
            }
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "文章ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "文章服务暂不可用", 503)
