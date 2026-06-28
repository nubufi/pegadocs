import os

from pydantic import Field
from pydantic_settings import BaseSettings

cpu_count = os.cpu_count() or 1
num_workers = cpu_count * 4


class Settings(BaseSettings):
    """Application settings"""

    ENV: str = Field(default="prod")
    ENABLE_MOCK_API: bool = Field(default=False)
    SPIDER_WEB_API_KEY: str = Field(default="")

    # Redis
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")

    # S3 Storage
    S3_DATA_SOURCE_BUCKET_NAME: str = Field(default="")
    S3_EMBEDDING_BUCKET_NAME: str = Field(default="")

    # Supabase
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="")

    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1)
    TEST_API_KEY: str = Field(default="")
    FERNET_SECRET_KEY: str = Field(default="")

    CHUNK_SIZE: int = Field(default=500)
    CHUNK_OVERLAP: int = Field(default=20)
    MAX_WORKERS: int = Field(default=num_workers)

    # Table names
    API_KEYS_TABLE_NAME: str = Field(default="api_keys")
    CHAT_HISTORY_TABLE_NAME: str = Field(default="chats")
    COLLECTIONS_TABLE_NAME: str = Field(default="collections")
    DATA_SOURCES_TABLE_NAME: str = Field(default="data_sources")
    DATABASE_TABLE_NAME: str = Field(default="databases")
    MODELS_TABLE_NAME: str = Field(default="models")
    PROMPT_TABLE_NAME: str = Field(default="prompts")
    REFERENCE_CODES_TABLE_NAME: str = Field(default="reference_codes")
    JOB_STATUS_TABLE_NAME: str = Field(default="job_status")
    FILE_STATUS_TABLE_NAME: str = Field(default="file_status")
    NODES_TABLE_NAME: str = Field(default="nodes_status")

    SITE_URL: str = Field(default="https://pegadocs.com")

    RESEND_API_KEY: str = Field(default="")
    RESEND_FROM_EMAIL: str = Field(default="")

    TASK_STORE: str = Field(default="redis")  # or "dynamodb"
    DDB_TABLE: str = Field(default="tasks")
    TTL_SECONDS: int = Field(default=24 * 3600)  # 1 days

    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="eu-central-1")

    DEFAULT_VECTOR_BUCKET_NAME: str = Field(default="")
    SENTRY_DSN: str = Field(default="")
    EMBEDDING_JOBS_SQS_URL: str = Field(default="")

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
