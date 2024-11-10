# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 16:21
# @Author  : Galleons
# @File    : students_api_v2.py

"""
这里是文件说明
"""
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse


from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient
from app.api.v2.dependencies.by_qdrant import get_qdrant_client
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

router = APIRouter()


@router.get("/search")
async def search_items(
        query: str,
        qdrant_client: QdrantClient = Depends(get_qdrant_client)
):
    try:
        # 使用注入的qdrant客户端
        search_result = qdrant_client.search(
            collection_name="my_collection",
            query_vector=[0.2, 0.1, 0.9],
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=query)
                    )
                ]
            )
        )
        return {"results": search_result}
    except Exception as e:
        logger.error(f"Search operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


# 使用示例
if __name__ == "__main__":
    # 方式1：直接获取客户端
    client = QdrantClientManager.get_client()

    # 方式2：使用上下文管理器
    with QdrantClientManager.get_client_context() as client:
        collections = client.get_collections()
        print(collections)