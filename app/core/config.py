# app/core/config.py
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings(BaseSettings):
    # プロジェクト設定
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "CollaboGames")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Azure MySQL設定
    AZURE_MYSQL_HOST: str = os.getenv("AZURE_MYSQL_HOST", "")
    AZURE_MYSQL_USER: str = os.getenv("AZURE_MYSQL_USER", "")
    AZURE_MYSQL_PASSWORD: str = os.getenv("AZURE_MYSQL_PASSWORD", "")
    AZURE_MYSQL_DATABASE: str = os.getenv("AZURE_MYSQL_DATABASE", "")
    AZURE_MYSQL_PORT: str = os.getenv("AZURE_MYSQL_PORT", "3306")
    AZURE_MYSQL_SSL_MODE: str = os.getenv("AZURE_MYSQL_SSL_MODE", "")
    USE_AZURE: bool = os.getenv("USE_AZURE", "False").lower() == "true"
    
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback_secret_key_please_change_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # CORS設定
    ALLOWED_HOSTS: list = ["*"]

    # データベースURLを動的に生成
    @property
    def get_database_url(self) -> str:
        """データベース接続URLを取得"""
        if self.USE_AZURE:
            # Azure MySQL用の接続URL（SSLはURLではなく connect_args で設定する）
            return f"mysql+pymysql://{self.AZURE_MYSQL_USER}:{self.AZURE_MYSQL_PASSWORD}@{self.AZURE_MYSQL_HOST}:{self.AZURE_MYSQL_PORT}/{self.AZURE_MYSQL_DATABASE}"
        else:
            # ローカルデータベース接続URL
            return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 環境変数からの自動読み込みを許可
        extra = "ignore"  # 追加の変数を無視

# グローバル設定インスタンスの作成
settings = Settings()