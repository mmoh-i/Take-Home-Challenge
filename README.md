# Content Aggregator — Backend

This repository is a FastAPI-based backend for a content aggregation platform (take-home challenge). It fetches articles from multiple sources, stores them in PostgreSQL, and exposes endpoints for a frontend to query and manage user preferences.

This README contains setup instructions, an example `.env`, and sample API usage.

## Requirements

- Python 3.9+
- PostgreSQL (local or AWS RDS)
- (Optional) Docker if you prefer running Postgres in a container

## Quick setup (development)

1. Clone the repo and enter the directory (you already are here):

   ```bash
   git clone <repo-url> && cd take_home_challenge
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create or point to a PostgreSQL database.

   - Local (Homebrew):
     ```bash
     brew services start postgresql
     createdb take_home_challenge
     ```

   - AWS RDS: create an RDS instance and note host, username, password, and DB name.

5. Create an `.env` file (example below). The app uses `python-dotenv` to load env vars.

6. Start the server:

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

Open http://127.0.0.1:8000/docs for interactive API docs.

## Example `.env`

Place this file at the project root as `.env` (do NOT commit real credentials).

```
# Postgres (local or RDS)
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/take_home_challenge

# API keys
NEWSAPI_KEY=news_key_here(EventRegistry)
GUARDIAN_API_KEY=Your_guardian_key
FETCH_INTERVAL_SECONDS=900

# Other optional settings
# Sentry or other integrations can be added if needed
```

Notes:
- If using AWS RDS, set `DATABASE_URL` to: `postgresql://<USER>:<PASSWORD>@<HOST>:5432/<DBNAME>`
- If your password contains special characters, URL-encode them.

## Common issues & troubleshooting

- "can't adapt type 'HttpUrl'": Pydantic's `HttpUrl` must be cast to `str` before inserting into the DB. The codebase already casts `article.url` to `str` before insert.
- "column ... does not exist": This means your DB schema is out-of-sync with models. Use Alembic or run `ALTER TABLE` to add/rename columns (e.g. `author`, `fetched_at`).
- 401 from The Guardian: ensure `GUARDIAN_API_KEY` is present in `.env` and loaded. The fetcher will skip Guardian fetch if key is missing.

## Endpoints (summary)

- GET /articles
  - Query params: `skip`, `limit`, `source`, `author`, `category`, `date_from` (ISO), `date_to` (ISO), `q` (search)
  - Returns list of articles (Pydantic `ArticleRead`)

- POST /articles/sync
  - Triggers a fetch from configured sources and upserts into DB
  - Returns `{ "created": <n> }`

- GET /preferences/{user_id}
  - Returns user preference object

- POST /preferences
  - Body: `PreferenceIn` containing `user_id`, `favorite_sources`, `favorite_categories`

## Sample usage (curl)

1) Get latest articles (no filters):

```bash
curl -s "http://127.0.0.1:8000/articles" | jq '.'
```

2) Filter by source and author:

```bash
curl -s "http://127.0.0.1:8000/articles?source=The%20Guardian&author=Aliyu%20Amin" | jq '.'
```

3) Trigger a manual sync (fetch + upsert):

```bash
curl -X POST "http://127.0.0.1:8000/articles/sync"
```

4) Get or create preferences for a user:

```bash
curl "http://127.0.0.1:8000/preferences/user123"
```

5) Set preferences:

```bash
curl -X POST "http://127.0.0.1:8000/preferences" -H "Content-Type: application/json" -d '{"user_id":"user123","favorite_sources":["The Guardian"],"favorite_categories":["technology"]}'
```

## Sample response (GET /articles)

```json
[
  {
    "title": "Chess outsiders triumph at World Cup in Goa and battle for Candidates spots",
        "url": "https://www.theguardian.com/sport/2025/nov/21/chess-outsiders-triumph-at-world-cup-in-goa-and-battle-for-candidates-spots",
        "source": "The Guardian",
        "category": "Sport",
        "author": null,
        "summary": "The four semi-finalists, led by Wei Yi, will battle for three 2026 Candidates places – none of them has reached this stage before",
        "content": "The $2m World Cup in Goa will be remembered as an event where established stars were humbled and knocked out by supposedly lesser lights. At 26, China’s Wei Yi is the oldest in Friday’s semi-finals. He was once a prodigy, renowned for his brilliant attacking style and the youngest to surpass an elite 2700 rating, but then opted to take a six-year break from chess to study economics and management, which he says he does not regret.  It is an all-Uzbek semi-final as Sindarov’s opponent is Nodirbek Yakubboev,\n 23, whose refusal, for religious reasons, to shake hands with India’s Vaishali Rameshbabu at the start of their game at Wijk aan Zee made headlines.  the second-strongest female player of all time. Hou won her first game smoothly, but the likely winners of the entire event are the so-called Fide team, which is actually the full-strength Russian squad playing their first team tournament since the invasion of Ukraine in 2022. On Sunday, the UK Open Blitz Championship finals take place at Leamington Spa, and will be covered by online commentaries. GM Gawain Jones is the top seed and favourite in the Open, although GM Eldar Gasanov, the 2023 and 2024 winner, is sure to make a bid to retain his title. In the Women’s Championship, 10-year-old Bodhana Sivanandan is top seeded after missing the title narrowly in 2023 and 2024. 3999: 1…f2! 2 Qxg5 Qh1+! 3 Kxh1 f1=Q+ 4 Kh2 Rf2+ 5 Kg3 Rf3+ 6 Kg4 Qxh3 mate.",
        "published_at": "2025-11-21T08:00:05",
        "id": 158,
        "fetched_at": "2025-11-21T09:31:34.944290"
  }
]
```

## Development tips

- Add a third data source (e.g., NewsAPI) in `fetchers.py` to meet the challenge requirements.
- Use the scheduler in `scheduler.py` to run `bulk_upsert_articles` periodically.
- Add unit tests for fetchers and CRUD operations where possible.

## Screenshot / Deliverable

Drop your screenshot(s) into the repo (e.g. `./screenshots/sync-success.png`).

You can reference them in the README like:

```
![sync success](screenshots/sync-success.png)
```

## Screenshots (included)

Few Postman screenshots demonstrating some endpoints flows.

- Sync button / trigger:

![Sync To refrech Content](screenshots/Sync20%To20%refrech20%Content.png)

- Successful refresh (shows refreshed content list):

![refreshed contents](screenshots/refreshed20%contents.png)

- Filtering by category UI / example Postman query:

![filter by category](screenshots/filter20%by20%category.png)

- Pagination behavior in the frontend / results:

![Pagination](screenshots/Pagination.png)
