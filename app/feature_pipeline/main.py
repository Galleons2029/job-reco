from bytewax.dataflow import Dataflow
from app.db.qdran import QdrantDatabaseConnector
from app.feature_pipeline.data_flow.stream_input import RabbitMQSource
from app.feature_pipeline.data_flow.stream_output import QdrantOutput

import bytewax.operators as op


from app.feature_pipeline.data_logic.dispatchers import (
    ChunkingDispatcher,
    CleaningDispatcher,
    EmbeddingDispatcher,
    RawDispatcher,
)

connection = QdrantDatabaseConnector()

flow = Dataflow("流式摄取管道")   # 初始化管道流
stream = op.input("输入", flow, RabbitMQSource()) # 从队列中读取数据

stream = op.map("原始调度",
                stream,
                RawDispatcher.handle_mq_message
)   # 将JSON映射为Pydantic模式

stream = op.map("清理调度",
                stream,
                CleaningDispatcher.dispatch_cleaner
)   # 数据清洗

op.output(
    "清理后的数据导入到qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="clean"),
)

stream = op.flat_map("分块调度",
                     stream,
                     ChunkingDispatcher.dispatch_chunker
)

stream = op.map(
    "嵌入块调度", stream, EmbeddingDispatcher.dispatch_embedder
)

op.output(
    "嵌入数据导入到qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="vector"),
)
