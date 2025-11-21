from sqlalchemy.orm import Session
from models import Article, UserPreference
from schemas import ArticleCreate, PreferenceIn
from typing import List, Optional
from datetime import datetime
import json

def get_article_by_url(db: Session, url: str) -> Optional[Article]:
    return db.query(Article).filter(Article.url == url).first()

#CRUD operations for UserPreference
def create_article(db: Session, article: ArticleCreate) -> Article:
    #URL is a plain string (Pydantic HttpUrl can't be adapted directly)
    url_val = str(article.url) if article.url is not None else None
    db_article = Article(
        title=article.title,
        url=url_val,
        source=article.source,
        author=article.author,
        category=article.category,
        summary=article.summary,
        content=article.content,
        published_at=article.published_at or datetime.utcnow(),
        fetched_at=datetime.utcnow()
    )
    db.add(db_article)
    try:
        db.commit()
        db.refresh(db_article)
        print(f"[DB] Inserted article: {db_article.title} -> {db_article.url}")
        return db_article
    except Exception as e:
        db.rollback()
        print(f"[DB] Error inserting article {article.title}: {e}")
        raise

def bulk_upsert_articles(db: Session, articles: List[ArticleCreate]) -> List[Article]:
    created = []
    for a in articles:
        try:
            url_str = str(a.url) if a.url is not None else None
        except Exception:
            url_str = None

        if not url_str:
            print(f"[UPSERT] Skipping article with missing/invalid URL: {getattr(a, 'title', '<no title>')}")
            continue

        exist = get_article_by_url(db, url_str)
        if not exist:
            print(f"[UPSERT] Creating article: {getattr(a, 'title', '')} ({url_str})")
            created.append(create_article(db, a))
        else:
            print(f"[UPSERT] Skipping existing article: {getattr(a, 'title', '')} ({url_str})")
    return created

def list_articles(db: Session, skip: int = 0, limit: int = 100, filters: dict = None) -> List[Article]:
    query = db.query(Article)
    if filters:
        if 'source' in filters:
            query = query.filter(Article.source == filters['source'])
        if 'category' in filters:
            query = query.filter(Article.category == filters['category'])
        if 'author' in filters:
            query = query.filter(Article.author == filters['author'])
        if 'date_from' in filters:
            query = query.filter(Article.published_at >= filters['date_from'])
        if 'date_to' in filters:
            query = query.filter(Article.published_at <= filters['date_to'])
        # a keyword search in title, content, or summary
        if 'keyword' in filters:
            keyword = f"%{filters['keyword']}%"
            query = query.filter(
                Article.title.ilike(keyword)
                | Article.content.ilike(keyword)
                | Article.summary.ilike(keyword)
            )
    return query.order_by(Article.published_at.desc()).offset(skip).limit(limit).all()

#get user preference or create by user_id
def get_or_create_preference(db: Session, user_id: str) -> Optional[UserPreference]:
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not preference:

        preference = UserPreference(user_id=user_id, favorite_sources=json.dumps([]), favorite_categories=json.dumps([]))
        db.add(preference)
        db.commit()
        db.refresh(preference)
    return preference

def update_user_preference(db: Session, user_id: str, preference_in: PreferenceIn) -> UserPreference:
    preference = get_or_create_preference(db, user_id)
    if preference_in.favorite_sources is not None:
        preference.favorite_sources = json.dumps(preference_in.favorite_sources)
    if preference_in.favorite_categories is not None:
        preference.favorite_categories = json.dumps(preference_in.favorite_categories)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference