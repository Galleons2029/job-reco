# -*- coding: utf-8 -*-
# @Time    : 2024/11/28 14:37
# @Author  : Galleons
# @File    : category_api.py

"""
这里是文件说明
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime

from qdrant_client import models
import logging
from app.db.qdrant import QdrantClientManager
from app.config import settings

from app.db.models.jobs import (
    Bilateral_delete_record,
)
from app.utils.embeddings import vectorize

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

COLLECTION_NAME = settings.COLLECTION_TEST

class job_category(BaseModel):
    first_category_id: int
    first_category: str
    second_category_id: int
    second_category: str
    position_id: int
    position_name: str

class job_info(BaseModel):
    publish_id: int = Field(frozen=True, description="职位ID(不可更改)")

    # 职位详情
    job_name: str = Field(..., min_length=1, max_length=100, description="职位名称")
    job_require: str = Field(..., min_length=0, description="职位要求")
    job_descript: str = Field(..., min_length=0, description="职位描述")
    job_desc: Optional[str] = Field(None, description="职位描述(备用)")
    job_other: Optional[str] = Field(None, description="职位其他描述")



@router.post("/category_to_jobs", response_model=List[int])
async def category_to_jobs(category_id: int) -> List[int]:
    """
    根据职业类别ID推荐相关职位

    Args:

        category_id (int): 职业类别ID

    Returns:

        List[int]: 推荐职位ID列表，最多返回5个职位

    Raises:

        HTTPException:
            - 503: Qdrant服务不可用
            - 500: 服务器内部错误
    
    Description:

        - 通过职业类别的描述向量，在职位库中查找相似的职位
        - 仅返回未过期、已发布且状态正常的职位
        - 相似度阈值设置为0.5
    """
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    with QdrantClientManager.get_client_context() as qdrant_client:

        try:
            point = qdrant_client.retrieve(
                collection_name="job_category",
                ids=[category_id],
                with_payload=False,
                with_vectors=True,
            )

            description_vector = point[0].vector['description']

            _jobs = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=description_vector,  # <--- Dense vector
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(key="end_time",
                                              range=models.Range(gte=datetime.datetime.now().timestamp(), ), ),
                        models.FieldCondition(key='is_publish', match=models.MatchValue(value=1)),
                        models.FieldCondition(key='job_status', range=models.Range(gt=0)),
                    ],
                ),
                using='job_descript',
                score_threshold=0.5,
                with_payload=["publish_id"],
                limit=5  # 限制返回结果的数量
            ).points
            job_ids = [publish_id.payload['publish_id'] for publish_id in _jobs]

            return job_ids

        except Exception as e:
            logger.error(f"处理根据生涯职位推荐岗位请求时出错: {str(e)}")


@router.post("/jobs_to_category", response_model=job_category)
async def jobs_to_category(job: job_info) -> job_category:
    """
    根据职位信息推荐最匹配的职业类别

    Args:

        job (job_info): 职位信息对象，包含：
            - publish_id: 职位ID
            - job_name: 职位名称
            - job_require: 职位要求
            - job_descript: 职位描述
            - job_desc: 职位描述(备用)
            - job_other: 其他描述

    Returns:

        job_category: 推荐的职业类别信息，包含：
            - first_category_id: 一级类别ID
            - first_category: 一级类别名称
            - second_category_id: 二级类别ID
            - second_category: 二级类别名称
            - position_id: 职位ID
            - position_name: 职位名称

    Raises:

        HTTPException:
            - 503: Qdrant服务不可用
            - 500: 服务器内部错误

    Description:

        - 基于职位名称的向量表示查找最匹配的职业类别
        - 仅返回相似度最高的一个职业类别
    """
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            point = qdrant_client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=[job.publish_id],
                with_payload=False,
                with_vectors=True,
            )
            
            if not point:
                job_name_vector = await vectorize(job.job_name) # 如果没有找到对应的点

            else:
                job_name_vector = point[0].vector['job_name']

            _category = qdrant_client.query_points(
                collection_name="job_category",
                query=job_name_vector,
                using='position_name',
                # with_payload=["position_id"],
                limit=1
            ).points

            # category_ids = [category_id.payload['position_id'] for category_id in _category]
            return job_category(
                first_category_id=_category[0].payload['first_category_id'],
                first_category=_category[0].payload['first_category'],
                second_category_id=_category[0].payload['second_category_id'],
                second_category=_category[0].payload['second_category'],
                position_id=_category[0].payload['position_id'],
                position_name=_category[0].payload['position_name'],
            )  # 正常返回结果

        except Exception as e:
            logger.error(f"推荐生涯职位时请求时出错: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"处理请求时发生错误: {str(e)}"
            )
