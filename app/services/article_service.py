from html import escape
import re

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.article_repository import ArticleRepository
from app.services.product_mapper import normalize_product_image_url
from app.services.utils import ensure_str_uuid

IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"(?P<title>[^\"]*)\")?\)")
LINK_PATTERN = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^)\s]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")


def _escape_inline(text: str) -> str:
    escaped = escape(text)
    return LINK_PATTERN.sub(
        lambda match: f'<a href="{escape(match.group("href"), quote=True)}">{escape(match.group("label"))}</a>',
        escaped,
    )


def _render_markdown_block(block: str) -> str:
    image_match = IMAGE_PATTERN.fullmatch(block.strip())
    if image_match:
        src = normalize_product_image_url(image_match.group("src"))
        alt = escape(image_match.group("alt"))
        title = image_match.group("title")
        title_attr = f' title="{escape(title, quote=True)}"' if title else ""
        return f'<img src="{escape(src, quote=True)}" alt="{alt}"{title_attr} />'

    heading_match = HEADING_PATTERN.match(block)
    if heading_match:
        level = len(heading_match.group(1))
        content = _escape_inline(heading_match.group(2).strip())
        return f"<h{level}>{content}</h{level}>"

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if lines and all(line.startswith(("- ", "* ")) for line in lines):
        items = "".join(f"<li>{_escape_inline(line[2:].strip())}</li>" for line in lines)
        return f"<ul>{items}</ul>"

    if lines and all(re.match(r"\d+\.\s+", line) for line in lines):
        items = "".join(f"<li>{_escape_inline(re.sub(r'^\d+\.\s+', '', line))}</li>" for line in lines)
        return f"<ol>{items}</ol>"

    if lines and all(line.startswith(">") for line in lines):
        content = "<br/>".join(_escape_inline(line.lstrip(">").strip()) for line in lines)
        return f"<blockquote>{content}</blockquote>"

    paragraphs = "<br/>".join(_escape_inline(line) for line in lines)
    return f"<p>{paragraphs}</p>"


def render_article_markdown(content_markdown: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", content_markdown.strip()) if block.strip()]
    if not blocks:
        return ""
    return "".join(_render_markdown_block(block) for block in blocks)


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
                content_markdown = repo.get_article_markdown(article)

            return {
                "article": {
                    "id": str(article.id),
                    "date": article.date,
                    "title": article.title,
                    "desc": article.description,
                    "content_markdown": content_markdown,
                    "content_html": render_article_markdown(content_markdown),
                }
            }
        except AppError:
            raise
        except ValueError:
            raise AppError(ErrorCode.E_INPUT_FORMAT_INVALID, "文章ID格式不合法", 400)
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "文章服务暂不可用", 503)
