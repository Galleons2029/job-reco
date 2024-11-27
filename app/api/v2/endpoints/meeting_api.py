# -*- coding: utf-8 -*-
# @Time    : 2024/11/19 15:45
# @Author  : Galleons
# @File    : meeting_api.py

"""
这里是文件说明
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from qdrant_client import models
import logging
from app.db.qdrant import QdrantClientManager
from app.config import settings

from app.db.models.jobs import (
    Bilateral_delete_record, BilateralCollection,
    CareerTalkDelete, CareerTalkCollection
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

COLLECTION_NAME = settings.COLLECTION_TEST


class DeletePayloadRequest(BaseModel):
    """删除请求的基础模型

    Examples:
        >>> # 删除宣讲会记录
        >>> {"publish_ids": [1, 2, 3], "meeting_id": 123, "meeting_type": "career_talk"}
        >>> # 删除双选会记录
        >>> {"publish_ids": [1, 2, 3], "meeting_id": 456, "meeting_type": "fair"}
    """
    publish_ids: List[int]
    meeting_id: int = Field(..., description="宣讲会ID(career_talk_id)或双选会ID(fair_id)")
    meeting_type: str = Field(..., description="会议类型", pattern="^(career_talk|fair)$")

class MeetingDeleteCollection(BaseModel):
    """
    一个容器，包含多个删除请求实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[DeletePayloadRequest]

class BatchUpdateResponse(BaseModel):
    total_processed: int
    failed_count: int
    failed_updates: List[Dict[str, Any]] = Field(default_factory=list)


class BatchDeleteResponse(BaseModel):
    """删除操作的响应模型"""
    total_processed: int
    deleted_count: int
    failed_count: int
    failed_deletes: List[Dict[str, Any]] = Field(default_factory=list)



@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def batch_update_payload(updates: List[Dict[str, Any]], update_type: str) -> None:
    """批量更新多个岗位的双选会或者宣讲会标签

    Args:
        updates: 要更新的数据列表
        update_type: 更新类型，可选值: 'career_talk' 或 'fair'
    """
    payload_mapping = {
        'career_talk': ('career_talk', 'career_talk_id'),
        'fair': ('fair_list', 'fair_id'),
    }

    if update_type not in payload_mapping:
        raise ValueError(f"不支持的更新类型: {update_type}")

    payload_key, id_key = payload_mapping[update_type]

    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            update_operations = []
            for update in updates:
                publish_id = update['publish_id']
                item_id = update[id_key]

                search_result = qdrant_client.retrieve(
                    collection_name=COLLECTION_NAME,
                    ids=[publish_id],
                )

                if not search_result:
                    continue

                items_list = search_result[0].payload.get(payload_key, [])

                if item_id not in items_list:
                    items_list.append(item_id)
                    update_operations.append(
                        models.SetPayloadOperation(
                            set_payload=models.SetPayload(
                                payload={payload_key: items_list},
                                points=[publish_id]
                            )
                        )
                    )

            if update_operations:
                qdrant_client.batch_update_points(
                    collection_name=COLLECTION_NAME,
                    update_operations=update_operations,
                )

        except Exception as e:
            logger.error(f"批量更新{update_type}时出错: {str(e)}")
            raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def batch_delete_payload(publish_ids: List[int], item_id: int, delete_type: str) -> tuple[int, List[int]]:
    """批量删除payload中的指定ID

    Args:
        publish_ids: 要处理的publish_id列表
        item_id: 要删除的career_talk_id或fair_id
        delete_type: 删除类型，可选值: 'career_talk' 或 'fair'

    Returns:
        tuple[int, List[int]]: (成功删除数量, 失败的publish_ids列表)
    """
    payload_mapping = {
        'career_talk': 'career_talk',
        'fair': 'fair_list',
    }

    if delete_type not in payload_mapping:
        raise ValueError(f"不支持的删除类型: {delete_type}")

    payload_key = payload_mapping[delete_type]
    deleted_count = 0
    failed_ids = []

    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            update_operations = []

            # 批量获取所有点
            search_results = qdrant_client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=publish_ids,
            )

            for result in search_results:
                try:
                    publish_id = result.id
                    items_list = result.payload.get(payload_key, [])

                    if item_id in items_list:
                        items_list.remove(item_id)
                        update_operations.append(
                            models.SetPayloadOperation(
                                set_payload=models.SetPayload(
                                    payload={payload_key: items_list},
                                    points=[publish_id]
                                )
                            )
                        )
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"处理publish_id {publish_id}时出错: {str(e)}")
                    failed_ids.append(publish_id)

            if update_operations:
                qdrant_client.batch_update_points(
                    collection_name=COLLECTION_NAME,
                    update_operations=update_operations,
                )

            return deleted_count, failed_ids

        except Exception as e:
            logger.error(f"批量删除{delete_type}时出错: {str(e)}")
            raise


@router.post("/update_career_record", response_model=BatchUpdateResponse)
async def update_career_talk_payloads(updates: CareerTalkCollection) -> BatchUpdateResponse:
    """批量更新Qdrant career_talk payloads的API端点"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    failed_updates = []
    total_processed = 0

    try:
        batch_updates = [update.model_dump() for update in updates.data]
        await batch_update_payload(updates=batch_updates, update_type='career_talk')
        total_processed = len(updates.data)

        return BatchUpdateResponse(
            total_processed=total_processed,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )

    except Exception as e:
        failed_updates.extend([
            {**update.model_dump(), 'error': str(e)}
            for update in updates.data
        ])
        logger.error(f"处理career_talk更新请求时出错: {str(e)}")
        return BatchUpdateResponse(
            total_processed=0,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )


@router.post("/update_fair_record", response_model=BatchUpdateResponse)
async def update_fair_payloads(updates: BilateralCollection) -> BatchUpdateResponse:
    """批量更新Qdrant fair_id payloads的API端点"""
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    failed_updates = []
    total_processed = 0

    try:
        batch_updates = [update.model_dump() for update in updates.data]
        await batch_update_payload(updates=batch_updates, update_type='fair')
        total_processed = len(updates.data)

        return BatchUpdateResponse(
            total_processed=total_processed,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )

    except Exception as e:
        failed_updates.extend([
            {**update.model_dump(), 'error': str(e)}
            for update in updates.data
        ])
        logger.error(f"处理fair_id更新请求时出错: {str(e)}")
        return BatchUpdateResponse(
            total_processed=0,
            failed_count=len(failed_updates),
            failed_updates=failed_updates
        )


@router.post("/delete_meeting_records", response_model=List[BatchDeleteResponse])
async def delete_meeting_payloads(requests: MeetingDeleteCollection) -> List[BatchDeleteResponse]:
    """批量删除会议记录的API端点
    
    支持批量删除多组宣讲会(career_talk)和双选会(fair)记录
    """
    if not QdrantClientManager.check_health():
        raise HTTPException(status_code=503, detail="Qdrant服务不可用")

    responses = []
    
    for request in requests.data:
        try:
            deleted_count, failed_ids = await batch_delete_payload(
                publish_ids=request.publish_ids,
                item_id=request.meeting_id,
                delete_type=request.meeting_type
            )
            
            failed_deletes = [
                {"publish_id": failed_id, "error": "处理失败"}
                for failed_id in failed_ids
            ]

            responses.append(BatchDeleteResponse(
                total_processed=len(request.publish_ids),
                deleted_count=deleted_count,
                failed_count=len(failed_ids),
                failed_deletes=failed_deletes
            ))

        except Exception as e:
            logger.error(f"处理删除请求时出错: {str(e)}, 请求数据: {request.model_dump()}")
            failed_deletes = [
                {"publish_id": pid, "error": str(e)}
                for pid in request.publish_ids
            ]
            responses.append(BatchDeleteResponse(
                total_processed=len(request.publish_ids),
                deleted_count=0,
                failed_count=len(request.publish_ids),
                failed_deletes=failed_deletes
            ))

    return responses