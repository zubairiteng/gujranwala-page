"""
Card Generator for Hamara Gujranwala Facebook Page.
Generates 1080x1080 branded social media news & hero cards using Pillow.
Optimized for high CTR, mobile readability, and viral Facebook sharing.
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


def get_font(size=36, bold=False):
    """
    Load best available font across Windows and Linux (GitHub Actions).
    Falls back gracefully to default PIL font.
    """
    candidate_fonts = [
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "tahoma.ttf",
        "arial.ttf"
    ]
    for path in candidate_fonts:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def wrap_text_to_lines(text, max_chars=40):
    """Wrap long text into manageable lines."""
    return textwrap.wrap(text, width=max_chars)


def generate_news_card(title, source_name, category="BREAKING NEWS", output_path="card.png"):
    """
    Generate a branded breaking news card.
    """
    width = 1080
    height = 1080

    # Rich dark slate background with green gradient
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Top Brand Banner
    draw.rectangle([(0, 0), (width, 140)], fill=(20, 83, 45))  # Deep Pakistani Forest Green
    draw.rectangle([(0, 135), (width, 140)], fill=(234, 179, 8))  # Golden Accent line

    # Brand Title
    font_brand = get_font(42, bold=True)
    font_sub = get_font(24)
    draw.text((50, 30), "HAMARA GUJRANWALA", fill=(255, 255, 255), font=font_brand)
    draw.text((50, 85), "ہمارا گوجرانوالہ • باخبر گوجرانوالہ، بااختیار گوجرانوالہ", fill=(253, 224, 71), font=font_sub)

    # Category Badge (Pill)
    draw.rounded_rectangle([(50, 180), (380, 240)], radius=12, fill=(220, 38, 38))  # Red alert
    font_badge = get_font(26, bold=True)
    draw.text((70, 192), f"🚨 {category.upper()}", fill=(255, 255, 255), font=font_badge)

    # Main News Headline Box
    draw.rounded_rectangle([(50, 270), (width - 50, 850)], radius=20, fill=(30, 41, 59), outline=(51, 65, 85), width=2)

    # News Title Text Wrapping
    lines = wrap_text_to_lines(title, max_chars=36)
    font_title = get_font(44, bold=True)
    y_text = 330
    line_spacing = 65

    for line in lines[:7]:
        draw.text((90, y_text), line, fill=(248, 250, 252), font=font_title)
        y_text += line_spacing

    # Verified Source Badge
    draw.rounded_rectangle([(90, 750), (width - 90, 810)], radius=10, fill=(15, 23, 42))
    font_meta = get_font(26)
    draw.text((115, 765), f"📌 Verified Source: {source_name} | مصدقہ ذریعہ", fill=(148, 163, 184), font=font_meta)

    # Footer CTA Bar
    draw.rectangle([(0, height - 120), (width, height)], fill=(15, 23, 42))
    draw.line([(0, height - 120), (width, height - 120)], fill=(71, 85, 105), width=2)

    font_cta = get_font(28, bold=True)
    draw.text((50, height - 90), "👉 Follow 'Hamara Gujranwala' for real-time local updates!", fill=(250, 204, 21), font=font_cta)
    draw.text((50, height - 50), "fb.com/HamaraGujranwalaOfficial", fill=(148, 163, 184), font=font_sub)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    img.save(output_path, quality=92)
    return output_path


def generate_hero_card(hero, output_path="hero_card.png"):
    """
    Generate a branded Gujranwala hero/heritage tribute card.
    """
    width = 1080
    height = 1080

    # Rich dark royal blue / gold themed card
    img = Image.new("RGB", (width, height), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)

    # Top Brand Header
    draw.rectangle([(0, 0), (width, 140)], fill=(14, 116, 144))  # Rich Teal / Blue
    draw.rectangle([(0, 135), (width, 140)], fill=(250, 204, 21))  # Golden accent

    font_brand = get_font(40, bold=True)
    font_sub = get_font(24)
    draw.text((50, 30), "HAMARA GUJRANWALA | ہمارا گوجرانوالہ", fill=(255, 255, 255), font=font_brand)
    draw.text((50, 85), "گوجرانوالہ کے ہیرو اور قابلِ فخر تاریخی روایات", fill=(253, 224, 71), font=font_sub)

    # Hero Badge Pill
    badge_text = hero.get("badge", "🌟 GUJRANWALA HERO")
    draw.rounded_rectangle([(50, 180), (520, 240)], radius=12, fill=(202, 138, 4))
    font_badge = get_font(26, bold=True)
    draw.text((70, 192), badge_text, fill=(255, 255, 255), font=font_badge)

    # Main Story Card
    draw.rounded_rectangle([(50, 270), (width - 50, 860)], radius=20, fill=(23, 37, 84), outline=(30, 58, 138), width=2)

    # Hero Name English & Urdu
    font_name = get_font(48, bold=True)
    draw.text((90, 320), hero["name_en"], fill=(255, 255, 255), font=font_name)
    
    font_tagline = get_font(32)
    draw.text((90, 390), hero.get("tagline", ""), fill=(253, 224, 71), font=font_tagline)

    # Story Text
    font_body = get_font(30)
    lines = wrap_text_to_lines(hero["story_en"], max_chars=44)
    y_text = 460
    for line in lines[:5]:
        draw.text((90, y_text), line, fill=(226, 232, 240), font=font_body)
        y_text += 46

    # Highlight Pill
    draw.rounded_rectangle([(90, 740), (width - 90, 820)], radius=12, fill=(15, 23, 42))
    font_q = get_font(25, bold=True)
    draw.text((110, 765), "💬 Join the discussion: What makes you proud of Gujranwala?", fill=(250, 204, 21), font=font_q)

    # Bottom Footer
    draw.rectangle([(0, height - 120), (width, height)], fill=(10, 15, 30))
    draw.line([(0, height - 120), (width, height - 120)], fill=(51, 65, 85), width=2)
    font_cta = get_font(28, bold=True)
    draw.text((50, height - 80), "👉 Follow 'Hamara Gujranwala' • The Pride of Punjab", fill=(255, 255, 255), font=font_cta)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    img.save(output_path, quality=92)
    return output_path


if __name__ == "__main__":
    card1 = generate_news_card(
        "Prime suspect in Gujranwala bride murder case apprehended in joint police operation",
        "Dawn News",
        output_path="test_news_card.png"
    )
    print("Generated news card:", card1)
