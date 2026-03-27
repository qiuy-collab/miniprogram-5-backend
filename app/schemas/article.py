from pydantic import BaseModel


class ArticleSummary(BaseModel):
    id: str
    date: str
    title: str
    desc: str


class ArticleDetail(ArticleSummary):
    content_markdown: str
    content_html: str


class ListArticlesResponse(BaseModel):
    articles: list[ArticleSummary]


class GetArticleDetailResponse(BaseModel):
    article: ArticleDetail
