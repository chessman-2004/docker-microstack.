from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Microstack Enterprise API"
    ENVIRONMENT: str = Field(default="production")
    
    # Security
    API_KEY_NAME: str = "X-API-Key"
    API_KEY: str = Field(default="microstack-dev-secret-key-change-in-prod")
    
    # Infrastructure
    DATABASE_URL: str = Field(default="postgresql://postgres:postgrespassword@db:5432/microservices_db")
    CELERY_BROKER_URL: str = Field(default="redis://cache:6379/0")
    PDF_STORAGE_DIR: str = Field(default="/app/generated_pdfs")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()