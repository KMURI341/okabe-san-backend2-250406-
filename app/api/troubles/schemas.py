from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ...schemas.base import BaseSchemaModel

class TroubleBase(BaseSchemaModel):
    title: str = Field(..., min_length=1, max_length=100, description="お困りごとのタイトル")
    description: str = Field(..., min_length=10, description="お困りごとの詳細説明")
    category: str = Field(..., description="お困りごとのカテゴリー")

class TroubleCreate(TroubleBase):
    project_id: int = Field(..., description="関連するプロジェクトID")
    
class TroubleUpdate(BaseSchemaModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="お困りごとのタイトル")
    description: Optional[str] = Field(None, min_length=10, description="お困りごとの詳細説明")
    category: Optional[str] = Field(None, description="お困りごとのカテゴリー")
    status: Optional[str] = Field(None, description="お困りごとのステータス")

class TroubleResponse(TroubleBase):
    id: int
    project_id: int
    project: str
    author_id: int
    author: str
    status: str
    created_at: datetime
    comments: int = 0

class TroubleDetailResponse(TroubleResponse):
    pass

class TroublesListResponse(BaseSchemaModel):
    troubles: List[TroubleResponse]
    total: int