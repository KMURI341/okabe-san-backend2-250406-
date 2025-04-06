from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class TroubleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="お困りごとのタイトル")
    description: str = Field(..., min_length=10, max_length=1000, description="お困りごとの詳細説明")
    category: str = Field(..., description="お困りごとのカテゴリー")

class TroubleCreate(TroubleBase):
    project_id: int = Field(..., description="関連するプロジェクトID")

class TroubleUpdate(TroubleBase):
    pass

class TroubleResponse(TroubleBase):
    id: int
    project_id: int
    project_title: str
    author_id: int
    author: str
    created_at: datetime
    comments: int = 0

    class Config:
        orm_mode = True

class TroubleDetailResponse(TroubleResponse):
    # メッセージ関連の情報を追加する場合
    # messages: List[MessageResponse] = []
    pass

class TroublesListResponse(BaseModel):
    troubles: List[TroubleResponse]
    total: int