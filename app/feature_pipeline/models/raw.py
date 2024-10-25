from typing import Optional

from app.feature_pipeline.models.base import DataModel


class RepositoryRawModel(DataModel):
    name: str
    link: str
    content: dict
    owner_id: str| None = None


class ArticleRawModel(DataModel):
    platform: str
    link: str
    content: dict
    author_id: str| None = None


class PostsRawModel(DataModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None


class JobsRawModel(DataModel):
    name: str
    category: str


    platform: str
    content: dict


class DocumentRawModel(DataModel):
    knowledge_id: str
    doc_id: str
    path: str
    content: dict
    user_id: str | None = None
    image: Optional[str] = None
