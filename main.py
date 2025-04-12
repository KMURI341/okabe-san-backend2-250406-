from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ───────── 全モデルを明示的にインポート ─────────
# これにより、各モデルが Base.metadata に登録され、create_all() でテーブルが生成されます
from app.api.projects import models as project_models
from app.api.users import models as user_models
from app.api.troubles import models as trouble_models
from app.api.messages import models as message_models  # メッセージ関連があれば

# ───────── ルーターのインポート ─────────
try:
    from app.api.projects.router import router as projects_router
    from app.api.users.router import router as users_router
    from app.api.auth.router import router as auth_router
    from app.api.troubles.router import router as troubles_router
    from app.api.messages.router import router as messages_router
except ImportError as e:
    print(f"インポートエラー: {e}")
    print(f"現在のパス: {sys.path}")
    raise

# ───────── データベース関連のインポート ─────────
from app.core.database import engine, Base

app = FastAPI(
    title="CollaboGames Backend API",
    description="コラボゲームズのバックエンドAPIサービス",
    version="0.1.0"
)

# ───────── CORSミドルウェアの設定 ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────── Startup イベント：テーブル自動生成 ─────────
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# ───────── 各種ルーターの追加 ─────────
app.include_router(auth_router, prefix="/api/auth", tags=["認証"])
app.include_router(users_router, prefix="/api/users", tags=["ユーザー"])
app.include_router(projects_router, prefix="/api/projects", tags=["プロジェクト"])
app.include_router(troubles_router, prefix="/api/troubles", tags=["お困りごと"])
app.include_router(messages_router, prefix="/api/messages", tags=["メッセージ"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CollaboGames Backend API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
