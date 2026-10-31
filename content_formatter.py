"""
Content Formatter for Hamara Gujranwala Facebook Page.
Transforms raw news items and hero profiles into high-engagement,
culturally resonant Facebook posts with proper attribution and follow-CTAs.
"""

from datetime import datetime


def format_news_post(news_item):
    """
    Format a verified Gujranwala news post with clear Urdu hook,
    factual summary, source attribution, discussion question, and CTAs.
    """
    title = news_item.get("title", "")
    source = news_item.get("source", "Verified News")
    link = news_item.get("link", "")
    
    caption = (
        f"🚨 بریکنگ نیوز | اہم گوجرانوالہ اپڈیٹ\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📢 {title}\n\n"
        f"گوجرانوالہ اور گردونواح کے لیے اہم اور تازہ ترین خبر۔\n\n"
        f"📌 باضابطہ اور تصدیق شدہ ذریعہ: {source}\n"
        f"🔗 تفصیلی رپورٹ: {link}\n\n"
        f"⚠️ قارئین سے التماس ہے کہ غیر مصدقہ افواہوں سے گریز کریں اور ہمیشہ مصدقہ ذرائع سے باخبر رہیں۔\n\n"
        f"💬 گوجرانوالہ کے شہریوں کی اس بارے میں کیا رائے ہے؟ کمنٹس میں اپنے خیالات کا اظہار ضرور کریں۔\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 گوجرانوالہ کی ہر گلی، ہر چوک اور ہر لمحے کی سچی خبر سب سے پہلے حاصل کرنے کے لیے ہمارے پیج 'Hamara Gujranwala' کو لائک اور فالو کریں!\n\n"
        f"#HamaraGujranwala #Gujranwala #GujranwalaNews #گوجرانوالہ #CityOfWrestlers #PakistanNews"
    )
    return caption


def format_hero_post(hero_item):
    """
    Format a Gujranwala hero/heritage post celebrating the city's icons,
    wrestlers, literary figures, and landmarks.
    """
    name_ur = hero_item.get("name_ur", "")
    name_en = hero_item.get("name_en", "")
    badge = hero_item.get("badge", "🌟 گوجرانوالہ کا فخر")
    tagline = hero_item.get("tagline", "")
    story_ur = hero_item.get("story_ur", "")
    story_en = hero_item.get("story_en", "")
    question = hero_item.get("engagement_question", "آپ کا اس بارے میں کیا خیال ہے؟")
    hashtags = " ".join(hero_item.get("hashtags", ["#HamaraGujranwala", "#Gujranwala"]))

    caption = (
        f"{badge}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏆 {name_ur} ({name_en})\n"
        f"✨ {tagline}\n\n"
        f"{story_ur}\n\n"
        f"📖 English Brief:\n"
        f"{story_en}\n\n"
        f"💬 آپ سے سوال:\n"
        f"{question}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❤️ گوجرانوالہ کی عظیم تاریخ، پہلوانی کی روایات اور کھانوں کی پہچان کو زندہ رکھنے کے لیے پیج 'Hamara Gujranwala' کو فالو کریں اور یہ پوسٹ اپنے دوستوں کے ساتھ شیئر کریں!\n\n"
        f"{hashtags}"
    )
    return caption


def format_culture_post(topic="food"):
    """
    Format a culture, food, or civic discussion post for high engagement.
    """
    caption = (
        f"🍲 زندہ دلانِ گوجرانوالہ | ذائقوں اور روایات کا شہر\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"کہتے ہیں کہ جو شخص گوجرانوالہ آئے اور یہاں کا ناشتہ، چراغ کے تکے، کھیا علی گیٹ کی لسی "
        f"یا دال بازار کی مچھلی نہ کھائے، اس کا سفر ادھورا ہے۔\n\n"
        f"گوجرانوالہ کے باسی نہ صرف پہلوانی اور صنعت میں دنیا بھر میں اپنا لوہا منوا چکے ہیں، "
        f"بلکہ مہمان نوازی اور لذیذ کھانوں میں بھی ان کا کوئی ثانی نہیں۔\n\n"
        f"💬 آج کا دلچسپ سوال:\n"
        f"آپ کے خیال میں گوجرانوالہ کی سب سے لذیذ اور سدا بہار فوڈ ڈش کون سی ہے؟ اور آپ کا پسندیدہ فوڈ سپاٹ کون سا ہے؟ کمنٹس میں نام بتائیں!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 گوجرانوالہ کے باسیوں کے اپنے پیج 'Hamara Gujranwala' کو فالو کریں۔\n\n"
        f"#HamaraGujranwala #GujranwalaFood #CityOfWrestlers #ChiraghTikka #گوجرانوالہ"
    )
    return caption
