from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    app_name: str = Field(default="TrimTrack")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    base_url: str = Field(default="http://localhost:8000")
    ngrok_url: Optional[str] = Field(default=None)  
    debug: bool = Field(default=False)

    database_url: str = Field(
        default="postgresql+asyncpg://urlshortener:urlshortener@localhost:5432/urlshortener"
    )
    sqlite_fallback: bool = Field(default=False)
    sqlite_url: str = Field(default="sqlite+aiosqlite:///./urlshortener.db")

    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: Optional[str] = Field(default=None)

    machine_id: int = Field(default=1, ge=0, le=1023)

    rate_limit_redirect: int = Field(default=100)
    rate_limit_create: int = Field(default=10)
    rate_limit_window: int = Field(default=60)

    cache_ttl: int = Field(default=86400)  
    cache_warm_top_n: int = Field(default=1000)

    bloom_filter_capacity: int = Field(default=1_000_000)
    bloom_filter_error_rate: float = Field(default=0.001)

    safety_score_threshold: float = Field(default=0.5)
    ml_model_path: str = Field(default="ml/model.pkl")

    geo_api_url: str = Field(default="http://ip-api.com/json")

    prometheus_enabled: bool = Field(default=True)

    db_pool_min: int = Field(default=5)
    db_pool_max: int = Field(default=20)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
