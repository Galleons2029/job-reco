# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:58
# @Author  : Galleons
# @File    : routers.py

"""
就业平台终端
"""

import logging
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from pydantic import ValidationError

from app.api.v1.endpoints import (
    users, table_fill_api, bilateral_meeting, students_api, student_v2
)
from app.api.v2.endpoints import (
    jobs_api_v2, meeting_api, recom, category_api, resume_v1, school_v1
)

# api_router = APIRouter()
api_router = FastAPI(
    title="AI就业平台",
    summary="包括AI填表、岗位推荐",
    version="1.1.0",
)


api_router.include_router(table_fill_api.router, prefix="/zsk/v1/table_fill", tags=["table-fill-v1"])
api_router.include_router(bilateral_meeting.router, prefix="/zsk/v1/bilateral", tags=["bilateral-v1"])
api_router.include_router(students_api.router, prefix="/zsk/v1/student", tags=["student-v1"])
# api_router.include_router(chat.router, prefix="/zsk/v1/chat", tags=["chat-v1"])
# api_router.include_router(chat_v2.router, prefix="/zsk", tags=["chat-v1"])

api_router.include_router(users.router, prefix="/zsk/v1/user", tags=["user-v1"])
api_router.include_router(student_v2.router, prefix="/test/zsk/v2/student", tags=["student-v2"])
api_router.include_router(recom.router, prefix="/test/zsk/v2/recom", tags=["recom-v2"])
api_router.include_router(jobs_api_v2.router, prefix="/test/zsk/v2/jobs", tags=["jobs-v2"])
api_router.include_router(meeting_api.router, prefix="/test/zsk/v2/meetings", tags=["meetings-v2"])
api_router.include_router(category_api.router, prefix="/test/zsk/v1/career", tags=["career-v1"])
api_router.include_router(resume_v1.router, prefix="/test/zsk", tags=["resume-v1"])
api_router.include_router(school_v1.router, prefix="/test/zsk", tags=["schools-v1"])





# CORS配置
api_router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @api_router.on_event("startup")
# async def startup():
#     await db.connect()
#
#
# @api_router.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()



@api_router.middleware("http")
async def log_request(request: Request, call_next):
    # 仅在请求方法是 POST 时处理 JSON 请求体
    if request.method == "POST":
        try:
            body = await request.json()  # 尝试解析 JSON 请求体
            logging.info(f"Request body: {body}")
        except Exception as e:
            logging.error(f"Failed to parse JSON: {e}")

    # 继续请求处理
    response = await call_next(request)
    return response


@api_router.post("/items/")
async def create_item(item: dict):
    return item


# @api_router.exception_handler(ValidationError)
# async def validation_exception_handler(request, exc: ValidationError):
#     error_messages = []
#     for error in exc.errors():
#         error_messages.append({
#             'field': error['loc'][0],  # 获取字段名
#             'message': error['msg'],    # 获取错误信息
#             'type': error['type']       # 获取错误类型
#         })
#     return JSONResponse(
#         status_code=422,
#         content={'detail': error_messages}
#     )

@api_router.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误，返回详细的错误信息
    """
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "字段": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "value": error.get("input", None)
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "数据验证错误",
            "validation_errors": validation_errors
        }
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "routers:api_router",
        host="0.0.0.0",
        port=9001,
        # reload=True,
        # reload_excludes=["*.pyc", "*.pyo", "*.pyd", "*/__pycache__/*", "*.py"],  # 排除不需要监视的文件
        # reload_includes=["resume_v1.py","resumes.py"],  # 只监视特定类型的文件
    )
