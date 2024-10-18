# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 09:54
# @Author  : Galleons
# @File    : students_api.py

"""
这里是文件说明
"""

from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.responses import Response
import motor.motor_asyncio
from bson import ObjectId
from pymongo import ReturnDocument

from app.config import settings
from app.db.models import StudentModel, UpdateStudentModel, StudentCollection


router = APIRouter()


client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DATABASE_HOST)
db = client.get_database("college")
student_collection = db.get_collection("students")

@router.post(
    "/students/",
    response_description="添加新学生",
    response_model=StudentModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: StudentModel = Body(...)):
    """
    插入一条新的学生记录。

    将创建一个唯一的 `id` 并在响应中提供。
    """
    new_student = await student_collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await student_collection.find_one(
        {"_id": new_student.inserted_id}
    )
    return created_student


@router.get(
    "/students/",
    response_description="列出所有学生",
    response_model=StudentCollection,
    response_model_by_alias=False,
)
async def list_students():
    """
    列出数据库中的所有学生数据。

    响应是未分页的，限制为 1000 个结果。
    """
    return StudentCollection(students=await student_collection.find().to_list(1000))


@router.get(
    "/students/{id}",
    response_description="获取单个学生",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    """
    获取特定学生的记录，通过 `id` 查找。
    """
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"学生 {id} 未找到")

@router.put(
    "/students/{id}",
    response_description="更新学生",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    """
    更新现有学生记录的单个字段。

    只有提供的字段会被更新。
    任何缺失或 `null` 字段将被忽略。
    """
    student = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    if len(student) >= 1:
        update_result = await student_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"学生 {id} 未找到")

    # 更新为空，但我们仍应返回匹配的文档：
    if (existing_student := await student_collection.find_one({"_id": id})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"学生 {id} 未找到")

@router.delete("/students/{id}", response_description="删除学生")
async def delete_student(id: str):
    """
    从数据库中删除单个学生记录。
    """
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"学生 {id} 未找到")