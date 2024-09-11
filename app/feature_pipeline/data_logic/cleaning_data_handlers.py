from abc import ABC, abstractmethod

from app.feature_pipeline.models.base import DataModel
from app.feature_pipeline.models.clean import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from app.feature_pipeline.models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel
from app.utils.cleaning import clean_text


class CleaningDataHandler(ABC):
    """
    所有数据清洗处理程序的抽象类。
    清洗步骤中所有的数据转换逻辑都在这里完成。
    """

    @abstractmethod
    def clean(self, data_model: DataModel) -> DataModel:
        pass


# 将原始数据模型映射到清理后的数据模型，都由一组Handler()类建模

class PostCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: PostsRawModel) -> PostCleanedModel:
        return PostCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            cleaned_content=clean_text("".join(data_model.content.values())),  # 完成清洗步骤
            author_id=data_model.author_id,
            image=data_model.image if data_model.image else None,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        return ArticleCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class RepositoryCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: RepositoryRawModel) -> RepositoryCleanedModel:
        return RepositoryCleanedModel(
            entry_id=data_model.entry_id,
            name=data_model.name,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            owner_id=data_model.owner_id,
            type=data_model.type,
        )
