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
from app.db.models.jobs import JobUpdateItem
from app.utils.embeddings import vectorize

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

COLLECTION_NAME = "job_2024_1115"


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
            # 收集所有需要更新的publish_ids
            publish_ids = [job.publish_id for job in updates]
            
            # 批量获取所有点
            search_results = qdrant_client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=publish_ids,
            )
            
            # 创建publish_id到job更新的映射
            updates_map = {job.publish_id: job for job in updates}
            
            # 准备批量更新操作
            update_operations = []
            
            # 处理每个搜索结果
            for result in search_results:
                try:
                    publish_id = result.id
                    job = updates_map[publish_id]
                    
                    # 获取需要更新的字段
                    update_payload = job.get_non_none_fields()
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
                    # 如果批量更新失败，将所有操作标记为失败
                    failed_updates.extend([
                        {"publish_id": op.set_payload.points[0], "error": "批量更新失败"}
                        for op in update_operations
                    ])
                    updated_count = 0

            return updated_count, failed_updates

        except Exception as e:
            logger.error(f"批量更新岗位时出错: {str(e)}")
            raise

@router.post(
    "/jobs_update/",
    response_model=BatchUpdateResponse,
    responses={
        200: {"description": "成功更新岗位信息"},
        400: {"description": "请求数据无效"},
        503: {"description": "Qdrant服务不可用"}
    }
)
async def update_jobs(updates: List[JobUpdateItem]) -> BatchUpdateResponse:
    """批量更新岗位信息的API端点"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    try:
        updated_count, failed_updates = await batch_update_jobs(updates)

        return BatchUpdateResponse(
            total_processed=len(updates),
            updated_count=updated_count,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )

    except Exception as e:
        logger.error(f"处理岗位更新请求时出错: {str(e)}")
        failed_updates = [
            {"publish_id": job.publish_id, "error": str(e)}
            for job in updates
        ]
        return BatchUpdateResponse(
            total_processed=len(updates),
            updated_count=0,
            failed_count=len(updates),
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