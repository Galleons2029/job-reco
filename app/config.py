from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "云研云就业岗位推荐服务平台"
    API_V1_STR: str = "/api/v1"
    VERSION:str = "1.0.0"

    # MongoDB configs
    MONGO_DATABASE_HOST: str = "mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app"
#    MONGO_DATABASE_HOST: str = "mongodb+srv://galleons777:galleons@cluster0.b1w6ev1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    MONGO_DATABASE_NAME: str = "admin"
    MONGO_DATABASE_API_PORT: int = 27016

    # 硅基流动API
    Silicon_api_key1: str | None = "sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm"
    Silicon_api_key2: str | None = "sk-kutnkphezarrglswegiqwwaywqqwkvanwjobmwmdjututqkf"
    Silicon_api_key3: str | None = "sk-orbrjhjcqmgezlurbvsmfxqmnjwkmjdrypwdiwvyfarkbnag"
    Silicon_base_url: str | None = "https://api.siliconflow.cn/v1"
    Silicon_model_v1: str | None = "Qwen/Qwen2-72B-Instruct"

    # CometML config
    COMET_API_KEY: str | None = "l0vgJvULBTl8tJfYg6LDG90BV"
    COMET_WORKSPACE: str | None = "galleons2029"
    COMET_PROJECT: str | None = "general"

    # Embeddings config
    #EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_ID: str = "bge-small-zh-v1.5"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 512
    EMBEDDING_MODEL_DEVICE: str = "gpu"

    # 预设（待修改）
    OPENAI_MODEL_ID: str = "qwen2-pro"
    OPENAI_API_KEY: str | None = None

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE_NAME: str = "default"

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_DATABASE_URL: str = "http://localhost:6333"
    QDRANT_CLOUD_URL: str = "str"
    USE_QDRANT_CLOUD: bool = False
    QDRANT_APIKEY: str | None = None

    # LLM Model config
    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str | None = None
    MODEL_TYPE: str = "Qwen/Qwen2-72B-Instruct"

    # RAG config
    TOP_K: int = 5
    KEEP_TOP_K: int = 5
    EXPAND_N_QUERY: int = 5


    QWAK_DEPLOYMENT_MODEL_ID: str = "copywriter_model"
    QWAK_DEPLOYMENT_MODEL_API: str = (
        "https://models.llm-twin.qwak.ai/v1/copywriter_model/default/predict"
    )

settings = Settings()