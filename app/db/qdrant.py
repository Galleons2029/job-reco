# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 15:54
# @Author  : Galleons
# @File    : qdrant.py

"""
这里是文件说明
"""

# utils/qdrant_client.py
import logging
from typing import Optional
from contextlib import contextmanager
from qdrant_client import QdrantClient, models

from app.config import get_qdrant_settings

logger = logging.getLogger(__name__)


class QdrantClientManager:
    _instance: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        获取Qdrant客户端单例实例
        """
        if cls._instance is None:
            settings = get_qdrant_settings()
            try:
                cls._instance = QdrantClient(
                    url=f"{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
                    api_key=settings.QDRANT_API_KEY,
                    prefer_grpc=settings.QDRANT_PREFER_GRPC,
                    timeout=settings.QDRANT_TIMEOUT,
                    https=settings.QDRANT_HTTPS
                )
                logger.info("Successfully initialized Qdrant client connection")
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant client: {str(e)}")
                raise
        return cls._instance

    @classmethod
    def check_health(cls) -> bool:
        """
        检查Qdrant服务健康状态
        """
        try:
            client = cls.get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False

    @classmethod
    @contextmanager
    def get_client_context(cls):
        """
        提供上下文管理器方式使用客户端
        """
        client = None
        try:
            client = cls.get_client()
            yield client
        except Exception as e:
            logger.error(f"Error during Qdrant client usage: {str(e)}")
            raise
        finally:
            if client:
                # 这里可以添加任何需要的清理操作
                pass




