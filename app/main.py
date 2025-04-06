from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# パスの追加（実行ディレクトリをモジュール検索パスに追加）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# APIルーターのインポート
from app.api.projects.router import router as projects_router
from app.api.users.router import router as users_router
from app.api.auth.router import router as auth_router
# 後でコメントアウトを外します
# from app.api.troubles.router import router as troubles_router
# from app.api.messages.router import router as messages_router

app = FastAPI(
    title="CollaboGames Backend API",
    description="コラボゲームズのバックエンドAPIサービス",
    version="0.1.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの追加
app.include_router(auth_router, prefix="/api/auth", tags=["認証"])
app.include_router(users_router, prefix="/api/users", tags=["ユーザー"])
app.include_router(projects_router, prefix="/api/projects", tags=["プロジェクト"])
# 後でコメントアウトを外します
# app.include_router(troubles_router, prefix="/api/troubles", tags=["お困りごと"])
# app.include_router(messages_router, prefix="/api/messages", tags=["メッセージ"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CollaboGames Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)