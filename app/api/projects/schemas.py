from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="プロジェクトのタイトル")
    description: str = Field(..., min_length=10, max_length=1000, description="プロジェクトの詳細説明")
    category: str = Field(..., description="プロジェクトのカテゴリー")

class ProjectCreate(ProjectBase):
    author_id: int

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    author_id: int
    author: str
    created_at: datetime
    likes: int = 0
    comments: int = 0
    is_favorite: bool = False

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    new_projects: List[ProjectResponse]
    favorite_projects: List[ProjectResponse]
    total_projects: int

class ProjectCategoryResponse(BaseModel):
    categories: List[str]

class UserFavoriteProjectCreate(BaseModel):
    user_id: int
    project_id: int

class RankingUser(BaseModel):
    name: str
    points: int
    rank: int
