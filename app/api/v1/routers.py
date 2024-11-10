# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:58
# @Author  : Galleons
# @File    : routers.py

"""
就业平台终端
"""

import logging
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.endpoints import (
    users, table_fill_api, bilateral_meeting, students_api, chat, student_v2, recom, jobs_api
)

# api_router = APIRouter()
api_router = FastAPI(
    title="AI就业平台",
    summary="包括AI填表、岗位推荐",
    version="0.0.3",
)


api_router.include_router(table_fill_api.router, prefix="/zsk/v1/table_fill", tags=["table-fill-v1"])
api_router.include_router(bilateral_meeting.router, prefix="/zsk/v1/bilateral", tags=["bilateral-v1"])
api_router.include_router(students_api.router, prefix="/zsk/v1/student", tags=["student-v1"])
# api_router.include_router(mongodb.router, prefix="/zsk/v1/document", tags=["document-v1"])
api_router.include_router(chat.router, prefix="/zsk/v1/chat", tags=["chat-v1"])
api_router.include_router(users.router, prefix="/zsk/v1/user", tags=["user-v1"])
api_router.include_router(student_v2.router, prefix="/zsk/v2/student", tags=["student-v2"])
api_router.include_router(recom.router, prefix="/zsk/v2/recom", tags=["recom-v2"])
api_router.include_router(jobs_api.router, prefix="/zsk/v2/jobs", tags=["jobs-v2"])



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


@api_router.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    error_messages = []
    for error in exc.errors():
        error_messages.append({
            'field': error['loc'][0],  # 获取字段名
            'message': error['msg'],    # 获取错误信息
            'type': error['type']       # 获取错误类型
        })
    return JSONResponse(
        status_code=422,
        content={'detail': error_messages}
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "routers:api_router",
        host="192.168.100.146",
        port=9000,
        reload=True
    )
