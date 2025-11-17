from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SLACK_WEBHOOK_URL: str
    PUBMED_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()