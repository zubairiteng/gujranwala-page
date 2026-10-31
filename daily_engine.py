"""
Main Autonomous Execution Engine for Hamara Gujranwala Facebook Page.
Executes scheduled posting slots (News, Heroes, Heritage, Food & Community Discussions),
generates branded image cards, calls Facebook Graph API, and logs growth progress.
"""

import argparse
import datetime
import json
import os
import sys

# Ensure UTF-8 output encoding across Windows and Linux
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import DAILY_POST_TARGET, PAGE_ID, PAGE_NAME, TARGET_FOLLOWERS
from card_generator import generate_hero_card, generate_news_card
from content_formatter import format_culture_post, format_hero_post, format_news_post
from fb_poster import FacebookPoster
from heroes_bank import get_unposted_hero
from news_aggregator import fetch_gujranwala_news, load_history, save_history

LOGS_DIR = "daily_logs"


def get_pkt_now():
    """Return current datetime in Pakistan Standard Time (UTC+5)."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now + datetime.timedelta(hours=5)


def log_daily_event(action_name, details, post_id=None):
    """Log posting activity into daily markdown logs."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    today_str = get_pkt_now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOGS_DIR, f"{today_str}.md")

    timestamp = get_pkt_now().strftime("%H:%M:%S PKT")
    entry = f"### [{timestamp}] {action_name}\n"
    if post_id:
        entry += f"- **Status**: Published (Post ID: `{post_id}`)\n"
    else:
        entry += "- **Status**: Logged / Simulated\n"
    entry += f"- **Details**: {details}\n\n"

    # Create file with header if not exists
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# Daily Activity Log — {today_str}\n")
            f.write(f"**Page:** {PAGE_NAME} (`{PAGE_ID}`) | **Target:** {TARGET_FOLLOWERS} Followers\n\n")
            f.write("## Published Events\n\n")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


def run_news_post(poster):
    """Fetch verified Gujranwala news, generate card, and publish."""
    print("🔎 Searching for fresh verified Gujranwala news...")
    news_items = fetch_gujranwala_news(limit=1)

    if not news_items:
        print("⚠️ No unposted breaking news found at this moment. Falling back to Hero/Cultural Spotlight.")
        return run_hero_post(poster)

    item = news_items[0]
    print(f"📰 Found News: [{item['source']}] {item['title']}")

    # Generate Image Card
    temp_card = "temp_news_card.png"
    generate_news_card(item["title"], item["source"], category="BREAKING NEWS", output_path=temp_card)

    # Format Caption
    caption = format_news_post(item)

    # Post to Facebook
    res = poster.post_photo(temp_card, caption)

    # Cleanup temp card
    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

    # Save to history
    history = load_history()
    history.setdefault("posted_ids", []).append(item["id"])
    history.setdefault("posted_urls", []).append(item["link"])
    save_history(history)

    log_daily_event(
        "Breaking News Post",
        f"**Headline:** {item['title']}<br>**Source:** {item['source']}",
        post_id=res.get("post_id") or res.get("id")
    )
    return res


def run_hero_post(poster):
    """Select a Gujranwala hero, generate card, and publish tribute."""
    print("🌟 Selecting Gujranwala hero/legend tribute...")
    history = load_history()
    posted_heroes = set(history.get("posted_heroes", []))

    hero = get_unposted_hero(posted_heroes)
    print(f"🏆 Selected Hero: {hero['name_ur']} ({hero['name_en']})")

    # Generate Image Card
    temp_card = "temp_hero_card.png"
    generate_hero_card(hero, output_path=temp_card)

    # Format Caption
    caption = format_hero_post(hero)

    # Post to Facebook
    res = poster.post_photo(temp_card, caption)

    # Cleanup temp card
    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

    # Save to history
    history.setdefault("posted_heroes", []).append(hero["id"])
    save_history(history)

    log_daily_event(
        "Hero Spotlight Tribute",
        f"**Hero:** {hero['name_ur']} ({hero['name_en']})<br>**Category:** {hero['category']}",
        post_id=res.get("post_id") or res.get("id")
    )
    return res


def run_culture_post(poster):
    """Publish Gujranwala food/culture discussion post."""
    print("🍲 Preparing Gujranwala food & cultural engagement post...")
    caption = format_culture_post()

    # Generate News/Culture card
    temp_card = "temp_culture_card.png"
    generate_news_card(
        "Gujranwala Food & Cultural Heritage - What is your favorite spot?",
        "Hamara Gujranwala Community",
        category="FOOD & CULTURE",
        output_path=temp_card
    )

    res = poster.post_photo(temp_card, caption)

    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

    log_daily_event(
        "Cultural & Food Engagement Post",
        "Topic: Gujranwala Food spots & discussion question",
        post_id=res.get("post_id") or res.get("id")
    )
    return res


def determine_auto_action():
    """Determine best action based on current Pakistan hour (PKT)."""
    pkt_hour = get_pkt_now().hour
    print(f"🕒 Current Pakistan Time: {get_pkt_now().strftime('%Y-%m-%d %I:%M %p PKT')} (Hour: {pkt_hour})")

    # Morning (7-10 AM PKT): News / Morning Brief
    if 7 <= pkt_hour < 11:
        return "news"
    # Midday (11 AM - 2 PM PKT): Real-time news update
    elif 11 <= pkt_hour < 14:
        return "news"
    # Afternoon (2 PM - 5 PM PKT): Hero tribute & Wrestling pride
    elif 14 <= pkt_hour < 17:
        return "hero"
    # Evening (5 PM - 8 PM PKT): Evening news / city developments
    elif 17 <= pkt_hour < 20:
        return "news"
    # Prime-Time (8 PM - 10 PM PKT): Food & Culture discussion
    elif 20 <= pkt_hour < 22:
        return "culture"
    # Late Night (10 PM+): Community discussion or hero tribute
    else:
        return "hero"


def main():
    parser = argparse.ArgumentParser(description="Hamara Gujranwala Facebook Automation Engine")
    parser.add_argument("--action", choices=["auto", "news", "hero", "culture", "stats"], default="auto",
                        help="Action to execute")
    args = parser.parse_args()

    poster = FacebookPoster()
    action = args.action

    if action == "stats":
        stats = poster.get_page_stats()
        print("Page Statistics:", json.dumps(stats, indent=2))
        return

    if action == "auto":
        action = determine_auto_action()

    print(f"🚀 Executing Action: [{action.upper()}] for Facebook Page '{PAGE_NAME}'...")

    if action == "news":
        res = run_news_post(poster)
    elif action == "hero":
        res = run_hero_post(poster)
    elif action == "culture":
        res = run_culture_post(poster)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

    print("Execution complete:", res)


if __name__ == "__main__":
    main()
