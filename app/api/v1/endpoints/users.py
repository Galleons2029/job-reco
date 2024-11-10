# -*- coding: utf-8 -*-
# @Time    : 2024/10/29 17:11
# @Author  : Galleons
# @File    : users.py

"""
用户数据模型
"""

import os
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
import motor.motor_asyncio
from bson import ObjectId
from pymongo import ReturnDocument

from app.config import settings
from app.db.models.user import UserBase, UserInDB


router = APIRouter()


client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DATABASE_HOST)
db = client.get_database("scrabble")


def get_collection(collection_name: str):
    """
    动态获取指定的集合。
    """
    return db.get_collection(collection_name)


@router.post(
    "/user/",
    response_description="添加新记录",
    # response_model=us,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_document(collection_name: str, document = Body(...)):
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