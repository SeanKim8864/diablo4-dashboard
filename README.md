# Diablo IV — Sanctuary Console

Dark gothic executive dashboard for Diablo IV using only public Steam and Reddit data.
Built with FastAPI + Chart.js. Zero framework frontend — pure HTML/CSS/JS.

## Scope
- Satisfaction rate by major country
- Last 14 days player behavior metrics
- Core keywords and trends
- Satisfaction by playtime
- Topic frequency, sentiment, and engagement analysis

## Run
```bash
pip install -r requirements.txt
uvicorn server:app --reload
```
Open `http://localhost:8000`

## Render deploy
This app can be deployed on Render as a Python web service.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- Included file: `render.yaml`

## Data files
Place CSV files under `data/`:
- `steam_reviews.csv`
- `reddit_posts.csv`
- `reddit_comments.csv`

If files are missing, the app uses mock fallback data so the UI still renders.
