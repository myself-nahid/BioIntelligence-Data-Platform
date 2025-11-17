from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    # Database Credentials
    POSTGRES_HOST: str = "db"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Other Services
    REDIS_URL: str

    # API Keys & Webhooks
    SLACK_WEBHOOK_URL: str
    PUBMED_API_KEY: str | None = None

    # This is a Pydantic v2 feature to create a computed property.
    # It will automatically build the DATABASE_URL from the other fields.
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        )

    class Config:
        # This tells Pydantic to look for variables in a file named .env
        env_file = ".env"
        # This allows the case to match (e.g., POSTGRES_USER in .env maps to postgres_user in code)
        case_sensitive = True

settings = Settings()