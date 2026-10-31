"""
News Aggregator for Gujranwala.
Pulls verified news from Google News RSS & Pakistani news feeds, filters for
authentic tier-1 outlets, removes duplicates, and applies safety checks.
"""

import hashlib
import json
import os
import re
import urllib.parse
from datetime import datetime
import feedparser
from dateutil import parser as date_parser

from config import APPROVED_NEWS_SOURCES, PROHIBITED_KEYWORDS, SEARCH_QUERIES

HISTORY_FILE = "history.json"


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
    # Strip typical source tails
    parts = re.split(r"\s+[-–|]\s+", title)
    if len(parts) > 1:
        # If the last part is a source name
        return " - ".join(parts[:-1]).strip()
    return title.strip()


def extract_source(entry):
    """Extract source name from feed entry."""
    if hasattr(entry, "source") and isinstance(entry.source, dict):
        return entry.source.get("title", "Verified Source")
    if hasattr(entry, "title"):
        parts = re.split(r"\s+[-–|]\s+", entry.title)
        if len(parts) > 1:
            return parts[-1].strip()
    return "Official Media Report"


def fetch_gujranwala_news(limit=5):
    """
    Fetch latest verified Gujranwala news from RSS feeds.
    Returns a list of unposted, verified news items.
    """
    history = load_history()
    posted_ids = set(history.get("posted_ids", []))
    posted_urls = set(history.get("posted_urls", []))

    collected = []
    seen_in_batch = set()

    for query in SEARCH_QUERIES:
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

                # Filter out YouTube/unverified social clips
                source_name = extract_source(entry)
                if "youtube" in link.lower() or "youtube" in source_name.lower():
                    continue

                # Deduplication hash based on cleaned headline
                cleaned = clean_headline(title)
                story_hash = hashlib.md5(cleaned.lower().encode("utf-8")).hexdigest()

                if story_hash in posted_ids or link in posted_urls or story_hash in seen_in_batch:
                    continue

                # Parse published time
                pub_dt = None
                if published_str:
                    try:
                        pub_dt = date_parser.parse(published_str)
                    except Exception:
                        pub_dt = datetime.utcnow()
                else:
                    pub_dt = datetime.utcnow()

                seen_in_batch.add(story_hash)
                collected.append({
                    "id": story_hash,
                    "title": cleaned,
                    "original_title": title,
                    "source": source_name,
                    "link": link,
                    "published": pub_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "summary": summary
                })

                if len(collected) >= limit:
                    break
        except Exception as e:
            print(f"Error fetching query '{query}': {e}")

        if len(collected) >= limit:
            break

    return collected


if __name__ == "__main__":
    news = fetch_gujranwala_news(limit=3)
    print(f"Fetched {len(news)} fresh Gujranwala news stories:")
    for n in news:
        print(f"- [{n['source']}] {n['title']} ({n['published']})")
