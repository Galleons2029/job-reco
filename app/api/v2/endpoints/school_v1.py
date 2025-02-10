# -*- coding: utf-8 -*-
# @Time    : 2025/1/10 10:07
# @Author  : Galleons
# @File    : school_v1.py

"""
学校信息管理接口
提供学校信息的CRUD操作，支持批量更新和条件查询
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.schools import (
    SchoolCreate, SchoolUpdate, SchoolInDB, BatchUpdateSchools
)
from app.db.mongodb import get_database_instance
from app.utils.monitoring import monitor_operation, async_retry_with_backoff
from app.api.v2.dependencies.exceptions import SchoolNotFoundException

router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)

@router.post("/schools/create", response_model=SchoolInDB, status_code=201)
@monitor_operation(operation_type="insert", collection="schools")
async def create_new_school(
    school: SchoolCreate,
    mongo_client: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    创建新学校记录

    Args:
        school: 学校创建模型
        mongo_client: MongoDB数据库实例

    Returns:
        SchoolInDB: 创建成功的学校信息

    Raises:
        HTTPException: 当创建过程中发生错误时抛出
    """
    logger.info(f"开始创建学校记录 - 学校名称: {school.school_name}")

    collection = mongo_client.schools.school_info

    # 检查是否已存在
    existing = await collection.find_one({
        "$or": [
            {"school_name": school.school_name},
            {"school_code": school.school_code}
        ]
    })
    if existing:
        logger.error(f"创建失败：已存在相同名称或代码的学校 - {school.school_name}")
        raise HTTPException(
            status_code=400,
            detail="院校已存在！"
        )

    # # 获取新的school_id
    # last_school = await collection.find_one(sort=[("school_id", -1)])
    # new_school_id = (last_school["school_id"] + 1) if last_school else 1

    school_dict = school.model_dump()
    school_dict.update({
        # "modify_time": datetime.now(),
        "create_by": 1,
    })

    logger.debug(f"准备插入学校数据: {school_dict}")
    new_school = await collection.insert_one(school_dict)
    logger.info(f"学校创建成功 - ID: {new_school.inserted_id}")

    created_school = await collection.find_one({"_id": new_school.inserted_id})
    return SchoolInDB(**created_school)

@router.get("/schools/{school_id}", response_model=SchoolInDB)
@monitor_operation(operation_type="query", collection="schools")
async def read_school(
    school_id: int,
    mongo_client: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    获取指定学校信息

    Args:
        school_id: 学校ID
        mongo_client: MongoDB数据库实例

    Returns:
        SchoolInDB: 学校详细信息

    Raises:
        SchoolNotFoundException: 当指定ID的学校不存在时抛出
    """
    logger.info(f"查询学校信息 - ID: {school_id}")

    async def get_school_data():
        collection = mongo_client.schools.school_info
        school = await collection.find_one({"school_id": school_id})
        
        if not school:
            logger.error(f"未找到学校 - ID: {school_id}")
            raise SchoolNotFoundException()
            
        logger.info(f"成功获取学校信息 - ID: {school_id}")
        return SchoolInDB(**school)

    return await async_retry_with_backoff(get_school_data)

@router.post("/schools/batch_update", response_model=List[SchoolInDB])
@monitor_operation(operation_type="update", collection="schools")
async def batch_update_schools(
    update_data: BatchUpdateSchools,
    mongo_client: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    批量更新学校信息

    Args:
        update_data: 包含多个学校更新数据的模型
        mongo_client: MongoDB数据库实例

    Returns:
        List[SchoolInDB]: 更新后的学校信息列表

    Raises:
        HTTPException: 当更新过程中发生错误时抛出
    """
    logger.info(f"开始批量更新学校信息 - 数量: {len(update_data.schools)}")

    async def update_schools_data():
        collection = mongo_client.schools.school_info
        updated_schools = []

        for school in update_data.schools:
            school_dict = school.model_dump(exclude_unset=True)
            school_dict.update({
                "last_updated": datetime.now(),
            })

            result = await collection.find_one_and_update(
                {"school_id": school.school_id},
                {"$set": school_dict},
                return_document=True
            )

            if result:
                updated_schools.append(SchoolInDB(**result))
                logger.debug(f"成功更新学校 - ID: {school.school_id}")
            else:
                logger.warning(f"未找到要更新的学校 - ID: {school.school_id}")

        if not updated_schools:
            raise HTTPException(status_code=404, detail="No schools were updated")

        logger.info(f"批量更新完成 - 成功更新{len(updated_schools)}所学校")
        return updated_schools

    return await async_retry_with_backoff(update_schools_data)

@router.delete("/schools/{school_id}", status_code=204)
@monitor_operation(operation_type="delete", collection="schools")
async def remove_school(
    school_id: int,
    mongo_client: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    删除指定学校记录

    Args:
        school_id: 学校ID
        mongo_client: MongoDB数据库实例

    Raises:
        SchoolNotFoundException: 当指定ID的学校不存在时抛出
    """
    logger.info(f"开始删除学校 - ID: {school_id}")

    async def delete_school_data():
        collection = mongo_client.schools.school_info
        
        # 检查是否存在
        if not await collection.find_one({"school_id": school_id}):
            logger.error(f"删除失败：未找到学校 - ID: {school_id}")
            raise SchoolNotFoundException()

        result = await collection.delete_one({"school_id": school_id})
        logger.info(f"成功删除学校 - ID: {school_id}")

    await async_retry_with_backoff(delete_school_data)

@router.get("/schools", response_model=List[SchoolInDB])
@monitor_operation(operation_type="query", collection="schools")
async def get_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_211: Optional[bool] = None,
    is_985: Optional[bool] = None,
    province_name: Optional[str] = None,
    mongo_client: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    获取学校列表，支持分页和条件筛选

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        is_211: 是否为211院校
        is_985: 是否为985院校
        province_name: 省份名称
        mongo_client: MongoDB数据库实例

    Returns:
        List[SchoolInDB]: 符合条件的学校列表
    """
    logger.info(f"查询学校列表 - 跳过: {skip}, 限制: {limit}")

    async def list_schools_data():
        collection = mongo_client.schools.school_info
        
        # 构建查询条件
        query = {}
        if is_211 is not None:
            query["is_211"] = is_211
        if is_985 is not None:
            query["is_985"] = is_985
        if province_name:
            query["province_name"] = province_name

        logger.debug(f"查询条件: {query}")
        
        cursor = collection.find(query).skip(skip).limit(limit)
        schools = await cursor.to_list(length=limit)
        
        logger.info(f"成功获取学校列表 - 返回{len(schools)}条记录")
        return [SchoolInDB(**school) for school in schools]

    return await async_retry_with_backoff(list_schools_data)