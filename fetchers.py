import os
import requests
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from schemas import ArticleCreate

load_dotenv()

# Use clear, consistent env var names
EVENTREG_API_KEY = os.getenv("NEWSAPI_KEY")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")


def log(source: str, message: str):
    print(f"[{source}] {message}")


def safe_date(dt):
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except Exception:
        return None


# News Api
def convert_eventreg_article(item) -> ArticleCreate:
    return ArticleCreate(
        title=item.get("title"),
        url=item.get("url"),
        source=item.get("source", {}).get("title", "Unknown"),
        category=(
            item.get("categories", [{}])[0].get("label")
            if item.get("categories")
            else "general"
        ),
        summary=item.get("summary"),
        content=item.get("body"),
        published_at=safe_date(item.get("date"))
    )


def fetch_from_eventregistry(query: dict, pages: int = 1, per_page: int = 100) -> List[ArticleCreate]:
    log("EventRegistry", "Starting fetch...")
    all_articles = []

    for page in range(1, pages + 1):
        body = {
            "action": "getArticles",
            "query": {"$query": query},
            "articlesPage": page,
            "articlesCount": per_page,
            "articlesSortBy": "date",
            "articlesSortByAsc": False,
            "articlesArticleBodyLen": -1,
            "includeArticleTitle": True,
            "includeArticleBody": True,
            "includeArticleAuthors": True,
            "includeArticleCategories": True,
            "includeSourceTitle": True,
            "resultType": "articles",
            "apiKey": EVENTREG_API_KEY
        }

        try:
            resp = requests.post(
                "https://eventregistry.org/api/v1/article/getArticles",
                json=body,
                timeout=15
            )
        except Exception as e:
            log("EventRegistry", f"Network error: {e}")
            continue

        if resp.status_code != 200:
            log("EventRegistry", f"API error {resp.status_code}: {resp.text}")
            continue

        results = resp.json().get("articles", {}).get("results", [])
        log("EventRegistry", f"Page {page}: {len(results)} articles")

        for item in results:
            try:
                all_articles.append(convert_eventreg_article(item))
            except Exception as e:
                log("EventRegistry", f"Parse error: {e}")

    log("EventRegistry", f"TOTAL articles fetched: {len(all_articles)}")
    return all_articles


# THE GUARDIAN API

def convert_guardian_article(item) -> ArticleCreate:
    fields = item.get("fields", {})

    return ArticleCreate(
        title=item.get("webTitle"),
        url=item.get("webUrl"),
        source="The Guardian",
        category=item.get("sectionName", "general"),
        summary=fields.get("trailText"),
        content=fields.get("bodyText"),
        published_at=safe_date(item.get("webPublicationDate")),
    )



def fetch_from_guardian(pages: int = 1) -> List[ArticleCreate]:
    log("Guardian", "Starting fetch...")

    if not GUARDIAN_API_KEY:
        log("Guardian", "ERROR: No API key found in environment variable GUARDIAN_API_KEY")
        return []

    articles = []
    base_url = "https://content.guardianapis.com/search"

    for page in range(1, pages + 1):
        params = {
            "api-key": GUARDIAN_API_KEY,
            "show-fields": "trailText,bodyText",
            "page-size": 100,
            "page": page
        }

        try:
            resp = requests.get(base_url, params=params, timeout=15)
        except Exception as e:
            log("Guardian", f"Network error: {e}")
            continue

        if resp.status_code != 200:
            log("Guardian", f"API error {resp.status_code}: {resp.text}")
            continue

        data = resp.json().get("response", {})
        results = data.get("results", [])

        log("Guardian", f"Page {page}: {len(results)} articles")

        for item in results:
            try:
                articles.append(convert_guardian_article(item))
            except Exception as e:
                log("Guardian", f"Parse error: {e}")

    log("Guardian", f"TOTAL articles fetched: {len(articles)}")
    return articles



def fetch_all_sources() -> List[ArticleCreate]:
    log("FETCHER", "Collecting articles from EventRegistry + Guardian")

    all_articles = []

    # EventRegistry Default Query
    default_query = {
        "$and": [
            {"keyword": "AI"},
            {"categoryUri": "dmoz/Computers/Artificial_Intelligence"}
        ]
    }

    try:
        er_articles = fetch_from_eventregistry(default_query, pages=1)
        all_articles.extend(er_articles)
    except Exception as e:
        log("FETCHER", f"EventRegistry fetch error: {e}")

    # The Guardian
    try:
        guardian_articles = fetch_from_guardian(pages=1)
        all_articles.extend(guardian_articles)
    except Exception as e:
        log("FETCHER", f"Guardian fetch error: {e}")

    log("FETCHER", f"TOTAL ARTICLES COLLECTED: {len(all_articles)}")

    return all_articles
