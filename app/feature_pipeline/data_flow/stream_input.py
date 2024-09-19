import json
from datetime import datetime
import time
from typing import Generic, Iterable, List, Optional, TypeVar
from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition
from app.config import settings
from app.feature_pipeline.mq import RabbitMQConnection
from app.utils.logging import get_logger

logger = get_logger(__name__)

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")

class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    """
    负责在 bytewax 和 rabbitmq 之间创建连接的类，促进数据从 mq 到 bytewax 流处理管道的传输。
    继承自 StatefulSourcePartition，以实现快照功能，能够保存队列的状态。
    """

    def __init__(self, queue_name: str, resume_state: MessageT | None = None) -> None:
        self._in_flight_msg_ids = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()
        self.connection.connect()
        self.channel = self.connection.get_channel()

    def next_batch(self, sched: Optional[datetime] = None) -> Iterable[DataT]:
        try:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name, auto_ack=True
            )
        except Exception:
            logger.error(
                f"从队列获取消息时出错。", queue_name=self.queue_name
            )
            time.sleep(5)  # 在重试访问队列之前睡眠 5 秒。

            self.connection.connect()
            self.channel = self.connection.get_channel()

            return []

        if method_frame:
            message_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(message_id)

            return [json.loads(body)]
        else:
            return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):
    def list_parts(self) -> List[str]:
        return ["single partition"]

    def build_part(
        self, now: datetime, for_part: str, resume_state: MessageT | None = None
    ) -> StatefulSourcePartition[DataT, MessageT]:
        return RabbitMQPartition(queue_name=settings.RABBITMQ_QUEUE_NAME)
