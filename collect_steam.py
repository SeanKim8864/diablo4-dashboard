import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request

APP_ID = 2344520  # Diablo IV on Steam
OUT = Path(__file__).resolve().parent / 'data' / 'steam_reviews.csv'
OUT.parent.mkdir(parents=True, exist_ok=True)


def fetch_reviews(num_per_page=100, max_pages=5):
    rows = []
    cursor = '*'
    for _ in range(max_pages):
        params = {
            'json': 1,
            'language': 'all',
            'filter': 'recent',
            'day_range': 365,
            'num_per_page': num_per_page,
            'cursor': cursor,
            'purchase_type': 'all',
        }
        url = f"https://store.steampowered.com/appreviews/{APP_ID}?{urlencode(params)}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode('utf-8', errors='ignore'))
        for r in payload.get('reviews', []):
            rows.append({
                'review_id': r.get('recommendationid'),
                'timestamp': datetime.fromtimestamp(r.get('timestamp_created', 0), tz=timezone.utc).isoformat(),
                'sentiment': 'positive' if r.get('voted_up') else 'negative',
                'language': r.get('language'),
                'country': '',
                'playtime_hours': round((r.get('author', {}).get('playtime_forever', 0) or 0) / 60, 2),
                'helpful_votes': r.get('votes_up', 0),
                'recommendation': 'recommended' if r.get('voted_up') else 'not_recommended',
                'review_text': (r.get('review') or '').replace('\r', ' ').replace('\n', ' ').strip(),
                'source': 'Steam',
            })
        cursor = payload.get('cursor')
        if not payload.get('success') or not payload.get('reviews') or not cursor:
            break
    return rows


def write_csv(rows):
    fieldnames = [
        'review_id', 'timestamp', 'sentiment', 'language', 'country',
        'playtime_hours', 'helpful_votes', 'recommendation', 'review_text', 'source'
    ]
    with OUT.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    rows = fetch_reviews()
    write_csv(rows)
    print(f'wrote {len(rows)} steam reviews -> {OUT}')
