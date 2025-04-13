from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# 相対インポートに変更
from ...models.base import Base
from ..users.models import User  # Userクラスをインポート

class Trouble(Base):
    __tablename__ = "troubles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("co_creation_projects.project_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # users.idからusers.user_idに修正
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    project = relationship("Project", back_populates="troubles")
    author = relationship("User", back_populates="troubles")
    messages = relationship("Message", back_populates="trouble")
