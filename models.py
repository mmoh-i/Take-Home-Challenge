from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(1000), nullable=False)
    url = Column(String(2000), unique=True, nullable=False)
    source = Column(String(1000), nullable=False, index=True)
    category = Column(String(1000), nullable=False, index=True)
    author = Column(String(1000), nullable=True, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    favorite_sources = Column(Text, nullable=True)
    favorite_categories = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint('user_id', name='uq_user'),)
    # No direct relationship defined here. If you plan to relate preferences
    # to other models, add the relationship after defining both classes.