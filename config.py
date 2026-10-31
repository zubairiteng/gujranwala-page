"""
Configuration file for Hamara Gujranwala Facebook Page Automation.
Page Target: 2,000+ Followers within 30 Days through High-Authority Local News,
Hero Tributes, Culture, Food, and Community Engagement.
"""

import os

# Facebook Page Details
PAGE_NAME = "Hamara Gujranwala"
PAGE_ID = os.getenv("FB_PAGE_ID", "61578710350501")
PAGE_URL = "https://www.facebook.com/profile.php?id=61578710350501"
PAGE_TAGLINE = "گوجرانوالہ کی ہر گلی، ہر چوک، اور ہر تندور کی خبر اب آپ تک"

# Graph API Credentials
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "").strip()
GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Target Metrics
TARGET_FOLLOWERS = 2000
DAYS_TIMEFRAME = 30
DAILY_POST_TARGET = 6  # Minimum 6 posts per day

# Editorial Guardrails (Strict Source Verification & Community Safety)
APPROVED_NEWS_SOURCES = [
    "Dawn",
    "The Express Tribune",
    "The News International",
    "Geo News",
    "Dunya News",
    "Express News",
    "ARY News",
    "BBC Urdu",
    "Aaj News",
    "Daily Pakistan",
    "Associated Press of Pakistan (APP)",
    "Radio Pakistan",
    "Deputy Commissioner Gujranwala Official",
    "Rescue 1122 Gujranwala",
    "City Traffic Police Gujranwala",
    "Punjab Police Official",
]

# Prohibited Topics & Safety Filter
PROHIBITED_KEYWORDS = [
    "leak",
    "mms",
    "vulgar",
    "blasphemy",
    "sectarian",
    "suicide video",
    "explicit",
    "unverified rumor",
    "hate speech",
    "cybercrime",
    "fraud scheme",
    "gambling",
]

# News Search Keywords & Geographic Scope
SEARCH_QUERIES = [
    "Gujranwala",
    "گوجرانوالہ",
    "Kamoke Gujranwala",
    "Wazirabad",
    "Nowshera Virkan",
]

# Time Slots (PKT UTC+5)
POSTING_SLOTS = [
    {"slot": "morning_brief", "pkt_hour": 8, "theme": "Daily Gujranwala Morning Update & Civic Alerts"},
    {"slot": "midday_news", "pkt_hour": 12, "theme": "Breaking / Real-Time Gujranwala News"},
    {"slot": "hero_spotlight", "pkt_hour": 15, "theme": "Gujranwala Hero / Wrestling Pride / Historical Icon"},
    {"slot": "evening_updates", "pkt_hour": 18, "theme": "Evening City Developments & Traffic / Weather"},
    {"slot": "culture_food", "pkt_hour": 20, "theme": "Gujranwala Food, Industry, Lifestyle & Landmarks"},
    {"slot": "community_question", "pkt_hour": 22, "theme": "Late-Night Engagement Question & Discussion"},
]
