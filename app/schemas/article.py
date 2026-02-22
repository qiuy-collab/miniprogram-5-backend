from pydantic import BaseModel


class ArticleSummary(BaseModel):
    id: str
    date: str
    title: str
    desc: str


class ArticleDetail(ArticleSummary):
    content: list[str]


class ListArticlesResponse(BaseModel):
    articles: list[ArticleSummary]


class GetArticleDetailResponse(BaseModel):
    article: ArticleDetail
