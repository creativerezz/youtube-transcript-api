"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Redis configuration
    redis_url: Optional[str] = None
    cache_ttl_seconds: int = 3600

    # Webshare proxy configuration
    webshare_proxy_username: Optional[str] = None
    webshare_proxy_password: Optional[str] = None

    # Anthropic API configuration
    anthropic_api_key: Optional[str] = None

    # Logging configuration
    log_level: str = "INFO"
    json_logs: bool = False

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    @property
    def has_proxy_config(self) -> bool:
        """Check if proxy configuration is available."""
        return bool(self.webshare_proxy_username and self.webshare_proxy_password)

    @property
    def has_anthropic_config(self) -> bool:
        """Check if Anthropic API is configured."""
        return bool(self.anthropic_api_key)

    @property
    def has_redis_config(self) -> bool:
        """Check if Redis is configured."""
        return bool(self.redis_url)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance (cached after first call)
    """
    return Settings()
