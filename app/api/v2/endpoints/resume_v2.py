# -*- coding: utf-8 -*-
# @Time    : 2025/1/9 17:53
# @Author  : Galleons
# @File    : resume_v2.py
"""
人才简历CURD接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, FastAPI, Request
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from bson import ObjectId
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from app.db.models.resumes import (
    Resume, ResumeUpdate, ResumeResponse, Batch_resumes_update, ProfileUpdater
)
from app.db.mongodb import MongoDBManager, get_database_instance, batch_update_resumes
from app.utils.monitoring import monitor_operation, async_retry_with_backoff
from app.api.v2.dependencies.exceptions import ResumeNotFoundException, DuplicateResumeException
from app.db.models.resume_update import BatchResumesUpdate
from app.db.mongodb import get_database, lifespan


app = FastAPI(title="Resume Management API",
              # lifespan=lifespan
              )

# router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)

from app.db.models.resumes import ResumeUpdate, ResumeUpdateHandler

"""
请帮我针对class ResumeUpdate设计一套基于mongodb里以user_id为标识的文档进行更新的接口，要求：
1. 采用批处理的方式，每次输入为class Batch_resumes_update，对列表里的ResumeUpdate进行遍历
2. 每个ResumeUpdate解析为一个UpdateOne操作，其中非嵌套的简单字段直接统一放入更新操作中，例如  { "user_id": ResumeUpdate.user_id,  $set": {  "name": ResumeUpdate.name, "work_years": ResumeUpdate.work_years} }
3. 对于嵌套字段，根据ListUpdateOperation里的operation进行判断：
若为"update"则使用在user_id条件后加入对应的id，再在后面加入对应的字典，例如{ "user_id": ResumeUpdate.user_id, "work_experience.experience_id": 16，"project_experience.project_id": 1},{ "$set": { "name": ResumeUpdate.name, "work_years": ResumeUpdate.work_years,"work_experience.$.company_name": "华为","project_experience.$.project_name": "企业级微服务平台",} 来更新特定项
若为"append"则使用在user_id条件后加入对应的id，再使用$push操作在相应字段添加新的操作，例如    UpdateOne(
    { "user_id": ResumeUpdate.user_id, },  { "$push": {"education_experience": ListUpdateOperation.data,}},),
若为"delete"则使用在user_id条件后加入对应的id，再使用$pull操作在相应字段添加新的删除操作，例如 UpdateOne( { "user_id": ResumeUpdate.user_id, },  { "$pull": {"education_experience": {"education_id": education_experience.education_id},}}, ),
3. 最后使用pymongo中的bulk_write进行批量写入，将所有UpdateOne操作放入operations当中，例如：
operations = [
    UpdateOne(
    { "user_id": 22222, },  { "$pull": {"work_experience": {"work_id": 1121},}},
    ),
    UpdateOne(
    { "user_id": 22222,
      "work_experience.fakeid": 123456,
      "project_experience.project_id": 1,
      },
        { "$set": { "work_experience.$.demo": "第4次变更。",
                    "name": "柳佳龙",
                    "project_experience.$.company_name": "第1次变更。",
                   }

      },
    ),
]
再使用collection.bulk_write(operations)进行统一操作
"""

@app.post("/resumes/update_resume", response_model=ResumeResponse)
@monitor_operation(operation_type="batch_update", collection="resumes")
async def update_resume(
        resume_update: ResumeUpdate,
        mongo_client: AsyncIOMotorClient = Depends(get_database_instance)
):
    """更新简历信息"""
    logger.debug(f"收到数据：{resume_update}")

    try:
        collection = mongo_client.test.resumes_test

        # 准备更新操作
        handler = ResumeUpdateHandler()
        update_ops = handler.prepare_update_operations(resume_update)

        # 执行更新并获取更新后的文档
        result = await collection.find_one_and_update(
            {"user_id": resume_update.user_id},
            update_ops,
            return_document=True  # 返回更新后的文档
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"未找到用户ID为 {resume_update.user_id} 的简历"
            )

        # 返回更新后的文档
        return ResumeResponse(**result)

    except Exception as e:
        logger.error(f"更新简历时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新简历失败: {str(e)}"
        )


@app.post("/resumes/create_resume", response_model=ResumeResponse, status_code=201)
async def create_resume(
        resume: Resume,
        mongo_client: AsyncIOMotorClient = Depends(get_database_instance)
):
    """
    创建新简历

    Args:
        resume: 简历数据模型
        mongo_client: MongoDB数据库实例

    Returns:
        ResumeResponse: 创建成功的简历响应

    Raises:
        DuplicateResumeException: 当简历已存在时抛出
    """
    logger.info(f"开始创建简历 - 用户标识: {resume.student_key}")

    try:
        db = mongo_client["test"]
        collection = db["resumes_test"]

        # 检查是否已存在
        existing = await collection.find_one({"user_id": resume.user_id})
        if existing:
            logger.error(f"创建失败：已存在相同用户标识的简历 - {resume.student_key}")
            raise DuplicateResumeException()

        # 将 Pydantic 模型转换为字典，并处理嵌套的 Pydantic 模型
        resume_dict = resume.model_dump(mode='json')

        logger.debug(f"准备插入简历数据: {resume_dict}")
        result = await collection.insert_one(resume_dict)
        logger.info(f"简历创建成功 - ID: {result.inserted_id}")

        # 获取创建的文档
        created_resume = await collection.find_one({"_id": result.inserted_id})
        if not created_resume:
            raise HTTPException(status_code=500, detail="Failed to retrieve created resume")

        return ResumeResponse(**created_resume)

    except DuplicateResumeException:
        raise
    except Exception as e:
        logger.error(f"创建简历时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建简历失败: {str(e)}")


# # 获取单个简历
# @app.get("/resumes/{resume_id}", response_model=ResumeResponse)
# @monitor_operation(operation_type="query", collection="resumes")
# async def get_resume(
#         resume_id: str,
#         db: AsyncIOMotorDatabase = Depends(get_database_instance)
# ):
#     """获取单个简历详情"""
#
#     async def fetch_resume():
#         collection = db["resumes"]  # 使用字典访问方式
#         resume = await collection.find_one({"_id": ObjectId(resume_id)})
#
#         if not resume:
#             raise ResumeNotFoundException()
#
#         resume["id"] = str(resume["_id"])
#         return resume
#
#     return await async_retry_with_backoff(fetch_resume)
#
#
#
# @app.put("/resumes/{resume_id}", response_model=ResumeResponse)
# @monitor_operation(operation_type="update", collection="resumes")
# async def update_resume(
#         user_id: str,
#         resume_update: ResumeUpdate,
#         db: AsyncIOMotorDatabase = Depends(get_database_instance)
# ):
#     """更新简历信息"""
#
#     async def update_resume_data():
#         collection = db["resumes"]  # 使用字典访问方式
#
#         # 检查是否存在
#         if not await collection.find_one({"_id": ObjectId(user_id)}):
#             raise ResumeNotFoundException()
#
#         # 准备更新数据
#         update_data = {}
#
#         # 处理普通字段
#         for field, value in resume_update.model_dump(exclude_unset=True).items():
#             if not isinstance(value, ListUpdateOperation):
#                 update_data[field] = value
#
#         # 处理列表类型字段
#         list_fields = ['education_experience', 'work_experience', 'project_experience',
#                        'leadership_experience', 'certificates']
#
#         for field in list_fields:
#             field_update = getattr(resume_update, field)
#             if field_update:
#                 if field_update.operation == OperationType.APPEND:
#                     # 追加新数据
#                     update_data[f"{field}"] = {
#                         "$push": {
#                             field: {"$each": field_update.data}
#                         }
#                     }
#                 elif field_update.operation == OperationType.UPDATE:
#                     # 更新特定项
#                     for index, item_data in field_update.data.items():
#                         update_data[f"{field}.{index}"] = item_data
#
#         # 添加最后更新时间
#         update_data["last_updated"] = datetime.now()
#
#         # 执行更新
#         await collection.update_one(
#             {"_id": ObjectId(user_id)},
#             {"$set": update_data}
#         )
#
#         # 获取更新后的文档
#         updated_resume = await collection.find_one({"_id": ObjectId(user_id)})
#         updated_resume["id"] = str(updated_resume["_id"])
#
#         return updated_resume
#
#     return await async_retry_with_backoff(update_resume_data)
#
#
# # 删除简历
# @app.delete("/resumes/{resume_id}", status_code=204)
# @monitor_operation(operation_type="delete", collection="resumes")
# async def delete_resume(
#         resume_id: str,
#         db: AsyncIOMotorDatabase = Depends(get_database_instance)
# ):
#     """删除指定简历"""
#
#     async def delete_resume_data():
#         collection = db["resumes"]  # 使用字典访问方式
#
#         # 检查是否存在
#         if not await collection.find_one({"_id": ObjectId(resume_id)}):
#             raise ResumeNotFoundException()
#
#         await collection.delete_one({"_id": ObjectId(resume_id)})
#
#     await async_retry_with_backoff(delete_resume_data)
#
#
# # 简历搜索
# @app.get("/resumes/search/", response_model=List[ResumeResponse])
# @monitor_operation(operation_type="search", collection="resumes")
# async def search_resumes(
#         db: AsyncIOMotorDatabase = Depends(get_database_instance),
#         keyword: str = Query(..., min_length=1),
#         skills: Optional[List[str]] = Query(None),
#         min_experience: Optional[int] = Query(None, ge=0),
#         max_salary: Optional[int] = Query(None, ge=0)
# ) -> List[Dict[str, Any]]:
#     """
#     高级简历搜索
#     支持关键词、技能、经验和薪资过滤
#     """
#
#     async def search_resume_data():
#         collection = db["resumes"]  # 使用字典访问方式
#
#         query = {
#             "$or": [
#                 {"name": {"$regex": keyword, "$options": "i"}},
#                 {"skill_description": {"$regex": keyword, "$options": "i"}},
#                 {"self_introduction": {"$regex": keyword, "$options": "i"}}
#             ]
#         }
#
#         if skills:
#             query["skill_description"] = {"$all": skills}
#
#         if min_experience is not None:
#             query["work_years"] = {"$gte": min_experience}
#
#         if max_salary is not None:
#             query["job_intention.salary_max"] = {"$lte": max_salary}
#
#         resumes = await collection.find(query).to_list(length=100)
#
#         for resume in resumes:
#             resume["id"] = str(resume["_id"])
#
#         return resumes
#
#     return await async_retry_with_backoff(search_resume_data)
#
#
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     """
#     处理请求验证错误，返回详细的错误信息
#     """
#     validation_errors = []
#     for error in exc.errors():
#         validation_errors.append({
#             "field": " -> ".join(str(x) for x in error["loc"]),
#             "message": error["msg"],
#             "value": error.get("input", None)
#         })
#
#     return JSONResponse(
#         status_code=422,
#         content={
#             "detail": "数据验证错误",
#             "validation_errors": validation_errors
#         }
#     )
#
#
# @app.patch("/resumes/{user_id}/education", response_model=ResumeResponse)
# @monitor_operation(operation_type="update", collection="resumes")
# async def update_education(
#         user_id: str,
#         education_update: EducationUpdate,
#         db: AsyncIOMotorDatabase = Depends(get_database_instance)
# ):
#     """
#     更新教育经历中的特定字段
#
#     Args:
#         user_id: 用户ID
#         education_update: 要更新的教育经历字段
#
#     Returns:
#         更新后的完整简历信息
#     """
#
#     async def update_education_data():
#         collection = db["resumes"]
#
#         # 获取要更新的字段
#         update_fields = education_update.model_dump(exclude_unset=True)
#         education_id = update_fields.pop('education_id')  # 移除ID字段，仅用于定位
#
#         # 构建更新查询
#         update_query = {
#             "$set": {
#                 f"education_experience.$[elem].{field}": value
#                 for field, value in update_fields.items()
#             }
#         }
#
#         # 使用数组过滤器定位特定的教育经历
#         array_filters = [{"elem.education_id": education_id}]
#
#         # 执行更新
#         result = await collection.update_one(
#             {"_id": ObjectId(user_id)},
#             update_query,
#             array_filters=array_filters
#         )
#
#         if result.matched_count == 0:
#             raise ResumeNotFoundException()
#
#         if result.modified_count == 0:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Education with id {education_id} not found"
#             )
#
#         # 获取更新后的文档
#         updated_resume = await collection.find_one({"_id": ObjectId(user_id)})
#         updated_resume["id"] = str(updated_resume["_id"])
#
#         return updated_resume
#
#     return await async_retry_with_backoff(update_education_data)

@app.post("/batch-update")
async def update_resumes(
    batch_update: BatchResumesUpdate,
    db = Depends(get_database)
) -> Dict[str, Any]:
    """
    Batch update resumes with various operations
    """
    try:
        result = await batch_update_resumes(db, batch_update)
        if not result:
            return {"message": "No updates performed"}
            
        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count,
            "upserted_count": result.upserted_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform batch update: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "resume_v2:app",
        host="0.0.0.0",
        port=9033,
        reload=True
    )