# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 09:56
# @Author  : Galleons
# @File    : mongodb.py

"""
用于mongodb文件O/I
"""
import os
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
import motor.motor_asyncio
from bson import ObjectId
from pymongo import ReturnDocument

from app.config import settings
from app.db.models import DocumentCollection
from app.feature_pipeline.models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel

import uuid
from bson import Binary
from pydantic import ConfigDict, BaseModel, Field

class Document(PostsRawModel):
    id: str = Field(alias="_id", default_factory=uuid.uuid4)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": str(uuid.uuid4()),
                "entry_id": "string",
                "type": "posts",
                "author_id": "string",
                "platform": "长沙总部基地",
                "content":
                    {
                        "title": "云研AI开发团队规范",
                        "content": """1. 云研开发团队从来不用打卡。2. 云研AI开发团队从来不加班。"""
                     }
            }
        },
    )

router = APIRouter()

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DATABASE_HOST)
db = client.get_database("scrabble")
document_collection = db.get_collection("posts")

@router.post(
    "/documents/",
    response_description="添加新文档",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_document(document: Document = Body(...)):
    """
    插入一条新的文档。

    将创建一个唯一的 `id` 并在响应中提供。
    """
    # # 手动将 UUID 转换为 bson.Binary
    # if isinstance(document.id, uuid.UUID):
    #     document.id = Binary.from_uuid(document.id)

    new_document = await document_collection.insert_one(
        document.model_dump(by_alias=True)
    )
    created_document = await document_collection.find_one(
        {"_id": new_document.inserted_id}
    )
    return created_document


@router.get(
    "/documents/",
    response_description="列出所有文档",
    response_model=DocumentCollection,
    response_model_by_alias=False,
)
async def list_documents():
    """
    列出数据库中的所有文档数据。

    响应是未分页的，限制为 1000 个结果。
    """
    return DocumentCollection(documents=await document_collection.find().to_list(1000))


@router.get(
    "/documents/{id}",
    response_description="获取单个文档",
    response_model=Document,
    response_model_by_alias=False,
)
async def show_document(id: str):
    """
    获取特定文档的记录，通过 `id` 查找。
    """
    if (
        document := await document_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return document

    raise HTTPException(status_code=404, detail=f"文档 {id} 未找到")

@router.put(
    "/documents/{id}",
    response_description="更新文档",
    response_model=Document,
    response_model_by_alias=False,
)
async def update_document(id: str, document: Document = Body(...)):
    """
    更新现有文档记录的单个字段。

    只有提供的字段会被更新。
    任何缺失或 `null` 字段将被忽略。
    """
    document = {
        k: v for k, v in document.model_dump(by_alias=True).items() if v is not None
    }

    if len(document) >= 1:
        update_result = await document_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": document},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"文档 {id} 未找到")

    # 更新为空，但我们仍应返回匹配的文档：
    if (existing_document := await document_collection.find_one({"_id": id})) is not None:
        return existing_document

    raise HTTPException(status_code=404, detail=f"文档 {id} 未找到")

@router.delete("/documents/{id}", response_description="删除文档")
async def delete_document(id: str):
    """
    从数据库中删除单个文档记录。
    """
    delete_result = await document_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"文档 {id} 未找到")





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "mongo_api:mongodb_CRUD",
        host="127.0.0.1",
        port=settings.MONGO_DATABASE_API_PORT,
        reload=True
    )
