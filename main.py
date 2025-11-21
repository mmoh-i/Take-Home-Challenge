from fastapi import FastAPI, Depends, HTTPException, Query
from contextlib import asynccontextmanager
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from schemas import ArticleRead, ArticleCreate, PreferenceIn, PreferenceOut
from crud import list_articles, bulk_upsert_articles, get_or_create_preference, update_user_preference
from scheduler import start_scheduler
from typing import Optional, List
from models import Article, UserPreference

Base.metadata.create_all(bind=engine)
app = FastAPI(title="News Aggregator API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
def startup_event():
    start_scheduler()

@app.get("/")
def root():
    return {"message": "API is working"}

@app.get("/articles", response_model=List[ArticleRead])
def read_articles(skip: int = 0, limit: int = 50, source: Optional[str] = None, author: Optional[str] = None, category: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    filters = {}
    if source:
        filters['source'] = source
    if author:
        filters['author'] = author
    if category:
        filters['category'] = category
    if date_from:
        from datetime import datetime
        filters['date_from'] = datetime.fromisoformat(date_from)
    if date_to:
        from datetime import datetime
        filters['date_to'] = datetime.fromisoformat(date_to)
    #search by keyword
    if q:
        filters['q'] = q
    return list_articles(db, skip=skip, limit=limit, filters=filters)

@app.post("/articles/sync")
def sync_now(db: Session = Depends(get_db)):
    from fetchers import fetch_all_sources
    articles = fetch_all_sources()
    created = bulk_upsert_articles(db, articles)
    return {"created": len(created)}

@app.get("/preferences/{user_id}", response_model=PreferenceOut)
def get_preferences(user_id: str, db: Session = Depends(get_db)):
    pref = get_or_create_preference(db, user_id)
    import json
    return PreferenceOut(
        user_id=pref.user_id,
        favorite_sources=json.loads(pref.favorite_sources) if pref.favorite_sources else [],
        favorite_categories=json.loads(pref.favorite_categories) if pref.favorite_categories else []
    )

@app.post("/preferences", response_model=PreferenceOut)
def set_preferences(pref_in: PreferenceIn, db: Session = Depends(get_db)):
    pref = update_user_preference(db, pref_in.user_id, pref_in.favorite_sources, pref_in.favorite_categories)
    import json
    return PreferenceOut(
        user_id=pref.user_id,
        favorite_sources=json.loads(pref.favorite_sources) if pref.favorite_sources else [],
        favorite_categories=json.loads(pref.favorite_categories) if pref.favorite_categories else []
    )
