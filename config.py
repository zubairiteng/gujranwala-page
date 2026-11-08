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
TARGET_FOLLOWERS = 10000
DAYS_TIMEFRAME = 30
DAILY_POST_TARGET = 7  # 7 daily slots: 5 News + 1 Popular Personality + 1 Culture/Food

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
    "music single",
    "music video",
    "song release",
    "track release",
    "album release",
    "bollywood",
    "hollywood",
]

# News Search Keywords & Geographic Scope
SEARCH_QUERIES = [
    "Gujranwala",
    "گوجرانوالہ",
    "Kamoke Gujranwala",
    "Wazirabad",
    "Nowshera Virkan",
]

# Time Slots (PKT UTC+5): 5 News + 1 Personality + 1 Food/Culture = 7 Posts Daily
POSTING_SLOTS = [
    {"slot": "slot_1_morning_news", "pkt_hour": 8, "theme": "Morning Civic Brief & Weather", "type": "news"},
    {"slot": "slot_2_midday_news", "pkt_hour": 11, "theme": "Midday Real-Time Breaking News", "type": "news"},
    {"slot": "slot_3_afternoon_news", "pkt_hour": 14, "theme": "Afternoon Spot News & City Updates", "type": "news"},
    {"slot": "slot_4_personality", "pkt_hour": 17, "theme": "Gujranwala Popular Personality & Legend Spotlight", "type": "hero"},
    {"slot": "slot_5_evening_news", "pkt_hour": 19, "theme": "Evening Prime News & Administration Updates", "type": "news"},
    {"slot": "slot_6_culture_food", "pkt_hour": 21, "theme": "Gujranwala Food, Heritage & Local Landmarks", "type": "culture"},
    {"slot": "slot_7_night_news", "pkt_hour": 22, "theme": "Night Wrap & Breaking News Alert", "type": "news"},
]
