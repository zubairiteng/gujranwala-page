from urdu_news_engine import craft_urdu_news_package
"""
Main Autonomous Execution Engine for Hamara Gujranwala Facebook Page.
Executes scheduled posting slots using the official Hamara Gujranwala 1024x1024 Template
and genuine Jameel Noori Nastaleeq Kasheeda typography.
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
from card_generator import generate_hero_card, generate_templated_news_card
from content_formatter import format_culture_post, format_hero_post, format_news_post
from fb_poster import FacebookPoster
from heroes_bank import get_unposted_hero
from news_aggregator import fetch_gujranwala_news, load_history, save_history

LOGS_DIR = "daily_logs"


def get_pkt_now():
    """Return current datetime in Pakistan Standard Time (UTC+5)."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now + datetime.timedelta(hours=5)


def get_urdu_date():
    """Return today's date formatted in Urdu."""
    months_ur = [
        "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
        "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
    ]
    now = get_pkt_now()
    return f"{now.day:02d} {months_ur[now.month - 1]} {now.year}ء"


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

    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# Daily Activity Log - {today_str}\n")
            f.write(f"**Page:** {PAGE_NAME} (`{PAGE_ID}`) | **Target:** {TARGET_FOLLOWERS} Followers\n\n")
            f.write("## Published Events\n\n")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


def run_news_post(poster):
    """Fetch verified Gujranwala news, generate card on official template, and publish."""
    print("🔎 Searching for fresh verified Gujranwala news (within 48 hours)...")
    news_items = fetch_gujranwala_news(limit=1)

    if not news_items:
        print("⚠️ No unposted breaking news found in the last 48 hours. Falling back to Hero/Cultural Spotlight.")
        return run_hero_post(poster)

    item = news_items[0]
    print(f"📰 Found Fresh News: [{item['source']}] {item['title']}")

    temp_card = "temp_news_card.png"
    date_str = get_urdu_date()
    source_str = f"حوالہ: گوجرانوالہ پیج / {item['source']}"

    # Generate complete Urdu news package (Urdu headline, description, category, matched photo, and caption)
    pkg = craft_urdu_news_package(item)
    headline = pkg["headline_ur"]
    description = pkg["desc_ur"]
    category = pkg["category_ur"]
    photo_path = pkg["photo_path"]
    caption = pkg["caption"]

    generate_templated_news_card(
        headline=headline,
        description=description,
        category=category,
        photo_path=photo_path,
        date_str=date_str,
        source_str=source_str,
        output_path=temp_card
    )
    res = poster.post_photo(temp_card, caption)

    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

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
    """Select a Gujranwala hero, generate tribute card on official template, and publish."""
    print("🌟 Selecting Gujranwala hero/legend tribute...")
    history = load_history()
    posted_heroes = history.get("posted_heroes", [])

    hero = get_unposted_hero(posted_heroes)
    print(f"🏆 Selected Hero: {hero['name_ur']} ({hero['name_en']})")

    temp_card = "temp_hero_card.png"
    generate_hero_card(hero, output_path=temp_card)

    caption = format_hero_post(hero)
    res = poster.post_photo(temp_card, caption)

    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

    history.setdefault("posted_heroes", []).append(hero["id"])
    save_history(history)

    log_daily_event(
        "Hero Spotlight Tribute",
        f"**Hero:** {hero['name_ur']} ({hero['name_en']})<br>**Category:** {hero['category']}",
        post_id=res.get("post_id") or res.get("id")
    )
    return res


def run_culture_post(poster):
    """Publish Gujranwala food/culture discussion post using official template."""
    print("🍲 Preparing Gujranwala food & cultural engagement post...")
    caption = format_culture_post()

    temp_card = "temp_culture_card.png"
    generate_templated_news_card(
        headline="گوجرانوالہ کے روایتی کھانے اور ثقافتی پہچان",
        description="چراغ کے روایتی کباب و تکے، کھیا علی گیٹ کی لسی اور دال بازار کے چٹپٹے ذائقے، جن کی لذت کے دیوانے پورے ملک سے گوجرانوالہ کا رخ کرتے ہیں",
        category="ذائقہ گوجرانوالہ کا",
        photo_path="assets/photos/food_heritage.jpg",
        date_str=get_urdu_date(),
        source_str="حوالہ: ہمارا گوجرانوالہ",
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


def run_approved_post(poster):
    """Publish the user-approved news post immediately."""
    print("📢 Publishing user-approved Smog Crackdown Post...")
    card_path = "assets/todays_approved_card.png"
    if not os.path.exists(card_path):
        card_path = "news_card.png"
        generate_templated_news_card(
            headline="گوجرانوالہ میں سموگ اور فضائی آلودگی کے خلاف بڑا ایکشن، فیکٹریاں سیل",
            description="ضلعی انتظامیہ کی جانب سے شہریوں کی صحت اور ماحول کے تحفظ کے لیے احکامات جاری",
            category="اہم خبر",
            photo_path="assets/smog_photo_1.jpg",
            date_str="02 نومبر 2026ء",
            source_str="حوالہ: گوجرانوالہ پیج / ایکسپریس نیوز",
            output_path=card_path
        )

    caption = """🚨 گوجرانوالہ اہم خبر | تازہ ترین اپڈیٹ
━━━━━━━━━━━━━━━━━━━━

📢 گوجرانوالہ میں سموگ اور فضائی آلودگی کے خلاف بڑا ایکشن، متعدد بھٹے اور فیکٹریاں سیل

تفصیلات کے مطابق:
گوجرانوالہ اور گردونواح میں ماحولیاتی تحفظ اور سموگ کے تدارک کے لیے ضلعی انتظامیہ اور محکمہ تحفظِ ماحول کی جانب سے گرینڈ آپریشن شروع کر دیا گیا ہے۔ حکومتی احکامات کی خلاف ورزی کرنے والے صنعتی یونٹس، بھٹوں اور دھواں چھوڑنے والی گاڑیوں کے خلاف بلا امتیاز کارروائیاں جاری ہیں۔

📌 مصدقہ حوالہ: گوجرانوالہ پیج / ایکسپریس نیوز
🗓️ تاریخ: 02 نومبر 2026ء

⚠️ شہریوں سے گزارش ہے کہ سموگ سے بچاؤ کے لیے حفاظتی تدابیر اختیار کریں اور ماحولیاتی ضوابط کی پاسداری کریں۔

💬 گوجرانوالہ کے شہریوں کی انتظامیہ کے اس اقدام کے بارے میں کیا رائے ہے؟ کمنٹس میں ضرور بتائیں۔

━━━━━━━━━━━━━━━━━━━━
👉 گوجرانوالہ کی ہر گلی، ہر چوک اور ہر لمحے کی سچی خبر سب سے پہلے حاصل کرنے کے لیے ہمارے پیج 'Hamara Gujranwala' کو لائک اور فالو کریں!

#HamaraGujranwala #GujranwalaNews #Gujranwala #گوجرانوالہ #گوجرانوالہ_اپڈیٹس #SmogUpdate #HamaraGujranwalaOfficial"""

    res = poster.post_photo(card_path, caption)
    log_daily_event(
        "User-Approved News Post",
        "Topic: Smog and Air Pollution Crackdown in Gujranwala",
        post_id=res.get("post_id") or res.get("id")
    )
    return res


def determine_auto_action():
    """Determine best action based on current Pakistan hour (PKT)."""
    pkt_hour = get_pkt_now().hour
    print(f"🕒 Current Pakistan Time: {get_pkt_now().strftime('%Y-%m-%d %I:%M %p PKT')} (Hour: {pkt_hour})")

    if 7 <= pkt_hour < 11:
        return "news"       # Morning News & Weather
    elif 11 <= pkt_hour < 14:
        return "news"       # Midday Real-Time News
    elif 14 <= pkt_hour < 16:
        return "hero"       # Afternoon Gujranwala Legends
    elif 16 <= pkt_hour < 19:
        return "news"       # Late Afternoon / Spot News
    elif 19 <= pkt_hour < 21:
        return "culture"    # Prime Food & Heritage
    elif 21 <= pkt_hour < 23:
        return "news"       # Night News Wrap
    else:
        return "hero"


def main():
    parser = argparse.ArgumentParser(description="Hamara Gujranwala Facebook Automation Engine")
    parser.add_argument("--action", choices=["auto", "approved", "news", "hero", "culture", "stats"], default="auto",
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

    if action == "approved":
        res = run_approved_post(poster)
    elif action == "news":
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
