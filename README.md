# Diablo IV Trend Dashboard

Executive dashboard for Diablo IV using only public Steam and Reddit data.

## Scope
- Satisfaction rate by major country
- Last 14 days player behavior metrics
- Core keywords and trends
- Satisfaction by playtime

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Render deploy
This app can be deployed on Render as a Python web service.
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- Included file: `render.yaml`

## Data files
Place CSV files under `data/`:
- `steam_reviews.csv`
- `reddit_posts.csv`
- `reddit_comments.csv`

If files are missing, the app uses mock fallback data so the UI still renders.
