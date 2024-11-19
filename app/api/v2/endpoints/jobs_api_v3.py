# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 14:30
# @Author  : Galleons
# @File    : jobs_api_v3.py

"""
这里是文件说明
"""
from typing import List, Optional
from datetime import datetime
import time
import logging
from fastapi import HTTPException, status, Depends, APIRouter
from pydantic import BaseModel, validator, Field, ValidationError, field_validator
from qdrant_client import models
from functools import wraps
import asyncio
from logging.handlers import RotatingFileHandler
from app.api.v2.dependencies.by_qdrant import get_qdrant_client
from qdrant_client import QdrantClient

from motor.motor_asyncio import AsyncIOMotorCollection
import re


# 配置日志
logging.basicConfig(
    handlers=[RotatingFileHandler('jobs_api.log', maxBytes=100000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


router = APIRouter()


# 自定义异常
class JobUpdateError(Exception):
    """岗位更新相关的自定义异常"""
    pass


class InvalidDateError(JobUpdateError):
    """日期格式无效"""
    pass


class JobNotFoundError(JobUpdateError):
    """岗位不存在"""
    pass


# 请求模型与验证器
class ExampleItem(BaseModel):
    publish_id: str | int = Field(..., description="岗位发布ID，用于唯一标识一个岗位")
    company_id: Optional[str | int] = Field(None, description="公司ID")
    m_company_id: Optional[int] = Field(None, description="公司ID(数字类型)")
    company_name: Optional[str] = Field(None, description="公司名称")
    job_id: Optional[str | int] = Field(None, description="岗位ID")
    end_time: Optional[int] = Field(None, description="结束时间(时间戳)")
    is_practice: Optional[int] = Field(None, description="是否为实习岗位", ge=0, le=1)
    is_zpj_job: Optional[int] = Field(None, description="是否为中评价岗位", ge=0, le=1)
    apply_count: Optional[int] = Field(None, description="申请人数", ge=0)
    job_name: Optional[str] = Field(None, description="岗位名称", max_length=200)

    # ... 其他字段定义 ...

    # 字段验证器
    @field_validator('end_time')
    def validate_end_time(cls, v):
        if v is not None:
            current_time = int(time.time())
            if v < current_time:
                raise ValueError("结束时间不能早于当前时间")
        return v

    @field_validator('salary_min', 'salary_max')
    def validate_salary(cls, v, values, field):
        if v is not None and v < 0:
            raise ValueError(f"{field.name} 不能为负数")
        if field.name == 'salary_max' and 'salary_min' in values:
            if values['salary_min'] is not None and v is not None:
                if v < values['salary_min']:
                    raise ValueError("最高薪资不能低于最低薪资")
        return v

    def get_non_none_fields(self) -> dict:
        """获取所有非None的字段值"""
        return {
            field: value
            for field, value in self.model_dump().items()
            if value is not None
        }


class ExampleModel(BaseModel):
    data: List[ExampleItem] = Field(..., description="岗位信息列表")


# 异步锁装饰器，用于并发控制
def async_lock(func):
    """异步锁装饰器，确保同一个publish_id不会同时被多个请求更新"""
    locks = {}

    @wraps(func)
    async def wrapper(*args, **kwargs):
        job = kwargs.get('job')
        if not job:
            return await func(*args, **kwargs)

        if job.publish_id not in locks:
            locks[job.publish_id] = asyncio.Lock()

        async with locks[job.publish_id]:
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                if not locks[job.publish_id].locked():
                    del locks[job.publish_id]

    return wrapper


# 数据库事务管理
class Transaction:
    """简单的事务管理上下文"""

    def __init__(self, qdrant_connection):
        self.qdrant = qdrant_connection
        self.operations = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 发生异常，执行回滚操作
            for operation in reversed(self.operations):
                try:
                    await self.rollback_operation(operation)
                except Exception as e:
                    logger.error(f"回滚操作失败: {str(e)}")
            return False
        return True

    async def rollback_operation(self, operation):
        """回滚单个操作"""
        # 实现具体回滚逻辑
        pass

    def add_operation(self, operation):
        """添加操作到事务列表"""
        self.operations.append(operation)


# # 依赖项
# async def get_qdrant_client():
#     """获取Qdrant客户端连接"""
#     # 这里实现获取连接的逻辑
#     return get_qdrant_client


@router.post(
    "/jobs_update/",
    response_description="更新岗位信息",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    responses={
        200: {
            "description": "成功更新岗位信息",
            "content": {
                "application/json": {
                    "example": {
                        "message": "岗位信息更新完成",
                        "updated_count": 2,
                        "total_count": 2
                    }
                }
            }
        },
        400: {
            "description": "请求参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "参数验证错误信息"
                    }
                }
            }
        },
        404: {
            "description": "未找到指定的岗位",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "岗位不存在"
                    }
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "服务器处理请求时发生错误"
                    }
                }
            }
        }
    }
)
async def update_jobs(
        jobs: ExampleModel,
        qdrant_client: QdrantClient = Depends(get_qdrant_client)
) -> dict:
    """
    批量更新岗位信息。

    ### 功能描述：
    - 支持批量更新多个岗位的信息
    - 仅更新传入且有值的字段
    - 使用publish_id作为唯一标识
    - 自动记录修改时间
    - 支持并发控制
    - 包含事务管理

    ### 参数说明：
    - jobs: 包含多个岗位信息的列表

    ### 返回值：
    - message: 更新结果描述
    - updated_count: 成功更新的记录数
    - total_count: 总处理记录数
    - errors: 错误信息列表（如果有）

    ### 注意事项：
    - 所有时间戳字段使用Unix时间戳格式
    - salary_min 必须小于 salary_max
    - end_time 必须大于当前时间
    """
    updated_count = 0
    errors = []

    async with Transaction(qdrant_client) as transaction:
        for job in jobs.data:
            try:
                await process_job_update(job, qdrant_client, transaction)
                updated_count += 1
                logger.info(f"岗位更新成功: {job.publish_id}")

            except JobNotFoundError:
                error_msg = f"岗位不存在: {job.publish_id}"
                errors.append(error_msg)
                logger.warning(error_msg)

            except ValidationError as e:
                error_msg = f"岗位 {job.publish_id} 数据验证错误: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

            except Exception as e:
                error_msg = f"岗位 {job.publish_id} 更新失败: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )

    response = {
        "message": "岗位信息更新完成",
        "updated_count": updated_count,
        "total_count": len(jobs.data)
    }

    if errors:
        response["errors"] = errors

    return response


@async_lock
async def process_job_update(
        job: ExampleItem,
        qdrant_client: QdrantClient,
        transaction: Transaction
) -> None:
    """
    处理单个岗位的更新操作

    Args:
        job: 岗位信息
        qdrant_client: Qdrant客户端
        transaction: 事务管理器

    Raises:
        JobNotFoundError: 岗位不存在
        ValidationError: 数据验证错误
        Exception: 其他错误
    """
    # 获取需要更新的字段
    update_payload = job.get_non_none_fields()
    publish_id = update_payload.pop('publish_id')

    # 检查岗位是否存在
    existing_job = qdrant_client.scroll(
        collection_name="job_test",
        points=models.Filter(
            must=[
                models.FieldCondition(
                    key="publish_id",
                    match=models.MatchValue(value=publish_id),
                ),
            ],
        )
    )

    if not existing_job:
        raise JobNotFoundError(f"岗位不存在: {publish_id}")

    # 添加修改时间信息
    current_time = int(time.time())
    update_payload.update({
        'modify_time': current_time,
        'modify_timestamp': datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
    })

    # 记录更新操作
    transaction.add_operation({
        'type': 'update',
        'publish_id': publish_id,
        'old_data': existing_job,
        'new_data': update_payload
    })

    # 执行更新
    result = await qdrant_client.set_payload(
        collection_name="job_test",
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

    if not result:
        raise Exception(f"更新操作失败: {publish_id}")



# 常量定义
PROTECTED_FIELDS = {
    "student_key",
    "school_id",
    "_id",
    "created_at",
    "updated_at"
}


class DeleteDataModel(BaseModel):
    school_id: str | int = Field(..., description="学校ID")
    student_key: str = Field(..., min_length=1, description="学生唯一标识")
    fields: List[str] = Field(..., description="需要删除的字段路径列表")

    @field_validator('fields')
    def validate_fields(cls, fields: List[str]) -> List[str]:
        # 验证字段格式
        field_pattern = re.compile(r'^[a-zA-Z0-9_]+(.[a-zA-Z0-9_]+)*$')

        for field in fields:
            # 检查字段名格式
            if not field_pattern.match(field):
                raise ValueError(f"无效的字段路径格式: {field}")

            # 检查是否为保护字段
            root_field = field.split('.')[0]
            if root_field in PROTECTED_FIELDS:
                raise ValueError(f"不能删除受保护的字段: {root_field}")

        return fields

    class Config:
        schema_extra = {
            "example": {
                "school_id": "2413",
                "student_key": "2c88bb981ed75e870ce26cd4996765e2",
                "fields": ["resume.project_experience.project_1"]
            }
        }


async def get_collection(school_id: str) -> AsyncIOMotorCollection:
    # 这里实现你的获取集合逻辑

    pass


class StudentFieldManager:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def validate_student_exists(self, student_key: str) -> bool:
        """验证学生是否存在"""
        doc = await self.collection.find_one({"student_key": student_key}, {"_id": 1})
        return bool(doc)

    async def delete_fields(self, student_key: str, fields: List[str]) -> dict:
        """删除指定字段"""
        # 构建 $unset 操作
        unset_data = {field: "" for field in fields}

        # 更新时间戳
        set_data = {"updated_at": datetime.utcnow()}

        # 执行更新操作
        result = await self.collection.update_one(
            {"student_key": student_key},
            {
                "$unset": unset_data,
                "$set": set_data
            }
        )

        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count
        }


@router.post("/delete_student_field/",
             response_model=dict,
             responses={
                 200: {"description": "字段删除成功"},
                 400: {"description": "请求数据无效"},
                 404: {"description": "学生不存在"},
                 500: {"description": "服务器内部错误"}
             })
async def delete_student_field(
        delete_data: DeleteDataModel,
        collection: AsyncIOMotorCollection = Depends(get_collection)
) -> dict:
    """
    删除学生档案中的指定字段

    - **school_id**: 学校ID
    - **student_key**: 学生唯一标识
    - **fields**: 需要删除的字段路径列表
    """
    try:
        # 创建管理器实例
        manager = StudentFieldManager(collection)

        # 验证学生是否存在
        student_exists = await manager.validate_student_exists(delete_data.student_key)
        if not student_exists:
            raise HTTPException(
                status_code=404,
                detail=f"学生不存在: {delete_data.student_key}"
            )

        # 执行字段删除
        result = await manager.delete_fields(
            delete_data.student_key,
            delete_data.fields
        )

        # 检查删除结果
        if result["modified_count"] == 0:
            if result["matched_count"] > 0:
                return {
                    "message": "字段可能已经不存在，无需删除",
                    "status": "unchanged",
                    "fields": delete_data.fields
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail="学生档案未找到"
                )

        return {
            "message": "字段删除成功",
            "status": "success",
            "deleted_fields": delete_data.fields,
            "modified_count": result["modified_count"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # 记录详细错误信息到日志
        logging.error(f"删除字段时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="服务器处理请求时发生错误，请稍后重试"
        )