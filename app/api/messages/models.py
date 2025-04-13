# app/api/messages/models.py を以下のように修正
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...models.base import Base
from ..users.models import User  # User クラスをインポート

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    # users.id を users.user_id に修正
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # troubles.id が正しい参照先
    trouble_id = Column(Integer, ForeignKey("troubles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    user = relationship("User", back_populates="messages")
    trouble = relationship("Trouble", back_populates="messages")