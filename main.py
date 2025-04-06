from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# APIルーターのインポート（後で追加）
# from app.api.projects.router import router as projects_router
# from app.api.users.router import router as users_router

app = FastAPI(
    title="CollaboGames Backend API",
    description="コラボゲームズのバックエンドAPIサービス",
    version="0.1.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントエンドのオリジンに置き換えてください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの追加（後で有効化）
# app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
# app.include_router(users_router, prefix="/api/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CollaboGames Backend API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
