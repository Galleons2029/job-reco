from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from xinference.thirdparty.deepseek_vl.serve.app_modules.presets import description

from app.api.routers import api_router
from app.config import settings

import logging

app = FastAPI(title=settings.PROJECT_NAME,
              description="基于大模型岗位推送平台",
              version=settings.VERSION,
              )

app.include_router(api_router, prefix=settings.API_V1_STR)



@app.middleware("http")
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

@app.post("/items/")
async def create_item(item: dict):
    return item


@app.exception_handler(ValidationError)
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
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )