# job_reco

职位推荐和用户画像系统

## 目录介绍

```coffeescript
.
├── app                   # 项目代码
│   ├── agent_HR              # HR智能体（待启动）
│   ├── crawler               # 自动化爬虫平台（待启动）
│   ├── db                    # 数据库组件
│   ├── evaluation            # 用于评估模型性能
│   └── feature_pipeline      # 特征管道，用于将Mongodb与Qdrant通过RabbitMQ进行同步
│       ├── data_flow            # 流式管道构建
│       ├── data_logic           # 特征数据提取
│       └── models               # 特征数据类建模
│   ├── llm                   # 模型加载库
│   ├── monitoring            # 模型监控组件
│   ├── rag                   # RAG文档检索库，用于构建llm与知识库的连接
│   ├── scripts               # 管道运行脚本
│   └── utils                 # 工具组件，用于数据清洗、文档切分、嵌入等作用
│
└── tests                 # 测试目录
│   └── docs              # 测试文档
```

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

