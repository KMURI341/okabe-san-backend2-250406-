# app/api/auth/router.py
from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .jwt import authenticate_user, create_access_token
from ..users.models import User
from ..users.schemas import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    ユーザー名とパスワードでログイン
    """
    print(f"ログインリクエスト受信: username={form_data.username}")
    
    # Azure DB からユーザーを認証
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        print(f"認証失敗: ユーザー '{form_data.username}' の認証に失敗しました")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが無効です",
        )
    
    print(f"認証成功: ユーザー '{form_data.username}' (ID: {user.user_id})")
    
    # 最終ログイン時間を更新
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # アクセストークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_name": user.name
    }

@router.post("/register", response_model=Token)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    新規ユーザー登録
    """
    # パスワード確認
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスワードが一致しません",
        )
    
    # Azure DB でユーザー名の重複チェック
    existing_user = db.query(User).filter(User.name == user_data.name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています",
        )
    
    now = datetime.utcnow()
    
    # 新しいユーザーを作成して Azure DB に保存
    user = User(
        name=user_data.name,
        password=get_password_hash(user_data.password),
        categories=",".join(user_data.categories) if user_data.categories else "",
        point_total=0,
        last_login_at=datetime.utcnow()
    )
    
    # カテゴリーがあれば設定
    if hasattr(user, 'categories') and user_data.categories:
        user.set_categories_list(user_data.categories)
    
    # データベースに保存
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # アクセストークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_name": user.name
    }