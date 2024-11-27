# -*- coding: utf-8 -*-
# @Time    : 2024/11/20 17:05
# @Author  : Galleons
# @File    : webm2mp3.py

"""
这里是文件说明
"""

from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from moviepy.video.io.VideoFileClip import VideoFileClip
from typing import Dict, Optional
from pathlib import Path
import shutil
import uuid
import os
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时清理所有遗留的临时文件"""
    # 清理上传目录
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    UPLOAD_DIR.mkdir(exist_ok=True)

    # 清理输出目录
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="WebM 转 MP3 API",
    description="用来将WebM文件转换为MP3格式的API服务 ",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置常量
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSION = ".webm"

# 确保必要的目录存在
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 存储转换任务的状态
conversion_tasks: Dict[str, Dict] = {}


class ConversionStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def cleanup_old_files():
    """清理24小时前的文件"""
    current_time = time.time()

    # 清理上传目录
    for file_path in UPLOAD_DIR.glob("*"):
        if current_time - file_path.stat().st_mtime > 24 * 3600:
            file_path.unlink(missing_ok=True)

    # 清理输出目录
    for file_path in OUTPUT_DIR.glob("*"):
        if current_time - file_path.stat().st_mtime > 24 * 3600:
            file_path.unlink(missing_ok=True)


async def convert_webm_to_mp3(task_id: str, input_path: Path, output_path: Path):
    """在后台进行WebM到MP3的转换"""
    try:
        conversion_tasks[task_id]["status"] = ConversionStatus.PROCESSING

        # 加载WebM文件
        video = VideoFileClip(str(input_path))

        # 提取音频并保存为MP3
        video.audio.write_audiofile(
            str(output_path),
            logger=None  # 禁用moviepy的进度输出
        )

        # 清理资源
        video.close()

        conversion_tasks[task_id].update({
            "status": ConversionStatus.COMPLETED,
            "output_filename": output_path.name
        })

        # 删除原始文件
        input_path.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Conversion failed for task {task_id}: {str(e)}")
        conversion_tasks[task_id].update({
            "status": ConversionStatus.FAILED,
            "error": str(e)
        })
        # 清理文件
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


@app.post("/convert")
async def upload_and_convert(
        file: UploadFile,
        background_tasks: BackgroundTasks
) -> Dict:
    """
    上传WebM文件并转换为MP3格式

    - 参数:
        - file: WebM格式的音频文件

    - 返回:
        - task_id: 转换任务ID
        - status: 任务状态
    """
    # 验证文件扩展名
    if not file.filename.lower().endswith(ALLOWED_EXTENSION):
        raise HTTPException(
            status_code=400,
            detail=f"只支持{ALLOWED_EXTENSION}格式的文件"
        )

    # 生成唯一的任务ID
    task_id = str(uuid.uuid4())

    # 创建输入和输出文件路径
    input_path = UPLOAD_DIR / f"{task_id}{ALLOWED_EXTENSION}"
    output_path = OUTPUT_DIR / f"{task_id}.mp3"

    try:
        # 保存上传的文件
        with open(input_path, "wb") as buffer:
            # 分块读取文件以处理大文件
            while chunk := await file.read(8192):
                # 检查文件大小限制
                if input_path.stat().st_size + len(chunk) > MAX_FILE_SIZE:
                    input_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件大小不能超过{MAX_FILE_SIZE / 1024 / 1024}MB"
                    )
                buffer.write(chunk)

        # 记录转换任务
        conversion_tasks[task_id] = {
            "status": ConversionStatus.PENDING,
            "original_filename": file.filename,
            "timestamp": time.time()
        }

        # 在后台开始转换
        background_tasks.add_task(
            convert_webm_to_mp3,
            task_id,
            input_path,
            output_path
        )

        # 清理旧文件
        background_tasks.add_task(cleanup_old_files)

        return {
            "task_id": task_id,
            "status": ConversionStatus.PENDING
        }

    except Exception as e:
        # 清理文件
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)

        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="文件上传失败"
        )


@app.get("/status/{task_id}")
async def get_conversion_status(task_id: str) -> Dict:
    """
    获取转换任务的状态

    - 参数:
        - task_id: 转换任务ID

    - 返回:
        - task_id: 转换任务ID
        - status: 任务状态
        - error: 错误信息（如果失败）
    """
    if task_id not in conversion_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )

    return {
        "task_id": task_id,
        **conversion_tasks[task_id]
    }


@app.get("/download/{task_id}")
async def download_converted_file(task_id: str) -> FileResponse:
    """
    下载转换完成的MP3文件

    - 参数:
        - task_id: 转换任务ID

    - 返回:
        - MP3文件
    """
    if task_id not in conversion_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )

    task = conversion_tasks[task_id]

    if task["status"] != ConversionStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="文件转换尚未完成"
        )

    output_path = OUTPUT_DIR / f"{task_id}.mp3"
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )

    return FileResponse(
        path=output_path,
        filename=task["original_filename"].replace(ALLOWED_EXTENSION, ".mp3"),
        media_type="audio/mpeg"
    )




# 如果直接运行此文件
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("webm2mp3:app", host="localhost", port=7000,reload=True)
