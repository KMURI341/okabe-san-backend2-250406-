from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# 相対インポートに変更
from ...models.base import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    # hashed_password = Column(String, nullable=False)  # 古い定義
    password = Column(String, nullable=False)  # データベース上の実際のカラム名に修正
    category_id = Column(Integer)  # usersテーブルには category_id がある可能性
    # categories = Column(String)  # 実際のデータベースにはないかもしれない
    num_answer = Column(Integer)  # これも必要かもしれない
    point_total = Column(Integer)  # これも必要かもしれない
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    projects = relationship("Project", back_populates="creator", foreign_keys="Project.creator_user_id")
    
    favorite_projects = relationship("UserFavoriteProject", 
                                   back_populates="user", 
                                   foreign_keys="UserFavoriteProject.user_id")
    messages = relationship("Message", back_populates="user")
    troubles = relationship("Trouble", back_populates="author")
    
    # メソッド
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
