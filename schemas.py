from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class ArticleBase(BaseModel):
    title: str = Field(..., max_length=1000)
    url: HttpUrl = Field(..., max_length=2000)
    source: str = Field(..., max_length=1000)
    category: str = Field(..., max_length=1000)
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass
class ArticleRead(ArticleBase):
    id: int
    fetched_at: Optional[datetime] = None
    class Config:
        orm_mode = True
        
class PreferenceIn(BaseModel):
    user_id: str
    favorite_sources: Optional[List[str]] = None
    favorite_categories: Optional[List[str]] = None

class PreferenceOut(BaseModel):
    user_id: str
    favorite_sources: Optional[List[str]] = None
    favorite_categories: Optional[List[str]] = None