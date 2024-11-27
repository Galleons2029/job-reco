# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 14:30
# @Author  : Galleons
# @File    : jobs_api_v2.py

"""
岗位信息更新API
支持批量更新和删除岗位信息
"""

from fastapi import HTTPException, APIRouter, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential
from qdrant_client import models
import logging
from datetime import datetime
import time
from app.db.qdrant import QdrantClientManager
from app.db.models.jobs import JobUpdateItem, Jobs
from app.utils.embeddings import vectorize
from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

COLLECTION_NAME = settings.COLLECTION_TEST


class BatchUpdateResponse(BaseModel):
    """批量更新响应模型"""
    total_processed: int
    updated_count: int
    failed_count: int
    failed_updates: List[Dict[str, Any]] = Field(default_factory=list)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def batch_update_jobs(updates: List[JobUpdateItem]) -> tuple[int, List[Dict[str, Any]]]:
    """批量更新岗位信息
    
    Args:
        updates: 要更新的岗位信息列表
        
    Returns:
        tuple[int, List[Dict]]: (成功更新数量, 失败的更新记录列表)
    """
    updated_count = 0
    failed_updates = []
    
    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            # 过滤掉所有字段都为None的更新项
            valid_updates = []
            for job in updates:
                non_none_fields = job.get_non_none_fields()
                if len(non_none_fields) > 1:  # 至少要有publish_id和一个其他字段
                    valid_updates.append((job, non_none_fields))
                else:
                    failed_updates.append({
                        "publish_id": job.publish_id,
                        "error": "没有需要更新的有效字段"
                    })
            
            # 收集所有需要更新的publish_ids
            publish_ids = [job.publish_id for job, _ in valid_updates]
            
            # 批量获取所有点
            search_results = qdrant_client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=publish_ids,
            )
            
            # 创建publish_id到job更新的映射
            updates_map = {job.publish_id: (job, fields) for job, fields in valid_updates}
            
            # 准备批量更新操作
            update_operations = []
            
            # 处理每个搜索结果
            for result in search_results:
                try:
                    publish_id = result.id
                    job, update_payload = updates_map[publish_id]
                    
                    # 移除publish_id字段
                    update_payload.pop('publish_id', None)
                    
                    # 添加修改时间信息
                    current_time = int(time.time())
                    update_payload.update({
                        'modify_time': current_time,
                        'modify_timestamp': datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    # 添加payload更新操作
                    update_operations.append(
                        models.SetPayloadOperation(
                            set_payload=models.SetPayload(
                                payload=update_payload,
                                points=[publish_id]
                            )
                        )
                    )

                    # 检查并更新向量
                    vector_updates = {}
                    if 'job_name' in update_payload:
                        vector_updates['job_name'] = await vectorize(update_payload['job_name'])
                    if 'job_descript' in update_payload:
                        vector_updates['job_descript'] = await vectorize(update_payload['job_descript'])
                    if 'job_require' in update_payload:
                        vector_updates['job_require'] = await vectorize(update_payload['job_require'])

                    # 如果有需要更新的向量，添加向量更新操作
                    if vector_updates:
                        update_operations.append(
                            models.UpdateVectorsOperation(
                                update_vectors=models.UpdateVectors(
                                    points=[
                                        models.PointVectors(
                                            id=publish_id,
                                            vector=vector_updates
                                        )
                                    ]
                                )
                            )
                        )
                    
                    updated_count += 1
                    
                except Exception as e:
                    failed_updates.append({
                        "publish_id": publish_id,
                        "error": str(e)
                    })
                    logger.error(f"准备更新岗位 {publish_id} 时出错: {str(e)}")
            
            # 检查未找到的岗位
            found_ids = {result.id for result in search_results}
            missing_ids = set(publish_ids) - found_ids
            for missing_id in missing_ids:
                failed_updates.append({
                    "publish_id": missing_id,
                    "error": "岗位不存在"
                })
            
            # 执行批量更新
            if update_operations:
                try:
                    qdrant_client.batch_update_points(
                        collection_name=COLLECTION_NAME,
                        update_operations=update_operations,
                    )
                except Exception as e:
                    logger.error(f"执行批量更新时出错: {str(e)}")
                    # 修改错误处理逻辑，区分不同类型的操作
                    failed_updates.extend([
                        {
                            "publish_id": op.set_payload.points[0] if isinstance(op, models.SetPayloadOperation) 
                                        else op.update_vectors.points[0].id,
                            "error": "批量更新失败"
                        }
                        for op in update_operations
                    ])
                    updated_count = 0

            return updated_count, failed_updates

        except Exception as e:
            logger.error(f"批量更新岗位时出错: {str(e)}")
            raise

class JobUpdateCollection(BaseModel):
    """
    岗位更新请求的集合模型。
    包装多个JobUpdateItem实例，避免直接暴露数组作为最高层结构。
    """
    data: List[JobUpdateItem]

@router.post(
    "/jobs_update/",
    response_model=BatchUpdateResponse,
    responses={
        200: {"description": "成功更新岗位信息"},
        400: {"description": "请求数据无效"},
        503: {"description": "Qdrant服务不可用"}
    }
)
async def update_jobs(updates: JobUpdateCollection) -> BatchUpdateResponse:
    """批量更新岗位信息的API端点"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    try:
        updated_count, failed_updates = await batch_update_jobs(updates.data)

        return BatchUpdateResponse(
            total_processed=len(updates.data),
            updated_count=updated_count,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )

    except Exception as e:
        logger.error(f"处理岗位更新请求时出错: {str(e)}")
        failed_updates = [
            {"publish_id": job.publish_id, "error": str(e)}
            for job in updates.data
        ]
        return BatchUpdateResponse(
            total_processed=len(updates.data),
            updated_count=0,
            failed_count=len(updates.data),
            failed_updates=failed_updates
        )

class JobDeleteRequest(BaseModel):
    """删除请求模型"""
    publish_ids: List[int] = Field(..., description="要删除的职位ID列表")

@router.post(
    "/jobs_delete/",
    status_code=status.HTTP_200_OK,
)
async def delete_jobs(request: JobDeleteRequest):
    """批量删除岗位"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=request.publish_ids
                ),
            )
            return {"message": "岗位删除成功"}
            
        except Exception as e:
            logger.error(f"删除岗位时出错: {str(e)}")
            raise HTTPException(status_code=500, detail="删除岗位失败")

class BatchCreateResponse(BaseModel):
    """批量创建响应模型"""
    total_processed: int
    created_count: int
    failed_count: int
    failed_creates: List[Dict[str, Any]] = Field(default_factory=list)

class JobCreateCollection(BaseModel):
    """岗位创建请求的集合模型"""
    data: List[Jobs]

async def batch_create_jobs(jobs: List[Jobs]) -> tuple[int, List[Dict[str, Any]]]:
    """批量创建岗位信息
    
    Args:
        jobs: 要创建的岗位信息列表
        
    Returns:
        tuple[int, List[Dict]]: (成功创建数量, 失败的创建记录列表)
    """
    created_count = 0
    failed_creates = []
    
    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            points = []
            for job in jobs:
                try:
                    # 添加创建时间信息
                    current_time = int(time.time())
                    job_dict = job.model_dump()
                    job_dict.update({
                        'create_time': current_time,
                        'modify_time': current_time,
                        'modify_timestamp': datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
                    })

                    # 生成向量
                    vectors = {
                        'job_name': await vectorize(job.job_name),
                        'job_descript': await vectorize(job.job_descript),
                        'job_require': await vectorize(job.job_require)
                    }

                    # 创建点
                    points.append(
                        models.PointStruct(
                            id=job.publish_id,
                            vector=vectors,
                            payload=job_dict
                        )
                    )
                    created_count += 1
                    
                except Exception as e:
                    failed_creates.append({
                        "publish_id": job.publish_id,
                        "error": str(e)
                    })
                    logger.error(f"准备创建岗位 {job.publish_id} 时出错: {str(e)}")

            # 执行批量创建
            if points:
                try:
                    qdrant_client.upload_points(
                        collection_name=COLLECTION_NAME,
                        points=points
                    )
                except Exception as e:
                    logger.error(f"执行批量创建时出错: {str(e)}")
                    failed_creates.extend([
                        {
                            "publish_id": point.id,
                            "error": "批量创建失败"
                        }
                        for point in points
                    ])
                    created_count = 0

            return created_count, failed_creates

        except Exception as e:
            logger.error(f"批量创建岗位时出错: {str(e)}")
            raise

@router.post(
    "/jobs_create/",
    response_model=BatchCreateResponse,
    responses={
        200: {"description": "成功创建岗位信息"},
        400: {"description": "请求数据无效"},
        503: {"description": "Qdrant服务不可用"}
    }
)
async def create_jobs(jobs: JobCreateCollection) -> BatchCreateResponse:
    """批量创建岗位信息的API端点"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    try:
        created_count, failed_creates = await batch_create_jobs(jobs.data)

        return BatchCreateResponse(
            total_processed=len(jobs.data),
            created_count=created_count,
            failed_count=len(failed_creates),
            failed_creates=failed_creates
        )

    except Exception as e:
        logger.error(f"处理岗位创建请求时出错: {str(e)}")
        failed_creates = [
            {"publish_id": job.publish_id, "error": str(e)}
            for job in jobs.data
        ]
        return BatchCreateResponse(
            total_processed=len(jobs.data),
            created_count=0,
            failed_count=len(jobs.data),
            failed_creates=failed_creates
        )