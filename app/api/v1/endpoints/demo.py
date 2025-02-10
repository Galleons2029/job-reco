# -*- coding: utf-8 -*-
# @Time    : 2024/11/1 20:22
# @Author  : Galleons
# @File    : demo.py

"""
这里是文件说明
"""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# 创建FastAPI应用
app = FastAPI()

# 连接到MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["student_db"]
collection = db["students"]

# 定义ID模型，用于Pydantic数据校验
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# 定义嵌套数据模型
class IntentionModel(BaseModel):
    sadd: Optional[str] = None
    salary: Optional[str] = None

class ExperienceModel(BaseModel):
    experience1: Optional[str] = None
    experience2: Optional[str] = None

class CompanyModel(BaseModel):
    company1: Optional[str] = None
    company2: Optional[str] = None
    company3: Optional[str] = None
    company4: Optional[str] = None
    company5: Optional[str] = None

class SkillModel(BaseModel):
    skill_1: Optional[str] = None
    skill_2: Optional[str] = None
    skill_3: Optional[str] = None
    skill_4: Optional[str] = None

class ResumeModel(BaseModel):
    weyon_id: Optional[str] = None
    experience: Optional[ExperienceModel] = None
    company: Optional[CompanyModel] = None
    skill: Optional[SkillModel] = None

class PersonInfoModel(BaseModel):
    person_info_1: Optional[Dict[str, str]] = None
    person_info_2: Optional[Dict[str, str]] = None

class StudentModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: Optional[str] = None
    intention: Optional[IntentionModel] = None
    person_info: Optional[PersonInfoModel] = None
    resume_base: Optional[Dict[str, ResumeModel]] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 创建接口：增、查、改、删（CRUD）

# 创建学生档案
@app.post("/students/", response_model=StudentModel)
async def create_student(student: StudentModel):
    new_student = student.dict(by_alias=True)
    result = await collection.insert_one(new_student)
    created_student = await collection.find_one({"_id": result.inserted_id})
    return created_student

# 获取学生档案
@app.get("/students/{student_id}", response_model=StudentModel)
async def get_student(student_id: str):
    student = await collection.find_one({"_id": ObjectId(student_id)})
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 更新学生档案
@app.put("/students/{student_id}", response_model=StudentModel)
async def update_student(student_id: str, student: StudentModel):
    update_data = {k: v for k, v in student.dict(by_alias=True).items() if v is not None}
    result = await collection.update_one({"_id": ObjectId(student_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_student = await collection.find_one({"_id": ObjectId(student_id)})
    return updated_student

# 删除学生档案
@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted successfully"}
