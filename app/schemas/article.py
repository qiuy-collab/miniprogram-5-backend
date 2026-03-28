from pydantic import BaseModel, Field


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


class AdminArticleListItem(BaseModel):
    id: str
    date: str
    title: str
    desc: str
    status: str
    published_at: int | None


class AdminArticleDetail(BaseModel):
    id: str
    date: str
    title: str
    desc: str
    status: str
    content_markdown: str
    content_html: str
    published_at: int | None


class AdminListArticlesResponse(BaseModel):
    articles: list[AdminArticleListItem]


class AdminGetArticleDetailResponse(BaseModel):
    article: AdminArticleDetail


class AdminUpsertArticleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    desc: str = Field(min_length=1, max_length=300)
    date: str = Field(min_length=1, max_length=40)
    content_markdown: str = Field(default="")
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")


class AdminUpsertArticleResponse(BaseModel):
    article: AdminArticleDetail


class AdminArticleStatusRequest(BaseModel):
    status: str = Field(pattern="^(published|draft|archived)$")


class AdminArticleStatusResponse(BaseModel):
    article: AdminArticleDetail
