# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 15:58
# @Author  : Galleons
# @File    : routers.py

"""
这里是文件说明
"""

from fastapi import APIRouter, FastAPI
from app.api.v1.endpoints import (
    user, table_fill_api, bilateral_meeting, students_api, mongodb, chat
)

api_router = FastAPI(
    title="AI就业平台",
    summary="包括AI填表、岗位推荐",
    version="0.0.3",
)


api_router.include_router(table_fill_api.router, prefix="/zsk/v1/table_fill", tags=["table-fill-v1"])
api_router.include_router(bilateral_meeting.router, prefix="/zsk/v1/bilateral", tags=["bilateral-v1"])
api_router.include_router(students_api.router, prefix="/zsk/v1/student", tags=["student-v1"])
api_router.include_router(mongodb.router, prefix="/zsk/v1/document", tags=["document-v1"])
api_router.include_router(chat.router, prefix="/zsk/v1/chat", tags=["chat-v1"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "routers:api_router",
        host="192.168.100.73",
        port=9000,
        reload=True
    )
