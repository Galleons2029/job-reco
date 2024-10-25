from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.models import Batch
from app.utils.logging import get_logger
from app.db.qdran import QdrantDatabaseConnector
from app.feature_pipeline.models.base import VectorDBDataModel

logger = get_logger(__name__)

class QdrantOutput(DynamicSink):
    """
    Bytewax 类，用于连接 Qdrant 向量数据库。
    继承自 DynamicSink，因为能够创建不同的接收源（例如，向量和非向量集合）
    """

    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str):
        self._connection = connection
        self._sink_type = sink_type

        try:
            self._connection.get_collection(collection_name="cleaned_posts")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="cleaned_posts",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_posts"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_articles")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="cleaned_articles",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_articles"
            )

        try:
            self._connection.get_collection(collection_name="cleaned_repositories")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="cleaned_repositories",
            )

            self._connection.create_non_vector_collection(
                collection_name="cleaned_repositories"
            )

        try:
            self._connection.get_collection(collection_name="vector_posts")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="vector_posts",
            )

            self._connection.create_vector_collection(collection_name="vector_posts")

        try:
            self._connection.get_collection(collection_name="vector_articles")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="vector_articles",
            )

            self._connection.create_vector_collection(collection_name="vector_articles")

        try:
            self._connection.get_collection(collection_name="vector_repositories")
        except UnexpectedResponse:
            logger.info(
                "无法访问集合。正在创建一个新的集合...",
                collection_name="vector_repositories",
            )

            self._connection.create_vector_collection(
                collection_name="vector_repositories"
            )

    # 为每一个Bytewax工作器创建一个数据接收器
    def build(self, step_id: str, worker_index: int, worker_count: int) -> StatelessSinkPartition:
        if self._sink_type == "clean":
            return QdrantCleanedDataSink(connection=self._connection)
        elif self._sink_type == "vector":
            return QdrantVectorDataSink(connection=self._connection)
        else:
            raise ValueError(f"不支持的接收类型: {self._sink_type}")


class QdrantCleanedDataSink(StatelessSinkPartition):
    """
    自定义无状态工作器/分区
    继承Bytewax中的无服务分区（StatelessSinkPartition）
    """

    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    # 将数据序列化为Qdrant可接收类型
    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, data = zip(*payloads)
        if data[0]["type"] == "documents":
            # collection_name = data[0]["knowledge_id"]
            logger.info(
                "检测到知识库文档插入",
                data=data,
                num=len(ids),
            )
        else:
            collection_name = get_clean_collection(data_type=data[0]["type"])
            self._client.write_data(
                collection_name=collection_name,
                points=Batch(ids=ids, vectors={}, payloads=data),
            )
            logger.info(
                "成功插入请求的向量点",
                collection_name=collection_name,
                num=len(ids),
            )


class QdrantVectorDataSink(StatelessSinkPartition):
    """
    采用Qdrant的批处理一次性上传所有可用点，从而减少了网络I/O端的延迟
    """

    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, vectors, meta_data = zip(*payloads)
        if meta_data[0]["type"] == "documents":
            collection_name = f"zsk_{str(meta_data[0]['knowledge_id'])}"
            try:
                self._client.get_collection(collection_name=collection_name)
            except UnexpectedResponse:
                logger.info(
                    "未检测到知识库。正在创建一个新的知识库...",
                    collection_name=collection_name,
                )
                self._client.create_vector_collection(
                    collection_name=collection_name
                )
            logger.debug(
                "数据类型：",
                datamodels=meta_data,
            )
        else:
            collection_name = get_vector_collection(data_type=meta_data[0]["type"])
        self._client.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors=vectors, payloads=meta_data),
        )

        logger.info(
            "成功插入请求的向量点",
            collection_name=collection_name,
            num=len(ids),
        )

def get_clean_collection(data_type: str) -> str:
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"
    else:
        raise ValueError(f"不支持的数据类型: {data_type}")

def get_vector_collection(data_type: str) -> str:
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
    else:
        raise ValueError(f"不支持的数据类型: {data_type}")
