from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...models.base import Base

class Project(Base):
    __tablename__ = "co_creation_projects"

    project_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    summary = Column(String(1000), nullable=True)
    description = Column(Text, nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # users.id から users.user_id に変更
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="projects")
    troubles = relationship("Trouble", back_populates="project")
    user_favorites = relationship("UserFavoriteProject", back_populates="project")
    
class UserFavoriteProject(Base):
    __tablename__ = "user_project_favorites"  # テーブル名を修正

    # 複合キーの定義
    # id = Column(Integer, primary_key=True, index=True)  # この行を削除
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)  # users.id から users.user_id に変更
    project_id = Column(Integer, ForeignKey("co_creation_projects.project_id"), primary_key=True)

    user = relationship("User", back_populates="favorite_projects")
    project = relationship("Project", back_populates="user_favorites")
