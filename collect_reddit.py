import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request

SUBREDDITS = ['diablo4', 'diablo', 'DiabloIV']
BASE = Path(__file__).resolve().parent / 'data'
POSTS_OUT = BASE / 'reddit_posts.csv'
COMMENTS_OUT = BASE / 'reddit_comments.csv'
BASE.mkdir(parents=True, exist_ok=True)


def fetch_json(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; DiabloDashboard/1.0)'})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))


def collect_posts(limit=50):
    rows = []
    seen = set()
    for sub in SUBREDDITS:
        url = f'https://www.reddit.com/r/{sub}/new.json?limit={limit}'
        data = fetch_json(url)
        for child in data.get('data', {}).get('children', []):
            d = child.get('data', {})
            pid = d.get('id')
            if not pid or pid in seen:
                continue
            seen.add(pid)
            title = d.get('title') or ''
            body = d.get('selftext') or ''
            topic = infer_topic(f'{title} {body}')
            sentiment = infer_sentiment(f'{title} {body}')
            rows.append({
                'post_id': pid,
                'timestamp': datetime.fromtimestamp(d.get('created_utc', 0), tz=timezone.utc).isoformat(),
                'sentiment': sentiment,
                'language': 'english',
                'country': '',
                'score': d.get('score', 0),
                'comment_count': d.get('num_comments', 0),
                'topic': topic,
                'title': title.replace('\n', ' ').strip(),
                'body': body.replace('\n', ' ').strip(),
                'subreddit': sub,
                'url': 'https://www.reddit.com' + (d.get('permalink') or ''),
                'source': 'Reddit',
            })
    return rows


def collect_comments(posts, per_post=20):
    rows = []
    for post in posts[:20]:
        url = post['url'].rstrip('/') + f'.json?limit={per_post}'
        try:
            data = fetch_json(url)
        except Exception:
            continue
        if len(data) < 2:
            continue
        comments = data[1].get('data', {}).get('children', [])
        for child in comments:
            if child.get('kind') != 't1':
                continue
            d = child.get('data', {})
            body = d.get('body') or ''
            if not body or body in ['[deleted]', '[removed]']:
                continue
            rows.append({
                'comment_id': d.get('id'),
                'timestamp': datetime.fromtimestamp(d.get('created_utc', 0), tz=timezone.utc).isoformat(),
                'sentiment': infer_sentiment(body),
                'language': 'english',
                'country': '',
                'score': d.get('score', 0),
                'topic': infer_topic(body),
                'body': body.replace('\n', ' ').strip(),
                'post_id': post['post_id'],
                'subreddit': post['subreddit'],
                'source': 'Reddit',
            })
    return rows


def infer_topic(text):
    text = (text or '').lower()
    topic_map = {
        'balance': ['balance', 'nerf', 'buff', 'class'],
        'loot': ['loot', 'drop', 'legendary', 'unique'],
        'progression': ['progression', 'leveling', 'xp', 'grind'],
        'endgame': ['endgame', 'pit', 'nightmare', 'torment'],
        'season content': ['season', 'battle pass', 'seasonal'],
        'build diversity': ['build', 'meta', 'viable'],
        'performance': ['performance', 'fps', 'stutter', 'lag'],
        'bugs': ['bug', 'broken', 'crash', 'issue'],
        'monetization': ['shop', 'mtx', 'monetization', 'skin'],
        'rewards': ['reward', 'rewarding', 'cache', 'boss materials'],
    }
    for topic, keywords in topic_map.items():
        if any(k in text for k in keywords):
            return topic
    return 'general'


def infer_sentiment(text):
    text = (text or '').lower()
    pos = ['good', 'great', 'fun', 'love', 'better', 'rewarding']
    neg = ['bad', 'worse', 'boring', 'hate', 'broken', 'stale', 'lag', 'crash', 'nerf']
    ps = sum(1 for w in pos if w in text)
    ns = sum(1 for w in neg if w in text)
    if ps > ns:
        return 'positive'
    if ns > ps:
        return 'negative'
    return 'neutral'


def write_csv(path, rows, fieldnames):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    posts = collect_posts()
    comments = collect_comments(posts)
    write_csv(POSTS_OUT, posts, ['post_id','timestamp','sentiment','language','country','score','comment_count','topic','title','body','subreddit','url','source'])
    write_csv(COMMENTS_OUT, comments, ['comment_id','timestamp','sentiment','language','country','score','topic','body','post_id','subreddit','source'])
    print(f'wrote {len(posts)} reddit posts -> {POSTS_OUT}')
    print(f'wrote {len(comments)} reddit comments -> {COMMENTS_OUT}')
