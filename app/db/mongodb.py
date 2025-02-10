# -*- coding: utf-8 -*-
# @Time    : 2025/1/8 11:07
# @Author  : Galleons
# @File    : mongodb.py

"""
MongoDB 连接模块
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Any, Dict, List
import time

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from prometheus_client import start_http_server
from fastapi import HTTPException, Depends
from pymongo import UpdateOne

from app.config import settings
from app.utils.monitoring import (
    async_retry_with_backoff,
    monitor_operation,
    MONGO_CONNECTION_POOL,
    MONGO_ERRORS
)
from app.db.models.resume_update import ResumeUpdate, BatchResumesUpdate, UpdateOperation

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """自定义数据库连接异常"""
    pass


class MongoDBManager:
    """MongoDB 连接管理器，提供数据库连接和操作接口"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_to_database(cls) -> None:
        """
        建立数据库连接
        
        特性:
        - 连接池配置
        - 重试机制
        - 连接验证
        - 指标收集
        """
        async def connect_attempt():
            # 配置连接池和超时设置
            cls.client = AsyncIOMotorClient(
                settings.MONGO_DATABASE_HOST,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                connectTimeoutMS=5000,
            )
            
            cls.db = cls.client[settings.MONGO_DATABASE_NAME]
            
            # 验证连接
            await cls.client.admin.command('ping')
            
            # 更新连接池指标 - 使用服务器状态信息
            server_status = await cls.client.admin.command('serverStatus')
            current_connections = server_status["connections"]["current"]
            available_connections = server_status["connections"]["available"]
            
            MONGO_CONNECTION_POOL.labels(pool_type="current").set(current_connections)
            MONGO_CONNECTION_POOL.labels(pool_type="available").set(available_connections)
            MONGO_CONNECTION_POOL.labels(pool_type="max").set(settings.MONGO_MAX_POOL_SIZE)
            
            logger.info(f"Successfully connected to MongoDB. Active connections: {current_connections}")

        try:
            await async_retry_with_backoff(
                connect_attempt,
                max_retries=3,
                initial_delay=0.1,
                max_delay=2.0
            )
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            MONGO_ERRORS.labels(error_type=type(e).__name__).inc()
            raise DatabaseConnectionError(f"Database connection error: {str(e)}")

    @classmethod
    @monitor_operation(operation_type="query", collection="health_check")
    async def check_health(cls) -> Dict[str, Any]:
        """
        增强的健康检查
        
        返回:
            Dict 包含:
            - 连接状态
            - 延迟信息
            - 连接池统计
            - 操作计数
            - 时间戳
        """
        try:
            if not cls.client:
                return {
                    "status": "unhealthy",
                    "message": "No database connection",
                    "timestamp": time.time()
                }

            start_time = time.time()
            await cls.client.admin.command('ping')
            latency = time.time() - start_time

            # 获取服务器状态
            server_status = await cls.client.admin.command('serverStatus')
            
            return {
                "status": "healthy",
                "latency_ms": round(latency * 1000, 2),
                "connections": {
                    "current": server_status["connections"]["current"],
                    "available": server_status["connections"]["available"],
                    "total_created": server_status["connections"]["totalCreated"]
                },
                "operations": {
                    "insert": server_status["opcounters"]["insert"],
                    "query": server_status["opcounters"]["query"],
                    "update": server_status["opcounters"]["update"],
                    "delete": server_status["opcounters"]["delete"]
                },
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            MONGO_ERRORS.labels(error_type=type(e).__name__).inc()
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": time.time()
            }

    @classmethod
    async def close_database_connection(cls) -> None:
        """关闭数据库连接"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    async def get_db(cls, database_name: Optional[str] = None) -> AsyncIOMotorDatabase:
        """
        获取数据库实例
        
        Args:
            database_name: 可选的数据库名称，如果未提供则使用默认配置
            
        Returns:
            AsyncIOMotorDatabase: MongoDB数据库实例
        """
        if cls.client is None:
            await cls.connect_to_database()
            
        db_name = database_name or settings.MONGO_DATABASE_NAME
        return cls.client[db_name]


@asynccontextmanager
async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """数据库连接的上下文管理器"""
    try:
        await MongoDBManager.connect_to_database()
        yield MongoDBManager.db
    finally:
        await MongoDBManager.close_database_connection()


# 在 FastAPI 应用中使用的 lifespan 事件处理
@asynccontextmanager
async def lifespan(app: "FastAPI"):  # type: ignore
    """
    FastAPI 应用的生命周期管理
    使用方法：
    app = FastAPI(lifespan=lifespan)
    """
    try:
        # 启动 Prometheus 指标服务器
        start_http_server(settings.METRICS_PORT)
        await MongoDBManager.connect_to_database()
        yield
    finally:
        await MongoDBManager.close_database_connection()


# 用于依赖注入的异步函数
async def get_database_instance() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """获取数据库连接实例"""
    client = AsyncIOMotorClient(
        settings.MONGO_DATABASE_HOST,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        connectTimeoutMS=5000,
    )
    try:
        # 验证连接
        await client.admin.command('ping')
        yield client
    finally:
        client.close()


async def build_update_operation(resume_update: ResumeUpdate) -> List[UpdateOne]:
    operations = []
    
    # Handle basic field updates
    if resume_update.basic_updates:
        operations.append(
            UpdateOne(
                {"user_id": resume_update.user_id},
                {"$set": resume_update.basic_updates}
            )
        )
    
    # Handle list operations
    if resume_update.list_operations:
        for list_op in resume_update.list_operations:
            query = {"user_id": resume_update.user_id}
            
            if list_op.operation == UpdateOperation.UPDATE:
                # Add field ID to query for specific item update
                query[f"{list_op.field_name}.{list_op.field_id_name}"] = list_op.field_id
                # Use positional $ operator to update matched array element
                set_dict = {
                    f"{list_op.field_name}.$.{key}": value 
                    for key, value in list_op.data.items()
                }
                operations.append(
                    UpdateOne(query, {"$set": set_dict})
                )
                
            elif list_op.operation == UpdateOperation.APPEND:
                operations.append(
                    UpdateOne(
                        {"user_id": resume_update.user_id},
                        {"$push": {list_op.field_name: list_op.data}}
                    )
                )
                
            elif list_op.operation == UpdateOperation.DELETE:
                operations.append(
                    UpdateOne(
                        {"user_id": resume_update.user_id},
                        {"$pull": {
                            list_op.field_name: {
                                list_op.field_id_name: list_op.field_id
                            }
                        }}
                    )
                )
    
    return operations

async def batch_update_resumes(db, batch_update: BatchResumesUpdate):
    """
    Perform batch updates on resume documents
    """
    all_operations = []
    
    for resume_update in batch_update.updates:
        operations = await build_update_operation(resume_update)
        all_operations.extend(operations)
    
    if all_operations:
        result = await db.resumes.bulk_write(all_operations)
        return result
    
    return None

