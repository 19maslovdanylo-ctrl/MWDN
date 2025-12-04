from functools import lru_cache
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Auction Service"
    app_version: str = "1.0.0"
    debug: bool = False

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "app_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Read Replica Configuration
    postgres_read_replica_host: str = "db_read_replica"
    postgres_read_replica_port: int = 5432

    database_url: str | None = None
    async_database_url: str | None = None

    read_replica_database_url: str | None = None
    async_read_replica_database_url: str | None = None

    redis_url: str | None = None
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    secret_key: str = "some-secret-key-change-this"
    access_token_expire_minutes: int = 30

    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    log_level: str = "INFO"

    rate_limit_max_requests: int = 3
    rate_limit_window_seconds: int = 60

    min_bid_price: float = 0.01
    max_bid_price: float = 1.00
    no_bid_probability: float = 0.30

    bidder_min_latency_ms: int = 10
    bidder_max_latency_ms: int = 100

    def model_post_init(self, __context: Any) -> None:
        if not self.database_url:
            self.database_url = (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

        if not self.async_database_url:
            self.async_database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

        # Build read replica database URLs
        if not self.read_replica_database_url:
            self.read_replica_database_url = (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_read_replica_host}:{self.postgres_read_replica_port}/{self.postgres_db}"
            )

        if not self.async_read_replica_database_url:
            self.async_read_replica_database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_read_replica_host}:{self.postgres_read_replica_port}/{self.postgres_db}"
            )

        if not self.redis_url:
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origins_list(self) -> list[str]:
        """Returns CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Returns allowed hosts as a list."""
        return [host.strip() for host in self.allowed_hosts.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()
