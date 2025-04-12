# app/api/troubles/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...models.base import Base

# 相対インポートに変更
from ...models.base import Base

class Trouble(Base):
    __tablename__ = "troubles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, index=True, nullable=False)
    # ここを "projects.id" から "co_creation_projects.project_id" に変更
    project_id = Column(Integer, ForeignKey("co_creation_projects.project_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    # Project モデルとの関連付け（Project モデルでは troubles リレーションシップを back_populates で定義している前提）
    project = relationship("Project", back_populates="troubles")
    author = relationship("User", back_populates="troubles")
    # メッセージのリレーションシップ（Message モデルがある前提）
    messages = relationship("Message", back_populates="trouble")
