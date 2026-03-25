"""Diablo IV Dashboard – FastAPI backend."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

app = FastAPI(title="Diablo IV Dashboard API")


# ---------------------------------------------------------------------------
# Helpers (ported from original app.py)
# ---------------------------------------------------------------------------

def safe_read_csv(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def normalize_sentiment(x):
    if pd.isna(x):
        return "neutral"
    x = str(x).lower().strip()
    if x in ("positive", "pos", "good", "recommended", "긍정"):
        return "positive"
    if x in ("negative", "neg", "bad", "not_recommended", "부정"):
        return "negative"
    return "neutral"


def sentiment_score(label: str) -> int:
    return 1 if label == "positive" else -1 if label == "negative" else 0


LANG_COUNTRY = {
    "english": "미국/영국/영어권", "en": "미국/영국/영어권",
    "korean": "대한민국", "ko": "대한민국",
    "german": "독일", "de": "독일",
    "french": "프랑스", "fr": "프랑스",
    "spanish": "스페인/중남미", "es": "스페인/중남미",
    "japanese": "일본", "ja": "일본",
    "russian": "러시아", "ru": "러시아",
    "chinese": "중국", "zh": "중국",
    "portuguese": "브라질/포르투갈", "pt": "브라질/포르투갈",
    "italian": "이탈리아", "it": "이탈리아",
    "turkish": "튀르키예", "tr": "튀르키예",
    "polish": "폴란드", "pl": "폴란드",
    "thai": "태국", "th": "태국",
}


def estimate_country(row):
    c = row.get("country")
    if pd.notna(c) and str(c).strip():
        return str(c).strip()
    lang = str(row.get("language", "")).lower()
    return LANG_COUNTRY.get(lang, "미상")


def playtime_bucket(hours):
    if pd.isna(hours):
        return "미상"
    if hours < 10:
        return "10시간 미만"
    if hours < 50:
        return "10~50시간"
    if hours < 100:
        return "50~100시간"
    if hours < 300:
        return "100~300시간"
    return "300시간 이상"


TOPIC_KR = {
    "general": "일반 의견",
    "loot": "전리품",
    "balance": "밸런스",
    "season content": "시즌 콘텐츠",
    "progression": "성장",
    "build diversity": "빌드 다양성",
    "bugs": "버그",
    "performance": "성능",
    "rewards": "보상",
    "endgame": "엔드게임",
    "monetization": "과금",
}


def localize_topic(t):
    return TOPIC_KR.get(str(t).strip().lower(), str(t))


# ---------------------------------------------------------------------------
# Load & process data
# ---------------------------------------------------------------------------

def load_data():
    steam = safe_read_csv(str(DATA / "steam_reviews.csv"))
    reddit_posts = safe_read_csv(str(DATA / "reddit_posts.csv"))
    reddit_comments = safe_read_csv(str(DATA / "reddit_comments.csv"))

    # Mock fallback
    if steam.empty:
        steam = pd.DataFrame({
            "review_id": range(1, 7),
            "timestamp": pd.date_range(end=datetime.today(), periods=6).astype(str),
            "sentiment": ["positive", "negative", "negative", "positive", "neutral", "positive"],
            "language": ["english", "korean", "english", "german", "english", "japanese"],
            "country": [None] * 6,
            "playtime_hours": [5, 25, 80, 140, 350, 45],
            "helpful_votes": [11, 4, 9, 15, 23, 6],
            "recommendation": ["recommended", "not_recommended", "not_recommended", "recommended", "recommended", "recommended"],
            "source": ["Steam"] * 6,
        })

    if reddit_posts.empty:
        reddit_posts = pd.DataFrame({
            "post_id": range(101, 105),
            "timestamp": pd.date_range(end=datetime.today(), periods=4).astype(str),
            "sentiment": ["negative", "positive", "negative", "neutral"],
            "language": ["english"] * 4,
            "country": [None] * 4,
            "score": [120, 90, 55, 20],
            "comment_count": [45, 30, 12, 5],
            "topic": ["balance", "loot", "performance", "endgame"],
            "source": ["Reddit"] * 4,
        })

    if reddit_comments.empty:
        reddit_comments = pd.DataFrame({
            "comment_id": range(201, 206),
            "timestamp": pd.date_range(end=datetime.today(), periods=5).astype(str),
            "sentiment": ["negative", "negative", "positive", "neutral", "negative"],
            "language": ["english"] * 5,
            "country": [None] * 5,
            "score": [10, 7, 5, 2, 3],
            "topic": ["balance", "bugs", "rewards", "build diversity", "performance"],
            "source": ["Reddit"] * 5,
        })

    for df in [steam, reddit_posts, reddit_comments]:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dt.tz_convert(None)
        df["sentiment"] = df["sentiment"].apply(normalize_sentiment)
        df["score_val"] = df["sentiment"].apply(sentiment_score)
        df["country_est"] = df.apply(estimate_country, axis=1)

    steam["playtime_bucket"] = steam["playtime_hours"].apply(playtime_bucket)

    reddit_posts["disc_type"] = "post"
    reddit_comments["disc_type"] = "comment"
    reddit = pd.concat([reddit_posts, reddit_comments], ignore_index=True, sort=False)

    return steam, reddit


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.get("/api/dashboard")
def dashboard_data():
    steam, reddit = load_data()

    today = datetime.today()
    start = today - timedelta(days=14)
    end = today + timedelta(days=1)

    steam_f = steam[(steam["timestamp"] >= start) & (steam["timestamp"] <= end)]
    reddit_f = reddit[(reddit["timestamp"] >= start) & (reddit["timestamp"] <= end)]
    combined = pd.concat([steam_f, reddit_f], ignore_index=True, sort=False)

    total = len(combined)
    pos = int((combined["sentiment"] == "positive").sum())
    neg = int((combined["sentiment"] == "negative").sum())
    neu = total - pos - neg
    sat_rate = round(pos / total * 100, 1) if total else 0
    neg_rate = round(neg / total * 100, 1) if total else 0

    # Top issue
    top_issue = "General"
    if "topic" in reddit_f.columns and not reddit_f.empty:
        top_issue = localize_topic(reddit_f["topic"].value_counts().index[0])

    # Daily trend
    def daily(df, label):
        if df.empty:
            return {}
        out = df.copy()
        out["date"] = out["timestamp"].dt.strftime("%Y-%m-%d")
        return out.groupby("date").size().to_dict()

    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(15)]
    steam_daily = daily(steam_f, "steam")
    reddit_daily = daily(reddit_f, "reddit")

    # Sentiment daily
    sent_daily_pos = {}
    sent_daily_neg = {}
    if not combined.empty:
        tmp = combined.copy()
        tmp["date"] = tmp["timestamp"].dt.strftime("%Y-%m-%d")
        for d, grp in tmp.groupby("date"):
            n = len(grp)
            sent_daily_pos[d] = round((grp["sentiment"] == "positive").sum() / n * 100, 1) if n else 0
            sent_daily_neg[d] = round((grp["sentiment"] == "negative").sum() / n * 100, 1) if n else 0

    trend = []
    for d in dates:
        trend.append({
            "date": d,
            "steam": steam_daily.get(d, 0),
            "reddit": reddit_daily.get(d, 0),
            "pos_rate": sent_daily_pos.get(d, 0),
            "neg_rate": sent_daily_neg.get(d, 0),
        })

    # Country satisfaction
    countries = []
    if not combined.empty:
        for country, grp in combined.groupby("country_est"):
            n = len(grp)
            p = int((grp["sentiment"] == "positive").sum())
            countries.append({
                "country": country,
                "total": n,
                "positive": p,
                "rate": round(p / n * 100, 1),
            })
        countries.sort(key=lambda x: x["total"], reverse=True)

    # Playtime satisfaction
    playtime = []
    if not steam_f.empty and "playtime_bucket" in steam_f.columns:
        order = ["10시간 미만", "10~50시간", "50~100시간", "100~300시간", "300시간 이상"]
        for bucket, grp in steam_f.groupby("playtime_bucket"):
            n = len(grp)
            p = int((grp["sentiment"] == "positive").sum())
            playtime.append({
                "bucket": bucket,
                "total": n,
                "positive": p,
                "rate": round(p / n * 100, 1),
                "order": order.index(bucket) if bucket in order else 99,
            })
        playtime.sort(key=lambda x: x["order"])

    # Topics
    topics = []
    if "topic" in reddit_f.columns and not reddit_f.empty:
        tbl = reddit_f.groupby("topic").agg(
            freq=("topic", "count"),
            avg_sent=("score_val", "mean"),
            avg_score=("score", "mean"),
        ).reset_index().sort_values("freq", ascending=False)
        q75 = tbl["freq"].quantile(0.75)
        q25 = tbl["freq"].quantile(0.25)
        for _, r in tbl.head(10).iterrows():
            trend_dir = "rising" if r["freq"] >= q75 else "falling" if r["freq"] <= q25 else "stable"
            topics.append({
                "topic": localize_topic(r["topic"]),
                "freq": int(r["freq"]),
                "sentiment": round(r["avg_sent"], 3),
                "engagement": round(r["avg_score"], 1),
                "trend": trend_dir,
            })

    return {
        "summary": {
            "total": total,
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "sat_rate": sat_rate,
            "neg_rate": neg_rate,
            "top_issue": top_issue,
            "period": f"{start.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}",
        },
        "trend": trend,
        "countries": countries,
        "playtime": playtime,
        "topics": topics,
    }


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(str(BASE / "static" / "index.html"))


static_dir = BASE / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
