# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 17:45
# @Author  : Galleons
# @File    : resume_v1.py

"""
人才简历CURD接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional, Dict, Any

from pydantic import ValidationError, BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import logging

from app.db.models.resumes import (
    Resume, ResumeUpdate, ResumeResponse, ListUpdateOperation,
    JobIntentionUpdate, ProfileUpdater, Batch_resumes_update, resume_recom
)
from app.db.mongodb import MongoDBManager, get_database_instance
from app.utils.monitoring import monitor_operation, async_retry_with_backoff
from app.api.v2.dependencies.exceptions import ResumeNotFoundException, DuplicateResumeException

# router = FastAPI(title="Resume Management API")

router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)

# 创建简历
@router.post("/resumes/create_resume", response_model=ResumeResponse, status_code=201)
@monitor_operation(operation_type="insert", collection="resumes")
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
        db = mongo_client["resumes"]
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



# 更新简历
@router.post("/resumes/update_resume", response_model=List[ResumeResponse])
@monitor_operation(operation_type="batch_update", collection="resumes")
async def update_resume(
    batch_data: Batch_resumes_update,
    mongo_client: AsyncIOMotorClient = Depends(get_database_instance)
):
    """
    批量更新简历
    
    Args:
        batch_data: 包含多个简历更新数据的批量请求
        mongo_client: MongoDB客户端实例

        batch_data格式说明：
        {
            :param 基础字段： user_id, name, gender 等个人基础信息
            :param 复杂字段： 教育经历、工作经历等嵌套字典
            复杂字段组成：
                :param operation: 复杂字段支持操作类型： 添加（append）、更新（update）、删除（delete）
                :param data: 数据内容：List[T]用于追加/替换，Dict[int, T]用于更新特定索引，List[int]用于删除操作
        }

    
    Returns:
        List[ResumeResponse]: 更新后的简历列表
    """
    logger.info(f"开始批量更新简历 - 数量: {len(batch_data.resumes)}")
    
    results = []
    errors = []

    try:
        updater = ProfileUpdater(
            mongo_client=mongo_client,
            database="resumes",
            collection="resumes_test"
        )

        for profile_data in batch_data.resumes:
            try:
                # 确保异步操作正确等待
                result = await updater.update_profile(profile_data)
                if result:
                    results.append(ResumeResponse(**result))
                else:
                    errors.append({
                        "user_id": profile_data.user_id,
                        "error": "Resume not found"
                    })
            except Exception as e:
                logger.error(f"更新简历失败 - 用户ID: {profile_data.user_id}, 错误: {str(e)}")
                errors.append({
                    "user_id": profile_data.user_id,
                    "error": str(e)
                })
        
        if errors:
            logger.error(f"批量更新过程中发生错误: {errors}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "部分简历更新失败",
                    "errors": errors,
                    "successful_updates": len(results)
                }
            )
        
        return results

    except Exception as e:
        logger.error(f"批量更新简历时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"批量更新简历失败: {str(e)}"
        )
    finally:
        updater.close()


class BatchDeleteRequest(BaseModel):
    user_ids: List[int] = Field(..., description="要删除的用户ID列表")
    is_school_user: bool | None= Field(False, description="是否是高校群体")

class DeleteResult(BaseModel):
    success: List[int] = Field(default_factory=list, description="成功删除的用户ID")
    failed: List[dict] = Field(default_factory=list, description="删除失败的用户ID及原因")
    total_deleted: int = Field(default=0, description="成功删除的总数")

@router.post("/resumes/delete", response_model=DeleteResult)
@monitor_operation(operation_type="batch_delete", collection="resumes")
async def batch_delete_resumes(
        request: BatchDeleteRequest,
        db: AsyncIOMotorClient = Depends(get_database_instance)
):
    """批量删除简历

    Args:
        request: 包含要删除的用户ID列表和用户类型
        db: MongoDB客户端实例

    Returns:
        DeleteResult: 删除操作的结果，包含成功和失败的详情
    """
    async def delete_resume_data():
        collection = db.resumes.resumes_test
        result = DeleteResult()
        
        for user_id in request.user_ids:
            try:
                # 构建查询条件
                query = {
                    "user_id": user_id,
                    "is_school_user": request.is_school_user
                }
                
                # 检查是否存在
                existing_resume = await collection.find_one(query)
                if not existing_resume:
                    result.failed.append({
                        "user_id": user_id,
                        "reason": "Resume not found"
                    })
                    continue

                # 执行删除
                delete_result = await collection.delete_one(query)
                if delete_result.deleted_count > 0:
                    result.success.append(user_id)
                    result.total_deleted += 1
                else:
                    result.failed.append({
                        "user_id": user_id,
                        "reason": "Delete operation failed"
                    })
            except Exception as e:
                result.failed.append({
                    "user_id": user_id,
                    "reason": str(e)
                })

        return result

    try:
        result = await async_retry_with_backoff(delete_resume_data)
        
        # 如果所有操作都失败，返回500错误
        if not result.success and result.failed:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "All delete operations failed",
                    "failures": result.failed
                }
            )
            
        return result
        
    except Exception as e:
        logger.error(f"批量删除简历时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"批量删除简历失败: {str(e)}"
        )


from app.db.qdrant import QdrantClientManager


# 在文件顶部添加分页响应模型
class PaginatedRecommendationResponse(BaseModel):
    data: List[int]  # 改为整数列表，而不是二维列表
    total: int
    page_size: int


@router.post("/resumes/recom", response_model=PaginatedRecommendationResponse)
async def get_resume_recommendations(
        resumes_request: resume_recom,
        mongo_client: AsyncIOMotorClient = Depends(get_database_instance)
):
    """获取简历推荐，返回分页结果"""
    try:
        with QdrantClientManager.get_client_context() as qdrant_client:
            if resumes_request.is_school_user:
                collection = mongo_client.resumes.resumes
            else:
                collection = mongo_client.resumes.resumes

            pipeline = []
            match_dict = {"user_id": {"$exists": True, "$ne": None},
                          # "is_school_user": resumes_request.is_school_user
                          "percent_complete": {
                                "$gte": 70,
                            },
                          # "orderdate": {
                          #     "$gte": datetime(2020, 1, 1, 0, 0, 0),
                          #     "$lt": datetime(2021, 1, 1, 0, 0, 0)
                          # }
                          }

            # # 获取 Qdrant 搜索结果
            # search_results = qdrant_client.retrieve(
            #     collection_name='job_test3',
            #     ids=[resumes_request.publish_id],
            # )

            # 构建查询管道
            if resumes_request.school_id:
                match_dict["school_id"] = resumes_request.school_id
            if resumes_request.profession:
                match_dict["profession"] = resumes_request.profession
            if resumes_request.gender.value:
                match_dict["gender"] = resumes_request.gender.value

            pipeline.append({
                "$match": match_dict
            })

            # 获取总数
            count_pipeline = pipeline.copy()
            count_pipeline.append({"$count": "total"})
            total = 0
            async for doc in collection.aggregate(count_pipeline):
                total = doc["total"]
                break

            # 添加分页到管道
            pipeline.extend([
                {"$skip": (resumes_request.page - 1) * resumes_request.page_size},
                {"$limit": resumes_request.page_size}
            ])

            # 执行查询并收集结果
            results = []
            async for doc in collection.aggregate(pipeline):
                if 'user_id' in doc:
                    results.append(doc['user_id'])

            logger.debug(f"在第{resumes_request.page}页找到 {len(results)} 份匹配简历。")

            return PaginatedRecommendationResponse(
                data=results,
                total=total,
                page_size=resumes_request.page_size
            )

    except Exception as e:
        logger.error(f"推荐查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推荐查询失败: {str(e)}")


# @router.exception_handler(RequestValidationError)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "resume_v1:router",
        host="0.0.0.0",
        port=9033,
        reload=True
    )