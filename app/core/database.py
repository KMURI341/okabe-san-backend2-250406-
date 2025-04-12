from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
import sys
from typing import Dict, Any

# 環境変数の読み込み
load_dotenv()

# パスを正しく設定
current_dir = os.path.dirname(os.path.abspath(__file__))  # core ディレクトリ
app_dir = os.path.dirname(current_dir)  # app ディレクトリ
project_root = os.path.dirname(app_dir)  # プロジェクトルート

# もしまだPythonパスに含まれていなければ追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 同じディレクトリからのインポート
try:
    from app.core.config import settings
except ImportError:
    # 最後の手段として、直接インポート
    try:
        from .config import settings
    except ImportError as e:
        print(f"設定のインポートエラー: {e}")
        print(f"現在のパス: {sys.path}")
        
        # config.pyへの直接パスを作成
        config_path = os.path.join(current_dir, "config.py")
        if os.path.exists(config_path):
            print(f"config.pyが存在します: {config_path}")
        else:
            print(f"config.pyが見つかりません: {config_path}")
        
        raise

# データベース接続設定
def get_db_connect_args() -> Dict[str, Any]:
    """データベース接続引数を取得"""
    connect_args = {}
    
    # Azure MySQLの場合のSSL設定
    if settings.USE_AZURE:
        ssl_mode = settings.AZURE_MYSQL_SSL_MODE.lower()
        if ssl_mode == "require":
            # SSL 証明書のパスを指定（Windows 環境の場合は raw 文字列またはバックスラッシュをエスケープ）
            connect_args["ssl"] = {
                "ssl_ca": r"C:\Users\mmkji\.ssl\DigiCertGlobalRootCA.crt.pem"
            }
    
    return connect_args

# エンジンの作成
try:
    # settings.get_database_url プロパティを使って、Azure MySQL用の接続URLを取得
    database_url = settings.get_database_url
    engine = create_engine(
        database_url,
        connect_args=get_db_connect_args(),
        pool_pre_ping=True,  # 接続が生きているか確認
        poolclass=NullPool     # 各リクエスト間でコネクションを再利用しない
    )

    # セッションファクトリーの作成
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # ベースクラスの作成
    Base = declarative_base()
except Exception as e:
    print(f"データベース設定中にエラーが発生しました: {e}")
    raise

# データベースセッションの依存性注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
