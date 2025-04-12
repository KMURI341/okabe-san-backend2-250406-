from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
import sys
from typing import Dict, Any

# 環境変数の読み込み
load_dotenv()

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_parent_dir)

# ここで直接インポート
from app.core.config import settings

# データベース接続設定
def get_db_connect_args() -> Dict[str, Any]:
    """データベース接続引数を取得"""
    connect_args = {}
    
    # SQLiteの場合の特別な設定
    if "sqlite" in settings.DATABASE_URL:
        connect_args["check_same_thread"] = False
    
    # Azure MySQLの場合のSSL設定
    if os.getenv("USE_AZURE", "False").lower() == "true":
        ssl_mode = os.getenv("AZURE_MYSQL_SSL_MODE", "")
        if ssl_mode == "require":
            connect_args["ssl_mode"] = "REQUIRED"
    
    return connect_args

# エンジンの作成
database_url = settings.DATABASE_URL
engine = create_engine(
    database_url,
    connect_args=get_db_connect_args(),
    pool_pre_ping=True,  # 接続が生きているか確認
    poolclass=NullPool  # 各リクエスト間でコネクションを再利用しない
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラスの作成
Base = declarative_base()

# データベースセッションの依存性注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()