# job_reco

职位推荐和用户画像系统，使用Mongodb作为文档数据库存取文档

## 目录介绍

```coffeescript
.
.
├── app：项目代码
│   ├── agent_HR：HR智能体（待启动）
│   ├── crawler：自动化爬虫平台（待启动）
│   ├── db：数据库组件
│   │        ├── api.py：基于fastapi对Mongodb增删改查的接口封装
│   │        ├── document.py：与 MongoDB 交互的基础框架
│   │        ├── models.py：文档数据建模
│   │        ├── mongo.py：用于连接到 MongoDB 数据库的单例类
│   │        ├── qdran.py：Qdrant交互接口
│   │        └── setup.py：Mongodb初始化
│   ├── evaluation：用于评估模型性能
│   ├── feature_pipeline：特征管道，用于将Mongodb与Qdrant通过RabbitMQ进行同步
│   │     ├── data_flow：基于Bytewax构建的流式管道
│   │     │      ├── stream_input.py：摄取RabbitMQ消息的管道入口
│   │     │      └── stream_output.py：导入Qdrant的管道出口
│   │     ├── data_logic：特征数据提取
│   │     │      ├── chunking_data_handler.py：分块数据句柄
│   │     │      ├── cleaning_data_handler.py：清洗数据句柄
│   │     │      ├── dispatchers.py：数据分发
│   │     │      └── embedding_data_handler.py：嵌入数据句柄
│   │     ├── models：特征数据类建模
│   │     │      └─api.py：
│   │     ├── cdc.py：特征数据类建模
│   │     ├── main.py：特征数据类建模
│   │     ├── mq.py：特征数据类建模
│   │     └── test_cdc.py：特征数据类建模
│   ├── llm：模型加载库
│   ├── monitoring：模型监控组件
│   ├── rag：RAG文档检索库，用于构建llm与知识库的连接
│   ├── scripts：管道运行脚本
│   └── utils：公共工具函数库，用于数据清洗、文档切分、嵌入等作用
│         ├── chunking.py：特征数据提取
│         ├── cleaning.py：特征数据提取
│         ├── embeddings.py：特征数据提取
│         └── logging.py：日志加载文件
│ 
│── tests：测试目录
│    └── docs：测试文档
│    
└─requirements.txt：python依赖库
```



# 设计文档

详细 









## 快速开始

使用 **TOX** 构建，支持 **CI** 跨平台，跨版本测试。测试可以使用TOX 自动完成

1. 安装TOX
    ```bash
    pip install tox
    ```

2. 测试代码
    ```bash
    tox
    ```
   
## TODO List

