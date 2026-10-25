from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lightweight ERP"
    SECRET_KEY: str = "changeme_in_production_1234567890" # Needs to be safe length for production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = "sqlite:///./erp.db"
    DEMO_MODE: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
