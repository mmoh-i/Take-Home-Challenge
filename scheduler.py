from apscheduler.schedulers.background import BackgroundScheduler
from fetchers import fetch_all_sources
from crud import bulk_upsert_articles
from database import SessionLocal
from dotenv import load_dotenv
import os

load_dotenv()

interval = int(os.getenv("FETCH_INTERVAL_SECONDS", 900))
def run_scheduler():
    db = SessionLocal()
    try:
        articles = fetch_all_sources()
        print(f"Fetched {len(articles)} articles. Upserting to database...")
            
        created_articles = bulk_upsert_articles(db, articles)
        print(f"Inserted {len(created_articles)} new articles.")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduler, 'interval', seconds=interval, max_instances=1)
    scheduler.start()
    return scheduler