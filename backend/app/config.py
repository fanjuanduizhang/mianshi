import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Hunter"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL: str = os.getenv(
        "DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions"
    )
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", "./data/chromadb")
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "./data/uploads")
    QUESTION_BANK_PATH: str = os.getenv(
        "QUESTION_BANK_PATH", "./data/question_bank"
    )

    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    )

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()

os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(settings.QUESTION_BANK_PATH, exist_ok=True)
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
