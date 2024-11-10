# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 10:00
# @Author  : Galleons
# @File    : jobs_api.py
"""
这里是文件说明
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional

import time
import logging
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, validator, Field
from functools import wraps
import asyncio
from logging.handlers import RotatingFileHandler
from app.api.v1.dependencies import get_qdrant_client, get_xinference_client


# 配置日志
logging.basicConfig(
    handlers=[RotatingFileHandler('jobs_api.log', maxBytes=100000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()


# MongoDB setup
mongo_connection = AsyncIOMotorClient("mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app")
db = mongo_connection["jobs"]

from qdrant_client import QdrantClient, models
qdrant_connection = QdrantClient(url="192.168.100.111:6333")

embed_model = get_xinference_client()

def get_collection(collection_name: str):
    """
    动态获取指定的集合。
    """
    return db.get_collection(collection_name)


class ExampleItem(BaseModel):
    publish_id: str | int
    company_id: str | int = None
    m_company_id: int | None = None
    company_name: str | None = None
    job_id: str | int = None
    end_time: int | None = None
    is_practice: int | None = None
    is_zpj_job: int | None = None
    apply_count: int | None = None
    job_name: str | None = None
    edu_category: str | None = None
    category: str | None = None
    category_id: int | None = None
    parent_category: str | None = None
    parent_category_id: int | None = None
    second_category: str | None = None
    second_category_id: int | None = None
    category_teacher_type: str | None = None
    job_number: str | None = None
    job_status: int | None = None
    job_require: str | None = None
    job_descript: str | None = None
    salary: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    contact_tel: str | None = None
    city_name: str | None = None
    work_address: str | None = None
    keywords: str | None = None
    welfare: str | None = None
    intro_apply: str | None = None
    intro_screen: str | None = None
    intro_interview: str | None = None
    intro_sign: str | None = None
    source: str | None = None
    province: str | None = None
    degree_require: str | None = None
    experience: str | None = None
    job_desc: str | None = None
    biz_salary: str | None = None
    about_major: str | None = None
    view_count: int | None = None
    job_other: str | None = None
    source_school_id: int | None = None
    source_school: str | None = None
    is_commend: int | None = None
    commend_time: int | None = None
    is_publish: str | None = None
    publish_hr_id: int | None = None
    publish_hr_openid: str | None = None
    publish_time: int | None = None
    amount_welfare_min: int | None = None
    amount_welfare_max: int | None = None
    time_type: str | None = None
    is_top: int | None = None
    job_type: int | None = None
    create_by: int | None = None
    create_time: int | None = None
    modify_by: int | None = None
    modify_time: int | None = None
    modify_timestamp: str | None = None
    is_default: int | None = None
    company_id_bak: int | None = None
    removed: int | None = None

    def get_non_none_fields(self) -> dict:
        """获取所有非None的字段值"""
        return {
            field: value
            for field, value in self.dict().items()
            if value is not None
        }


class ExampleModel(BaseModel):
    data: List[ExampleItem]


@router.post(
    "/jobs_update/",
    response_description="更新岗位信息",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
async def update_jobs(jobs: ExampleModel):
    """
    更新岗位记录。

    - 支持批量更新多个岗位信息
    - 仅更新传入且有值的字段
    - 使用publish_id作为唯一标识
    """
    updated_count = 0
    errors = []

    for job in jobs.data:
        try:
            # 获取所有非None的字段
            update_payload = job.get_non_none_fields()

            # 从payload中移除publish_id，因为它是查询条件
            publish_id = int(update_payload.pop('publish_id'))

            # 如果除了publish_id外没有其他需要更新的字段，则跳过
            if not update_payload:
                continue

            # 添加修改时间戳
            update_payload['modify_time'] = int(time.time())
            # update_payload['modify_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 更新记录
            result = qdrant_connection.set_payload(
                collection_name="job_2024_1109",
                payload=update_payload,
                points=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            )
            print(update_payload)
            # 更新成功计数
            if result:  # 根据实际的返回值判断是否更新成功
                updated_count += 1
                logger.info(f"岗位更新成功: publish_id={publish_id}, 更新字段: {list(update_payload.keys())}")

        except ValidationError as e:
            error_msg = f"岗位 {job.publish_id} 数据验证错误: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"岗位 {job.publish_id} 更新失败: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

    response = {
        "message": "岗位信息更新完成",
        "updated_count": updated_count,
        "total_count": len(jobs.data),
    }

    # 如果有错误，添加到响应中
    if errors:
        response["errors"] = errors


    return response




class JobDelete(BaseModel):
    data: List[int]



@router.post(
    "/jobs_delete/",
    response_description="删除岗位",
    # response_model=JobsModel,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
async def delete_jobs(jobs: JobDelete):
    """
    插入一条新的学生记录。

    将创建一个唯一的 `id` 并在响应中提供。
    """

    for publish_id in jobs.data:
        result = qdrant_connection.delete(
            collection_name="job_2024_1109",
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="publish_id",
                            match=models.MatchValue(value=publish_id),
                        ),
                    ],
                )
            ),
        )

    return {"message": f"岗位信息删除成功。"}






