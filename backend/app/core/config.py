from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import os


class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    url: str
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600


class RedisSettings(BaseModel):
    """Redis configuration settings."""
    url: str
    max_connections: int = 20


class AuthSettings(BaseModel):
    """Authentication configuration settings."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


class APISettings(BaseModel):
    """External API configuration settings."""
    world_bank_base_url: str = "https://api.worldbank.org/v2"
    imf_base_url: str = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
    fred_api_key: Optional[str] = None
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    un_comtrade_base_url: str = "https://comtradeapi.un.org/data/v1/get"
    sipri_base_url: str = "https://www.sipri.org/databases"
    gdelt_base_url: str = "https://api.gdeltproject.org/api/v2"
    google_trends_api_key: Optional[str] = None
    bis_base_url: str = "https://www.bis.org/statistics"
    oecd_base_url: str = "https://stats.oecd.org/restsdmx/sdmx.ashx"
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.3


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "SlashRun Simulation API"
    debug: bool = False
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    
    # Redis (optional, for caching)
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Authentication
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(60 * 24 * 7, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External APIs
    fred_api_key: Optional[str] = Field(None, env="FRED_API_KEY")
    google_trends_api_key: Optional[str] = Field(None, env="GOOGLE_TRENDS_API_KEY")
    
    # CORS
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow"  # Allow extra fields from .env
    }
    
    @property
    def database_settings(self) -> DatabaseSettings:
        """Get database settings."""
        return DatabaseSettings(
            url=self.database_url,
            echo=self.database_echo
        )
    
    @property
    def redis_settings(self) -> RedisSettings:
        """Get Redis settings."""
        return RedisSettings(url=self.redis_url)
    
    @property
    def auth_settings(self) -> AuthSettings:
        """Get authentication settings."""
        return AuthSettings(
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes
        )
    
    @property
    def api_settings(self) -> APISettings:
        """Get external API settings."""
        return APISettings(
            fred_api_key=self.fred_api_key,
            google_trends_api_key=self.google_trends_api_key
        )


# Global settings instance
settings = Settings()
