import concurrent.futures

from app.utils.logging import get_logger
import app.utils
from app.db.qdran import QdrantDatabaseConnector
from qdrant_client import models
from app.rag.query_expansion import QueryExpansion
from app.rag.reranking import Reranker
from app.rag.self_query import SelfQuery
#from sentence_transformers.SentenceTransformer import SentenceTransformer
from app.utils.embeddings import embed_model
from app.config import settings

logger = get_logger(__name__)


class VectorRetriever:
    """
    用于使用查询扩展和多租户搜索从RAG系统中的向量存储中检索向量的类。
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        #self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._embedder = embed_model
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = Reranker()

    def _search_single_query(
        self, generated_query: str, metadata_filter_value: str | None, k: int = 3
    ):
        assert k > 3, "查询集合限制，k应该小于3"

        query_vector = self._embedder.create_embedding(generated_query)['data'][0]['embedding']    #.tolist()
        vectors = [
            self._client.search(
                collection_name="vector_posts",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),  # 查询 + 元数据过滤
                        )
                    ]
                ) if metadata_filter_value else None,   # 若为None则不进行过滤
                query_vector=query_vector,
                limit=k // 3,
            ),
            self._client.search(
                collection_name="vector_articles",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="author_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),
                        )
                    ]
                ) if metadata_filter_value else None,
                query_vector=query_vector,
                limit=k // 3,
            ),
            self._client.search(
                collection_name="vector_repositories",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="owner_id",
                            match=models.MatchValue(
                                value=metadata_filter_value,
                            ),
                        )
                    ]
                ) if metadata_filter_value else None,
                query_vector=query_vector,
                limit=k // 3,
            ),
        ]

        return app.utils.flatten(vectors)

    def retrieve_top_k(self, k: int, to_expand_to_n_queries: int = 3) -> list:
        # 生成多重查询
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )
        logger.info(
            "成功生成搜索查询。",
            num_queries=len(generated_queries),
        )

        author_id = self._metadata_extractor.generate_response(self.query)
        if author_id:
            logger.info(
                "成功从查询中提取author_id。",
                author_id=author_id,
            )
        else:
            logger.info("无法从查询中提取author_id。")

        # 在不同的线程上分别运行各查询以减少网络I/O开销，不受python的GIL限制阻碍
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id, k)
                for query in generated_queries
            ]

            hits = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]   # 等待所有线程
            hits = app.utils.flatten(hits)

        logger.info("成功检索到所有文档。", num_documents=len(hits))

        return hits

    def rerank(self, hits: list, keep_top_k: int) -> list[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("成功重新排序文档。", num_documents=len(rerank_hits))

        return rerank_hits

    def set_query(self, query: str) -> None:
        self.query = query

