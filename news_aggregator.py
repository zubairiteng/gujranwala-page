"""
News Aggregator for Gujranwala.
Prioritizes real-time, fresh updates from Gujranwala local sources
(Gujranwala Page, Gujranwala Tez, Express Urdu, Dunya, Geo, Dawn),
strictly rejects outdated news (> 48 hours), removes duplicates, and applies safety checks.
"""

import hashlib
import json
import os
import re
import urllib.parse
from datetime import datetime, timezone, timedelta
import feedparser
from dateutil import parser as date_parser

from config import PROHIBITED_KEYWORDS

HISTORY_FILE = "history.json"
MAX_AGE_HOURS = 48  # Strict freshness: reject anything older than 48 hours


def load_history():
    """Load previously posted story IDs."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"posted_ids": [], "posted_urls": []}
    return {"posted_ids": [], "posted_urls": []}


def save_history(history):
    """Save history state."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")


def is_safe_and_ethical(title, summary=""):
    """Verify that story is safe, does not promote hate speech or cybercrime."""
    text = f"{title} {summary}".lower()
    for kw in PROHIBITED_KEYWORDS:
        if kw in text:
            return False
    return True


def clean_headline(title):
    """Clean headline by stripping common trailing source names like '- Dawn'."""
    parts = re.split(r"\s+[-–|]\s+", title)
    if len(parts) > 1:
        return " - ".join(parts[:-1]).strip()
    return title.strip()


def extract_source(entry):
    """Extract source name from feed entry."""
    if hasattr(entry, "source") and isinstance(entry.source, dict):
        return entry.source.get("title", "گوجرانوالہ پیج / باوثوق ذرائع")
    if hasattr(entry, "title"):
        parts = re.split(r"\s+[-–|]\s+", entry.title)
        if len(parts) > 1:
            return parts[-1].strip()
    return "گوجرانوالہ پیج / باوثوق ذرائع"


def fetch_gujranwala_news(limit=3):
    """
    Fetch latest verified Gujranwala news from RSS feeds.
    Strictly filters for news within the last 48 hours (no outdated data).
    """
    history = load_history()
    posted_ids = set(history.get("posted_ids", []))
    posted_urls = set(history.get("posted_urls", []))

    now_utc = datetime.now(timezone.utc)
    collected = []
    seen_in_batch = set()

    # Search queries targeted for fresh 24-48h updates
    queries = [
        "Gujranwala when:2d",
        "گوجرانوالہ when:2d",
        "site:facebook.com/GujranwalaPage when:3d",
        "site:express.pk گوجرانوالہ when:2d",
        "site:jang.com.pk گوجرانوالہ when:2d",
        "site:dailypakistan.com.pk گوجرانوالہ when:2d",
        "Gujranwala Tez",
    ]

    for query in queries:
        encoded_query = urllib.parse.quote(query)
        feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-PK&gl=PK&ceid=PK:en"
        
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                summary = getattr(entry, "summary", "").strip()
                published_str = getattr(entry, "published", "")

                if not title or not link:
                    continue

                # Safety check
                if not is_safe_and_ethical(title, summary):
                    continue

                # Filter out YouTube/unverified social noise
                source_name = extract_source(entry)
                if "youtube" in link.lower() or "youtube" in source_name.lower():
                    continue

                # Strict Freshness Check
                pub_dt = None
                if published_str:
                    try:
                        pub_dt = date_parser.parse(published_str)
                        if pub_dt.tzinfo is None:
                            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                    except Exception:
                        pub_dt = now_utc
                else:
                    pub_dt = now_utc

                # Reject news older than MAX_AGE_HOURS (48h)
                age_hours = (now_utc - pub_dt).total_seconds() / 3600.0
                if age_hours > MAX_AGE_HOURS:
                    continue

                cleaned = clean_headline(title)
                story_hash = hashlib.md5(cleaned.lower().encode("utf-8")).hexdigest()

                if story_hash in posted_ids or link in posted_urls or story_hash in seen_in_batch:
                    continue

                seen_in_batch.add(story_hash)
                collected.append({
                    "id": story_hash,
                    "title": cleaned,
                    "original_title": title,
                    "source": source_name,
                    "link": link,
                    "published": pub_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "published_dt": pub_dt,
                    "summary": summary
                })

                if len(collected) >= limit:
                    break
        except Exception as e:
            print(f"Notice: Query '{query}' check: {e}")

        if len(collected) >= limit:
            break

    # Sort strictly by most recent first
    collected.sort(key=lambda x: x["published_dt"], reverse=True)
    return collected


if __name__ == "__main__":
    news = fetch_gujranwala_news(limit=3)
    print(f"Fetched {len(news)} fresh Gujranwala news stories (within 48h):")
    for n in news:
        print(f"- [{n['source']}] {n['title']} ({n['published']})")
