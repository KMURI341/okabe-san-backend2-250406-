from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from sqlalchemy import text

from app.core.database import get_db
from app.api.projects.models import Project, UserFavoriteProject
from app.api.projects.schemas import (
    ProjectResponse, 
    ProjectListResponse, 
    ProjectCreate, 
    ProjectCategoryResponse,
    RankingUser
)
from app.api.users.models import User  # プロジェクトの作者情報等を取得する前提

router = APIRouter()

def convert_project(project: Project, db: Session, user_id: int) -> ProjectResponse:
    """
    プロジェクトモデルからProjectResponseに変換する補助関数です。
    - いいね数やコメント数はダミーで設定しています。
    - お気に入り情報と作者名は直接SQLで取得しています。
    """
    likes = 24  
    comments = 8  
    
    is_favorite = False
    try:
        favorite_result = db.execute(
            text("SELECT 1 FROM user_project_favorites WHERE user_id = :user_id AND project_id = :project_id"),
            {"user_id": user_id, "project_id": project.project_id}
        ).fetchone()
        is_favorite = favorite_result is not None
    except Exception as e:
        print(f"お気に入り情報の取得エラー: {e}")
    
    author_name = "Unknown"
    try:
        author_result = db.execute(
            text("SELECT name FROM users WHERE user_id = :user_id"),
            {"user_id": project.creator_user_id}
        ).fetchone()
        if author_result:
            author_name = author_result[0]
    except Exception as e:
        print(f"作者名の取得エラー: {e}")
    
    return ProjectResponse(
        id=project.project_id,
        title=project.title,
        description=project.description,
        category=project.summary or "",
        author_id=project.creator_user_id,
        author=author_name,
        created_at=project.created_at,
        likes=likes,
        comments=comments,
        is_favorite=is_favorite
    )

# ユーザーIDを元に、新着プロジェクト・お気に入りプロジェクト一覧を返すエンドポイント
@router.get("/", response_model=ProjectListResponse)
def get_projects(user_id: int, db: Session = Depends(get_db)):
    # 新着プロジェクトを取得
    new_projects = (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )

    # お気に入りプロジェクトを直接SQLで取得
    favorite_projects_query = """
    SELECT p.* FROM co_creation_projects p
    JOIN user_project_favorites f ON p.project_id = f.project_id
    WHERE f.user_id = :user_id
    ORDER BY p.created_at DESC
    LIMIT 8
    """
    favorite_projects = []
    try:
        result = db.execute(text(favorite_projects_query), {"user_id": user_id})
        # SQLAlchemyの場合、result.all()はRow型のリストになるので、Projectインスタンスに
        # 自動的に変換されていない可能性があります。
        # ここではシンプルに各行からIDなどを使って変換するか、
        # ORM経由で再度取得する方法も考えられますが、ここでは仮の実装とします。
        favorite_projects = [row for row in result.all()]
    except Exception as e:
        print(f"お気に入りプロジェクト取得エラー: {e}")

    total_projects = db.query(Project).count()

    return ProjectListResponse(
        new_projects=[convert_project(p, db, user_id) for p in new_projects],
        favorite_projects=[convert_project(p, db, user_id) for p in favorite_projects],
        total_projects=total_projects
    )

# プロジェクトIDを指定して、個別プロジェクトの詳細を返すエンドポイント
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # プロジェクト詳細取得ではユーザーコンテキストが無い場合は、いいねなどはダミー値やfalseに設定
    return ProjectResponse(
        id=project.project_id,
        title=project.title,
        description=project.description,
        category=project.summary or "",
        author_id=project.creator_user_id,
        author="Unknown",  # 作者名取得のために必要なら、上記convert_projectと同様にSQLで取得するか、リレーションを利用
        created_at=project.created_at,
        likes=0,
        comments=0,
        is_favorite=False
    )

@router.get("/categories", response_model=ProjectCategoryResponse)
def get_project_categories(db: Session = Depends(get_db)):
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
    ranking_data = [
        RankingUser(name="キツネ", points=1250, rank=1),
        RankingUser(name="パンダ", points=980, rank=2),
        RankingUser(name="ウサギ", points=875, rank=3)
    ]
    return ranking_data

@router.post("/create")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    if not project.title or not project.description or not project.category:
        raise HTTPException(status_code=400, detail="全ての項目を入力してください")
    # プロジェクト作成処理（例）
    new_project = Project(
        title=project.title,
        description=project.description,
        summary=project.category,
        creator_user_id=project.author_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": "Project created successfully", "project_id": new_project.project_id}