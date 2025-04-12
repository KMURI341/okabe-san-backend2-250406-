from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from app.core.database import get_db
from app.api.projects.models import Project, UserFavoriteProject
from app.api.projects.schemas import (
    ProjectResponse, 
    ProjectListResponse, 
    ProjectCreate, 
    ProjectCategoryResponse,
    RankingUser
)
from app.api.users.models import User  # User モデル側も、creator_user_id / projects 関係を持つ前提

router = APIRouter()

@router.get("/", response_model=ProjectListResponse)
def get_projects(user_id: int, db: Session = Depends(get_db)):
    # 新着プロジェクトを取得（co_creation_projects テーブルから）
    new_projects = (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )

    # お気に入りプロジェクト：UserFavoriteProject を JOIN してフィルター
    favorite_projects = (
        db.query(Project)
        .join(UserFavoriteProject)
        .filter(UserFavoriteProject.user_id == user_id)
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )

    # プロジェクト総数を取得
    total_projects = db.query(Project).count()

    # プロジェクトをレスポンス用に変換するローカル関数
    def convert_project(project: Project) -> ProjectResponse:
        likes = 24  # ダミーのいいね数（後ほど実際のロジックに置き換える）
        comments = 8  # ダミーのコメント数（後ほど実際のロジックに置き換える）
        is_favorite = (
            db.query(UserFavoriteProject)
            .filter(
                UserFavoriteProject.user_id == user_id,
                UserFavoriteProject.project_id == project.project_id
            )
            .first() is not None
        )

        return ProjectResponse(
            id=project.project_id,            # models.py で定義した project_id を使用
            title=project.title,
            description=project.description,
            # ここでは summary を category として返す例です（必要に応じて調整してください）
            category=project.summary if project.summary else "",
            author_id=project.creator_user_id,  # models.py で定義した creator_user_id を使用
            author=project.creator.name,         # リレーション名は creator として定義
            created_at=project.created_at,
            likes=likes,
            comments=comments,
            is_favorite=is_favorite
        )

    return ProjectListResponse(
        new_projects=[convert_project(p) for p in new_projects],
        favorite_projects=[convert_project(p) for p in favorite_projects],
        total_projects=total_projects
    )

@router.get("/categories", response_model=ProjectCategoryResponse)
def get_project_categories(db: Session = Depends(get_db)):
    # プロジェクトカテゴリー一覧（固定値）
    categories = [
        "テクノロジー", 
        "デザイン", 
        "マーケティング", 
        "ビジネス", 
        "教育", 
        "コミュニティ", 
        "医療", 
        "環境"
    ]
    return ProjectCategoryResponse(categories=categories)

@router.get("/ranking", response_model=List[RankingUser])
def get_activity_ranking(db: Session = Depends(get_db)):
    # ダミーデータ
    ranking_data = [
        RankingUser(name="キツネ", points=1250, rank=1),
        RankingUser(name="パンダ", points=980, rank=2),
        RankingUser(name="ウサギ", points=875, rank=3)
    ]
    return ranking_data

@router.post("/create")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # 必要項目のバリデーション
    if not project.title or not project.description or not project.category:
        raise HTTPException(status_code=400, detail="全ての項目を入力してください")
