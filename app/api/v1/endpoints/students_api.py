# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 09:54
# @Author  : Galleons
# @File    : students_api.py

"""
学生数据端口
"""
import os
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
import motor.motor_asyncio
from bson import ObjectId
from pymongo import ReturnDocument

from app.config import settings
from app.db.models.students import StudentModel, UpdateStudentModel, StudentCollection


router = APIRouter()


client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DATABASE_HOST)
db = client.get_database("college")


def get_collection(collection_name: str):
    """
    动态获取指定的集合。
    """
    return db.get_collection(collection_name)


@router.post(
    "/{collection_name}/",
    response_description="添加新记录",
    response_model=StudentModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_document(collection_name: str, document: StudentModel = Body(...)):
    """
    插入一条新的记录到指定集合中。
    将创建一个唯一的 `id` 并在响应中提供。
    """
    collection = get_collection(collection_name)
    new_document = await collection.insert_one(
        document.model_dump(by_alias=True, exclude=["id"])
    )
    created_document = await collection.find_one({"_id": new_document.inserted_id})
    return created_document


@router.get(
    "/{collection_name}/",
    response_description="列出所有记录",
    response_model=StudentCollection,
    response_model_by_alias=False,
)
async def list_documents(collection_name: str):
    """
    列出指定集合中的所有数据。
    响应是未分页的，限制为 1000 个结果。
    """
    collection = get_collection(collection_name)
    return StudentCollection(students=await collection.find().to_list(1000))


@router.get(
    "/{collection_name}/{id}",
    response_description="获取单个记录",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_document(collection_name: str, id: str):
    """
    获取特定集合中的单个记录，通过 `id` 查找。
    """
    collection = get_collection(collection_name)
    if (document := await collection.find_one({"_id": ObjectId(id)})) is not None:
        return document

    raise HTTPException(status_code=404, detail=f"记录 {id} 未找到")


@router.put(
    "/{collection_name}/{id}",
    response_description="更新记录",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def update_document(collection_name: str, id: str, document: UpdateStudentModel = Body(...)):
    """
    更新现有集合记录的单个字段。
    只有提供的字段会被更新。
    任何缺失或 `null` 字段将被忽略。
    """
    collection = get_collection(collection_name)
    update_data = {
        k: v for k, v in document.model_dump(by_alias=True).items() if v is not None
    }

    if len(update_data) >= 1:
        update_result = await collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"记录 {id} 未找到")

    # 更新为空，但我们仍应返回匹配的文档：
    if (existing_document := await collection.find_one({"_id": ObjectId(id)})) is not None:
        return existing_document

    raise HTTPException(status_code=404, detail=f"记录 {id} 未找到")


@router.delete("/{collection_name}/{id}", response_description="删除记录")
async def delete_document(collection_name: str, id: str):
    """
    从指定集合中删除单个记录。
    """
    collection = get_collection(collection_name)
    delete_result = await collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"记录 {id} 未找到")

