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
from app.api.users.models import User

router = APIRouter()

@router.get("/", response_model=ProjectListResponse)
def get_projects(
    user_id: int, 
    db: Session = Depends(get_db)
):
    # 新着プロジェクト
    new_projects = (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )

    # お気に入りプロジェクト
    favorite_projects = (
        db.query(Project)
        .join(UserFavoriteProject)
        .filter(UserFavoriteProject.user_id == user_id)
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )

    # プロジェクト総数
    total_projects = db.query(Project).count()

    # プロジェクトをレスポンススキーマに変換
    def convert_project(project):
        # ダミーのいいね数とコメント数
        likes = 24  # TODO: 実際のロジックに置き換える
        comments = 8  # TODO: 実際のロジックに置き換える
        
        # お気に入り判定
        is_favorite = db.query(UserFavoriteProject).filter(
            UserFavoriteProject.user_id == user_id,
            UserFavoriteProject.project_id == project.id
        ).first() is not None

        return ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            category=project.category,
            author_id=project.author_id,
            author=project.author.name,  # ユーザー名を取得
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
    # プロジェクトカテゴリーの一覧を取得
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
    # TODO: 実際のポイント計算ロジックに置き換える
    # 現時点では、ダミーデータを返す
    ranking_data = [
        RankingUser(name="キツネ", points=1250, rank=1),
        RankingUser(name="パンダ", points=980, rank=2),
        RankingUser(name="ウサギ", points=875, rank=3)
    ]
    return ranking_data

@router.post("/create")
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db)
):
    # プロジェクト作成のバリデーションを追加
    if not project.title or not project.description or not project.category:
        raise HTTPException(status_code=400, detail="全ての項目を入力してください")

    # プロジェクトを作成
    new_project = Project(
        title=project.title,
        description=project.description,
        category=project.category,
        author_id=project.author_id
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {"message": "プロジェクトを登録しました", "project_id": new_project.id}