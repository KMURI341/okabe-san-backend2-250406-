from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# 相対インポートに変更
from ...models.base import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # hashed_password から変更
    category_id = Column(Integer)
    num_answer = Column(Integer)
    point_total = Column(Integer)  # points ではなく point_total を使用
    # points カラムを削除
    last_login_at = Column(DateTime, nullable=False)  # 足りないカラム
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    projects = relationship("Project", back_populates="creator", foreign_keys="Project.creator_user_id")
    favorite_projects = relationship("UserFavoriteProject", back_populates="user", foreign_keys="UserFavoriteProject.user_id")
    messages = relationship("Message", back_populates="user")
    troubles = relationship("Trouble", back_populates="author")
    
    # points の代わりに point_total を使用するように修正
    def get_points(self):
        return self.point_total or 0
    
    def get_categories_list(self):
        """カテゴリー文字列をリストに変換"""
        if not hasattr(self, 'categories') or not self.categories:
            return []
        return [cat.strip() for cat in self.categories.split(",")]
    
    def set_categories_list(self, categories_list):
        """カテゴリーリストを文字列に変換"""
        if not hasattr(self, 'categories'):
            return  # categories 属性がない場合は何もしない
        
        if not categories_list:
            self.categories = ""
        else:
            self.categories = ",".join(categories_list)