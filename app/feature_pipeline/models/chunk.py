from typing import Optional

from app.feature_pipeline.models.base import DataModel


class PostChunkModel(DataModel):
    entry_id: str
    platform: str
    chunk_id: str
    chunk_content: str
    author_id: str | None = None
    image: Optional[str] = None
    type: str


class ArticleChunkModel(DataModel):
    entry_id: str
    platform: str
    link: str
    chunk_id: str
    chunk_content: str
    author_id: str | None = None
    type: str


class RepositoryChunkModel(DataModel):
    entry_id: str
    name: str
    link: str
    chunk_id: str
    chunk_content: str
    owner_id: str
    type: str
