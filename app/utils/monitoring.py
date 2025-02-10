from functools import wraps
import time
from typing import Any, Callable
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import logging

# 配置日志
logger = logging.getLogger(__name__)

# Prometheus 指标定义
MONGO_OPERATIONS = Counter(
    'mongodb_operations_total',
    'Total number of MongoDB operations',
    ['operation_type', 'collection', 'status']  # 标签用于分类统计
)

MONGO_OPERATION_LATENCY = Histogram(
    'mongodb_operation_latency_seconds',
    'MongoDB operation latency in seconds',
    ['operation_type', 'collection']  # 用于统计操作延迟分布
)

MONGO_CONNECTION_POOL = Gauge(
    'mongodb_connection_pool_size',
    'MongoDB connection pool size',
    ['pool_type']  # 监控连接池状态
)

MONGO_ERRORS = Counter(
    'mongodb_errors_total',
    'Total number of MongoDB errors',
    ['error_type']  # 错误类型统计
)

MONGO_POOL_METRICS = Gauge(
    'mongodb_pool_metrics',
    'MongoDB connection pool metrics',
    ['metric_type']  # current, available, max
)

MONGO_POOL_WAIT_QUEUE = Gauge(
    'mongodb_pool_wait_queue',
    'MongoDB connection pool wait queue size',
    ['queue_type']  # size, timeout
)

async def async_retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    exponential_base: float = 2,
    logger: logging.Logger = logger
) -> Any:
    """
    异步重试装饰器，使用指数退避策略
    
    参数:
        func: 需要重试的异步函数
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        exponential_base: 指数基数
    """
    retries = 0
    delay = initial_delay

    while True:
        try:
            return await func()
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Maximum retries ({max_retries}) reached. Last error: {str(e)}")
                raise

            delay = min(delay * exponential_base, max_delay)
            logger.warning(f"Retry {retries}/{max_retries} after {delay:.2f}s. Error: {str(e)}")
            await asyncio.sleep(delay)

def monitor_operation(operation_type: str, collection: str):
    """
   监控 MongoDB 操作的装饰器
    
    参数:
        operation_type: 操作类型（如：insert, query, update, delete）
        collection: 集合名称
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                MONGO_OPERATIONS.labels(
                    operation_type=operation_type,
                    collection=collection,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                MONGO_OPERATIONS.labels(
                    operation_type=operation_type,
                    collection=collection,
                    status="error"
                ).inc()
                MONGO_ERRORS.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                MONGO_OPERATION_LATENCY.labels(
                    operation_type=operation_type,
                    collection=collection
                ).observe(duration)
        return wrapper
    return decorator 