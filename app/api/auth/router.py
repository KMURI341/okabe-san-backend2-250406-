from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# 相対インポートに変更
from ...core.database import get_db
from ...core.security import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .jwt import authenticate_user, create_access_token
from ..users.models import User
from ..users.schemas import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2互換のトークンログインエンドポイント
    """
    # ユーザーを認証
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name
    }

@router.post("/login", response_model=Token)
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    ユーザー名とパスワードでログイン
    """
    # ユーザーを認証
    user = authenticate_user(db, username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが無効です",
        )
    
    # アクセストークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
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
    
    # ユーザー名の重複チェック
    existing_user = db.query(User).filter(User.name == user_data.name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています",
        )
    
    # 新しいユーザーを作成
    user = User(
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
    )
    
    # カテゴリーがあれば設定
    if user_data.categories:
        user.set_categories_list(user_data.categories)
    
    # データベースに保存
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # アクセストークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name
    }