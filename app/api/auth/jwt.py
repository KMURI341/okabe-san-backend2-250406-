from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# 相対インポートに変更
from ...core.security import verify_password, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ...core.database import get_db
from ..users.models import User
from ..users.schemas import TokenData

# OAuth2のパスワードベアラースキーマを定義
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    ユーザー名とパスワードでユーザーを認証する
    
    :param db: データベースセッション
    :param username: ユーザー名
    :param password: パスワード
    :return: 認証されたユーザー、または認証失敗の場合はNone
    """
    user = db.query(User).filter(User.name == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    アクセストークンを生成する
    
    :param data: トークンに含めるデータ
    :param expires_delta: トークンの有効期限
    :return: JWTトークン
    """
    to_encode = data.copy()
    
    # 有効期限の設定
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # トークンをエンコード
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    現在のユーザーを取得する
    
    :param db: データベースセッション
    :param token: アクセストークン
    :return: 現在のユーザー
    :raises: 認証エラーの場合はHTTPException
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # トークンをデコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # ユーザーを取得
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user