from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings(BaseSettings):
    # プロジェクト設定
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "CollaboGames")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback_secret_key_please_change_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # CORS設定
    ALLOWED_HOSTS: list = ["*"]

    class Config:
        # 環境変数の.envファイルからの読み込みを許可
        env_file = ".env"
        env_file_encoding = "utf-8"

# グローバル設定インスタンスの作成
settings = Settings()