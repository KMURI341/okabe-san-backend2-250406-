from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# 相対インポートに修正
from ...core.database import get_db
from ...api.auth.jwt import get_current_user
from ...api.users.models import User
from ...api.projects.models import Project
from .models import Trouble
from .schemas import (  # ここを修正
    TroubleCreate, 
    TroubleUpdate, 
    TroubleResponse, 
    TroubleDetailResponse,
    TroublesListResponse
)

router = APIRouter()

@router.post("/", response_model=TroubleResponse)
def create_trouble(
    trouble: TroubleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    新しいお困りごとを作成する
    """
    # プロジェクトの存在確認
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたプロジェクトが見つかりません"
        )
    
    # 新しいお困りごとを作成
    new_trouble = Trouble(
        title=trouble.title,
        description=trouble.description,
        category=trouble.category,
        project_id=trouble.project_id,
        author_id=current_user.id,
        status="open"
    )
    
    db.add(new_trouble)
    db.commit()
    db.refresh(new_trouble)
    
    return {
        "id": new_trouble.id,
        "title": new_trouble.title,
        "description": new_trouble.description,
        "category": new_trouble.category,
        "project_id": new_trouble.project_id,
        "project": project.title,
        "author_id": new_trouble.author_id,
        "author": current_user.name,
        "status": new_trouble.status,
        "created_at": new_trouble.created_at,
        "comments": 0  # 新規作成なのでコメントはゼロ
    }

@router.get("/", response_model=TroublesListResponse)
def get_troubles(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    お困りごとの一覧を取得する
    フィルターを適用可能：プロジェクトID、ステータス、カテゴリー
    """
    # クエリの作成
    query = db.query(Trouble)
    
    # フィルターの適用
    if project_id:
        query = query.filter(Trouble.project_id == project_id)
    if status:
        query = query.filter(Trouble.status == status)
    if category:
        query = query.filter(Trouble.category == category)
    
    # 総数の取得
    total = query.count()
    
    # ページネーション
    troubles = query.order_by(Trouble.created_at.desc()).offset(skip).limit(limit).all()
    
    # レスポンスの作成
    trouble_responses = []
    for trouble in troubles:
        # プロジェクト名の取得
        project = db.query(Project).filter(Project.id == trouble.project_id).first()
        # 作成者名の取得
        author = db.query(User).filter(User.id == trouble.author_id).first()
        # コメント数の取得（後でメッセージテーブルを使用）
        comments_count = 0  # TODO: メッセージテーブルからカウント
        
        trouble_responses.append({
            "id": trouble.id,
            "title": trouble.title,
            "description": trouble.description,
            "category": trouble.category,
            "project_id": trouble.project_id,
            "project": project.title if project else "Unknown",
            "author_id": trouble.author_id,
            "author": author.name if author else "Unknown",
            "status": trouble.status,
            "created_at": trouble.created_at,
            "comments": comments_count
        })
    
    return {
        "troubles": trouble_responses,
        "total": total
    }

@router.get("/{trouble_id}", response_model=TroubleDetailResponse)
def get_trouble_detail(
    trouble_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    特定のお困りごとの詳細を取得する
    """
    # お困りごとの取得
    trouble = db.query(Trouble).filter(Trouble.id == trouble_id).first()
    if not trouble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたお困りごとが見つかりません"
        )
    
    # プロジェクト名の取得
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    # 作成者名の取得
    author = db.query(User).filter(User.id == trouble.author_id).first()
    # コメント数の取得（後でメッセージテーブルを使用）
    comments_count = 0  # TODO: メッセージテーブルからカウント
    
    return {
        "id": trouble.id,
        "title": trouble.title,
        "description": trouble.description,
        "category": trouble.category,
        "project_id": trouble.project_id,
        "project": project.title if project else "Unknown",
        "author_id": trouble.author_id,
        "author": author.name if author else "Unknown",
        "status": trouble.status,
        "created_at": trouble.created_at,
        "comments": comments_count
    }

@router.put("/{trouble_id}", response_model=TroubleResponse)
def update_trouble(
    trouble_id: int,
    trouble_update: TroubleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    お困りごとを更新する
    """
    # お困りごとの取得
    trouble = db.query(Trouble).filter(Trouble.id == trouble_id).first()
    if not trouble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたお困りごとが見つかりません"
        )
    
    # 作成者または権限チェック（必要に応じて）
    if trouble.author_id != current_user.id:
        # ここではシンプルに作成者だけが編集できるようにする
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このお困りごとを編集する権限がありません"
        )
    
    # 更新が指定されたフィールドだけを更新
    if trouble_update.title is not None:
        trouble.title = trouble_update.title
    if trouble_update.description is not None:
        trouble.description = trouble_update.description
    if trouble_update.category is not None:
        trouble.category = trouble_update.category
    if trouble_update.status is not None:
        trouble.status = trouble_update.status
    
    db.commit()
    db.refresh(trouble)
    
    # プロジェクト名の取得
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    
    return {
        "id": trouble.id,
        "title": trouble.title,
        "description": trouble.description,
        "category": trouble.category,
        "project_id": trouble.project_id,
        "project": project.title if project else "Unknown",
        "author_id": trouble.author_id,
        "author": current_user.name,
        "status": trouble.status,
        "created_at": trouble.created_at,
        "comments": 0  # TODO: メッセージテーブルからカウント
    }

@router.get("/categories", response_model=List[str])
def get_trouble_categories():
    """
    利用可能なお困りごとカテゴリーの一覧を取得
    """
    # カテゴリーのリスト（後でデータベースから取得することも可能）
    categories = [
        "UI/UXデザイン",
        "コンテンツ制作",
        "モバイル開発", 
        "バックエンド開発",
        "インフラ",
        "セキュリティ",
        "テスト",
        "ドキュメント",
        "マーケティング",
        "その他"
    ]
    
    return categories