"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/workout_app"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    frontend_origin: str = "http://localhost:5173"
    default_plan_weeks: int = 12

    # Observability + safety limits
    log_level: str = "INFO"
    max_upload_mb: int = 10


settings = Settings()
