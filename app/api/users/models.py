from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# 相対インポートに変更
from ...models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    categories = Column(String)
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ - 文字列で参照する
    projects = relationship("Project", back_populates="author")
    favorite_projects = relationship("UserFavoriteProject", back_populates="user")
    messages = relationship("Message", back_populates="user")
    
    def get_categories_list(self):
        """カテゴリー文字列をリストに変換"""
        if not self.categories:
            return []
        return [cat.strip() for cat in self.categories.split(",")]
    
    def set_categories_list(self, categories_list):
        """カテゴリーリストを文字列に変換"""
        if not categories_list:
            self.categories = ""
        else:
            self.categories = ",".join(categories_list)