import uuid

from app.services.article_service import render_article_markdown


def test_render_article_markdown_renders_heading_and_paragraph():
    html = render_article_markdown("# 标题\n\n正文第一段")

    assert "<h1>标题</h1>" in html
    assert "<p>正文第一段</p>" in html


def test_render_article_markdown_renders_image_with_normalized_upload_url():
    html = render_article_markdown("![春茶](articles/spring.jpg \"春茶图\")")

    assert 'src="https://api.longxingtea.xyz/uploads/articles/spring.jpg"' in html
    assert 'alt="春茶"' in html
    assert 'title="春茶图"' in html


def test_render_article_markdown_renders_lists_and_blockquote():
    html = render_article_markdown("- 一\n- 二\n\n> 引言")

    assert "<ul><li>一</li><li>二</li></ul>" in html
    assert "<blockquote>引言</blockquote>" in html


def test_get_article_detail_returns_markdown_and_html(monkeypatch):
    from app.services import article_service

    article = type("Article", (), {
        "id": uuid.uuid4(),
        "date": "岁序·立春",
        "title": "春茶开采记",
        "description": "关于山野与新芽的故事。",
    })()
    paragraphs = [
        type("Paragraph", (), {"content": "# 标题"})(),
        type("Paragraph", (), {"content": "![图](articles/a.jpg)"})(),
        type("Paragraph", (), {"content": "正文"})(),
    ]

    class FakeSession:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeRepository:
        def __init__(self, _db):
            pass

        def get_article_by_id(self, _article_id):
            return article

        def get_article_markdown(self, _article):
            return "# 标题\n\n![图](articles/a.jpg)\n\n正文"
    monkeypatch.setattr(article_service, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(article_service, "ArticleRepository", FakeRepository)

    payload = article_service.ArticleService.get_article_detail(str(article.id))

    assert payload["article"]["content_markdown"] == "# 标题\n\n![图](articles/a.jpg)\n\n正文"
    assert '<img src="https://api.longxingtea.xyz/uploads/articles/a.jpg" alt="图" />' in payload["article"]["content_html"]
    assert "<p>正文</p>" in payload["article"]["content_html"]
