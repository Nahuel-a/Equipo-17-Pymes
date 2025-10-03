from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database settings
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str

    # Security settings
    CORS_DOMAINS: str
    SECRET_KEY: str = "your_default_secret_key"
    ALGORITHM: str = "HS256"
    EXPIRE_TOKEN: int = 30  # in minutes

    class Config:
        env_file = "../.env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()