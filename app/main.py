from fastapi import FastAPI
from xinference.thirdparty.deepseek_vl.serve.app_modules.presets import description

from app.api.v1.routers import api_router
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME,
              description="基于大模型岗位推送平台",
              version=settings.VERSION,
              )

app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="192.168.100.146",
        port=9001,
        reload=True
    )