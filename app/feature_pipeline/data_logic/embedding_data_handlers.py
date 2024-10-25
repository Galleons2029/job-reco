from abc import ABC, abstractmethod

from app.feature_pipeline.models.base import DataModel
from app.feature_pipeline.models.chunk import ArticleChunkModel, PostChunkModel, RepositoryChunkModel, DocumentChunkModel
from app.feature_pipeline.models.embedded_chunk import (
    ArticleEmbeddedChunkModel,
    PostEmbeddedChunkModel,
    RepositoryEmbeddedChunkModel,
    DocumentEmbeddedChunkModel,
)
from app.utils.embeddings import embedd_text

class EmbeddingDataHandler(ABC):
    """
    所有嵌入数据处理程序的抽象类。
    所有嵌入步骤的数据转换逻辑都在这里完成。
    """

    @abstractmethod
    def embedd(self, data_model: DataModel) -> DataModel:
        pass


class PostEmbeddingHandler(EmbeddingDataHandler):
    def embedd(self, data_model: PostChunkModel) -> PostEmbeddedChunkModel:
        return PostEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            chunk_id=data_model.chunk_id,
            chunk_content=data_model.chunk_content,
            embedded_content=embedd_text(data_model.chunk_content),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class ArticleEmbeddingHandler(EmbeddingDataHandler):
    def embedd(self, data_model: ArticleChunkModel) -> ArticleEmbeddedChunkModel:
        return ArticleEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.link,
            chunk_content=data_model.chunk_content,
            chunk_id=data_model.chunk_id,
            embedded_content=embedd_text(data_model.chunk_content),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class RepositoryEmbeddingHandler(EmbeddingDataHandler):
    def embedd(self, data_model: RepositoryChunkModel) -> RepositoryEmbeddedChunkModel:
        return RepositoryEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            name=data_model.name,
            link=data_model.link,
            chunk_id=data_model.chunk_id,
            chunk_content=data_model.chunk_content,
            embedded_content=embedd_text(data_model.chunk_content),
            owner_id=data_model.owner_id,
            type=data_model.type,
        )


#自定义类
class DocumentEmbeddingHandler(EmbeddingDataHandler):
    def embedd(self, data_model: DocumentChunkModel) -> DocumentEmbeddedChunkModel:
        return DocumentEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            knowledge_id=data_model.knowledge_id,
            doc_id=data_model.doc_id,
            path=data_model.path,
            chunk_id=data_model.chunk_id,
            chunk_content=data_model.chunk_content,
            embedded_content=embedd_text(data_model.chunk_content),
            user_id=data_model.user_id,
            type=data_model.type,
        )