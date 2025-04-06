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

from . import schemas

router = APIRouter()

@router.post("/", response_model=schemas.TroubleResponse)
def create_trouble(
    trouble: schemas.TroubleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # プロジェクトが存在するか確認
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")
    
    # お困りごと作成
    new_trouble = Trouble(
        title=trouble.title,
        description=trouble.description,
        category=trouble.category,
        project_id=trouble.project_id,
        author_id=current_user.id
    )
    
    db.add(new_trouble)
    db.commit()
    db.refresh(new_trouble)
    
    return schemas.TroubleResponse(
        id=new_trouble.id,
        title=new_trouble.title,
        description=new_trouble.description,
        category=new_trouble.category,
        project_id=new_trouble.project_id,
        project_title=project.title,
        author_id=new_trouble.author_id,
        author=current_user.name,
        created_at=new_trouble.created_at,
        comments=0  # 新規作成時はコメント数0
    )

@router.get("/", response_model=schemas.TroublesListResponse)
def get_troubles(
    project_id: int = Query(None, description="特定のプロジェクトのお困りごとを取得"),
    category: Optional[str] = Query(None, description="カテゴリでフィルタリング"),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # クエリ作成
    query = db.query(Trouble)
    
    # プロジェクトIDによるフィルタリング
    if project_id:
        query = query.filter(Trouble.project_id == project_id)
    
    # カテゴリによるフィルタリング
    if category:
        query = query.filter(Trouble.category == category)
    
    # 作成日時で降順ソート
    query = query.order_by(Trouble.created_at.desc())
    
    # 総数取得
    total = query.count()
    
    # ページネーション適用
    troubles = query.offset(skip).limit(limit).all()
    
    # レスポンス形式に変換
    trouble_list = []
    for trouble in troubles:
        # プロジェクト情報取得
        project = db.query(Project).filter(Project.id == trouble.project_id).first()
        
        # 作成者情報取得
        author = db.query(User).filter(User.id == trouble.author_id).first()
        
        # コメント数取得（メッセージとして扱う）
        # Note: Message モデルが実装されていることを前提とする
        # comments_count = db.query(Message).filter(Message.trouble_id == trouble.id).count()
        comments_count = 0  # 仮実装
        
        trouble_list.append(schemas.TroubleResponse(
            id=trouble.id,
            title=trouble.title,
            description=trouble.description,
            category=trouble.category,
            project_id=trouble.project_id,
            project_title=project.title if project else "Unknown Project",
            author_id=trouble.author_id,
            author=author.name if author else "Unknown User",
            created_at=trouble.created_at,
            comments=comments_count
        ))
    
    return schemas.TroublesListResponse(
        troubles=trouble_list,
        total=total
    )

@router.get("/{trouble_id}", response_model=schemas.TroubleDetailResponse)
def get_trouble_detail(
    trouble_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # お困りごと取得
    trouble = db.query(Trouble).filter(Trouble.id == trouble_id).first()
    if not trouble:
        raise HTTPException(status_code=404, detail="お困りごとが見つかりません")
    
    # プロジェクト情報取得
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    
    # 作成者情報取得
    author = db.query(User).filter(User.id == trouble.author_id).first()
    
    # コメント数取得（メッセージとして扱う）
    # comments_count = db.query(Message).filter(Message.trouble_id == trouble.id).count()
    comments_count = 0  # 仮実装
    
    return schemas.TroubleDetailResponse(
        id=trouble.id,
        title=trouble.title,
        description=trouble.description,
        category=trouble.category,
        project_id=trouble.project_id,
        project_title=project.title if project else "Unknown Project",
        author_id=trouble.author_id,
        author=author.name if author else "Unknown User",
        created_at=trouble.created_at,
        comments=comments_count,
        # メッセージ機能が実装されていることを前提とする
        # messages=[]  # 必要に応じてメッセージ一覧を取得
    )

@router.put("/{trouble_id}", response_model=schemas.TroubleResponse)
def update_trouble(
    trouble_id: int,
    trouble_update: schemas.TroubleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # お困りごと取得
    trouble = db.query(Trouble).filter(Trouble.id == trouble_id).first()
    if not trouble:
        raise HTTPException(status_code=404, detail="お困りごとが見つかりません")
    
    # 作成者のみ更新可能
    if trouble.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="自分のお困りごとのみ更新できます")
    
    # 更新
    trouble.title = trouble_update.title
    trouble.description = trouble_update.description
    trouble.category = trouble_update.category
    
    db.commit()
    db.refresh(trouble)
    
    # プロジェクト情報取得
    project = db.query(Project).filter(Project.id == trouble.project_id).first()
    
    return schemas.TroubleResponse(
        id=trouble.id,
        title=trouble.title,
        description=trouble.description,
        category=trouble.category,
        project_id=trouble.project_id,
        project_title=project.title if project else "Unknown Project",
        author_id=trouble.author_id,
        author=current_user.name,
        created_at=trouble.created_at,
        comments=0  # 仮実装
    )

@router.delete("/{trouble_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trouble(
    trouble_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # お困りごと取得
    trouble = db.query(Trouble).filter(Trouble.id == trouble_id).first()
    if not trouble:
        raise HTTPException(status_code=404, detail="お困りごとが見つかりません")
    
    # 作成者のみ削除可能
    if trouble.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="自分のお困りごとのみ削除できます")
    
    # 削除
    db.delete(trouble)
    db.commit()
    
    return None

@router.get("/categories", response_model=List[str])
def get_trouble_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # お困りごとのカテゴリー一覧を取得（重複を排除）
    categories = db.query(Trouble.category).distinct().all()
    
    # 結果を文字列のリストに変換
    category_list = [cat[0] for cat in categories]
    
    # もしカテゴリーがなければデフォルトのカテゴリーを返す
    if not category_list:
        category_list = ["UI/UXデザイン", "コンテンツ制作", "モバイル開発", "技術相談", "マーケティング"]
    
    return category_list