<<<<<<< HEAD
from pydantic import BaseSettings  # pydantic_settingsではなくpydantic
=======
from pydantic_settings import BaseSettings
>>>>>>> ff13e650aa280a9bae6aba74e2d684947458f107
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings(BaseSettings):
    # プロジェクト設定
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "CollaboGames")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

<<<<<<< HEAD
    # Azure MySQL設定
    AZURE_MYSQL_HOST: str = os.getenv("AZURE_MYSQL_HOST", "")
    AZURE_MYSQL_USER: str = os.getenv("AZURE_MYSQL_USER", "")
    AZURE_MYSQL_PASSWORD: str = os.getenv("AZURE_MYSQL_PASSWORD", "")
    AZURE_MYSQL_DATABASE: str = os.getenv("AZURE_MYSQL_DATABASE", "")
    AZURE_MYSQL_PORT: str = os.getenv("AZURE_MYSQL_PORT", "3306")
    AZURE_MYSQL_SSL_MODE: str = os.getenv("AZURE_MYSQL_SSL_MODE", "")

    # データベース設定
    # 環境に基づいてデータベースURLを選択
    @property
    def DATABASE_URL(self) -> str:
        azure_url = self.get_azure_database_url()
        local_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        
        # 環境変数USE_AZUREがTrueの場合、Azureデータベースを使用
        use_azure = os.getenv("USE_AZURE", "False").lower() == "true"
        return azure_url if use_azure else local_url

    def get_azure_database_url(self) -> str:
        """Azure MySQL用の接続URLを生成"""
        ssl_args = ""
        # SSLモードがrequireの場合、URLパラメータとして追加
        if self.AZURE_MYSQL_SSL_MODE == "require":
            ssl_args = "?ssl_mode=REQUIRED"
        
        return f"mysql+pymysql://{self.AZURE_MYSQL_USER}:{self.AZURE_MYSQL_PASSWORD}@{self.AZURE_MYSQL_HOST}:{self.AZURE_MYSQL_PORT}/{self.AZURE_MYSQL_DATABASE}{ssl_args}"
=======
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
>>>>>>> ff13e650aa280a9bae6aba74e2d684947458f107

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