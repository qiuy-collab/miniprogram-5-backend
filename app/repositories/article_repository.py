from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.article_content import ArticleContent


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_articles(self) -> list[Article]:
        stmt = select(Article).order_by(Article.date.desc(), Article.id.desc())
        return list(self.db.scalars(stmt).all())

    def list_articles_for_admin(self) -> list[Article]:
        stmt = select(Article).order_by(Article.date.desc(), Article.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_article_by_id(self, article_id: str) -> Article | None:
        aid = uuid.UUID(article_id)
        stmt = select(Article).where(Article.id == aid).limit(1)
        return self.db.scalars(stmt).first()

    def list_contents(self, article_id: str) -> list[ArticleContent]:
        aid = uuid.UUID(article_id)
        stmt = (
            select(ArticleContent)
            .where(ArticleContent.article_id == aid)
            .order_by(ArticleContent.sort_order)
        )
        return list(self.db.scalars(stmt).all())

    def get_article_markdown(self, article: Article) -> str:
        if article.content_markdown:
            return article.content_markdown
        contents = self.list_contents(str(article.id))
        return "\n\n".join(item.content for item in contents)

    def create_article(
        self,
        *,
        title: str,
        description: str,
        date: str,
        content_markdown: str,
        status: str,
        published_at: int | None,
        admin_user_id: str,
    ) -> Article:
        aid = uuid.UUID(admin_user_id)
        article = Article(
            title=title,
            description=description,
            date=date,
            content_markdown=content_markdown,
            status=status,
            published_at=published_at,
            created_by_admin_id=aid,
            updated_by_admin_id=aid,
        )
        self.db.add(article)
        self.db.flush()
        return article

    def update_article(
        self,
        article: Article,
        *,
        title: str,
        description: str,
        date: str,
        content_markdown: str,
        status: str,
        published_at: int | None,
        admin_user_id: str,
    ) -> Article:
        article.title = title
        article.description = description
        article.date = date
        article.content_markdown = content_markdown
        article.status = status
        article.published_at = published_at
        article.updated_by_admin_id = uuid.UUID(admin_user_id)
        self.db.flush()
        return article
