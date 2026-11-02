"""
Card Generator for Hamara Gujranwala Facebook Page.
Renders branded news cards using the official Hamara Gujranwala Template (1024x1024)
and genuine Jameel Noori Nastaleeq Kasheeda calligraphy font.
"""

import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "assets/template.jpg"
FONT_PATH = "assets/fonts/Jameel_Noori_Nastaleeq_Kasheeda.ttf"
DEFAULT_PHOTO = "assets/sample_news_photo.jpg"

CREAM_BG = (251, 248, 233)
DARK_GREEN = (6, 44, 26)
PILL_GREEN = (42, 71, 53)
GOLD_TEXT = (250, 204, 21)
GOLD_BORDER = (202, 138, 4)
DESC_TEXT = (35, 45, 55)


def urdu(text):
    """Reshape and reorder Urdu text for correct RTL Nastaleeq rendering."""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def wrap_urdu_lines(text, max_words=7):
    """Split long Urdu text into balanced lines for headlines."""
    words = text.strip().split()
    if len(words) <= max_words:
        return [text]
    
    mid = len(words) // 2
    # Adjust break point
    line1 = " ".join(words[:mid + (len(words) % 2)])
    line2 = " ".join(words[mid + (len(words) % 2):])
    return [line1, line2]


def generate_templated_news_card(
    headline,
    description,
    category="بریکنگ نیوز",
    photo_path=None,
    date_str=None,
    source_str="حوالہ: گوجرانوالہ پیج / ذرائع",
    output_path="news_card.png"
):
    """
    Renders an official, beautifully styled Hamara Gujranwala news card
    using the official 1024x1024 template and Jameel Noori Nastaleeq Kasheeda.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template image missing at {TEMPLATE_PATH}")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Load Jameel Noori Nastaleeq Kasheeda font
    if os.path.exists(FONT_PATH):
        font_cat = ImageFont.truetype(FONT_PATH, 24)
        font_hl = ImageFont.truetype(FONT_PATH, 40)
        font_desc = ImageFont.truetype(FONT_PATH, 28)
        font_meta = ImageFont.truetype(FONT_PATH, 22)
    else:
        # Fallback to default
        font_cat = font_hl = font_desc = font_meta = ImageFont.load_default()

    # 1. Category Pill
    draw.rectangle([(405, 168), (620, 198)], fill=PILL_GREEN)
    cat_t = urdu(category)
    bbox = font_cat.getbbox(cat_t)
    tw = bbox[2] - bbox[0]
    draw.text((512 - tw // 2, 164), cat_t, font=font_cat, fill=GOLD_TEXT)

    # 2. News Photo inside Green Arch Frame
    img_to_use = photo_path if (photo_path and os.path.exists(photo_path)) else DEFAULT_PHOTO
    if os.path.exists(img_to_use):
        try:
            photo = Image.open(img_to_use).convert("RGB")
            target_w, target_h = 580, 315

            # Resize & center crop to target dimensions
            img_ratio = photo.width / photo.height
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                new_h = target_h
                new_w = int(target_h * img_ratio)
            else:
                new_w = target_w
                new_h = int(target_w / img_ratio)
            photo = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            photo = photo.crop((left, top, left + target_w, top + target_h))

            px = (1024 - target_w) // 2
            py = 252

            # Golden border frame
            draw.rectangle([(px - 3, py - 3), (px + target_w + 2, py + target_h + 2)], fill=GOLD_BORDER)
            draw.rectangle([(px - 1, py - 1), (px + target_w, py + target_h)], fill=DARK_GREEN)
            img.paste(photo, (px, py))
        except Exception as e:
            print(f"Notice: Failed to load photo: {e}")

    # 3. Clean Template Placeholders with solid cream background
    draw.rectangle([(75, 615), (949, 818)], fill=CREAM_BG)
    draw.rectangle([(75, 830), (949, 878)], fill=CREAM_BG)
    draw.rectangle([(105, 888), (360, 922)], fill=CREAM_BG)
    draw.rectangle([(710, 888), (950, 922)], fill=CREAM_BG)

    # 4. Draw Headline in Jameel Noori Nastaleeq Kasheeda
    lines = wrap_urdu_lines(headline, max_words=7)
    if len(lines) == 1:
        hl_text = urdu(lines[0])
        b = font_hl.getbbox(hl_text)
        tw = b[2] - b[0]
        draw.text((512 - tw // 2, 675), hl_text, font=font_hl, fill=DARK_GREEN)
    else:
        y_positions = [638, 712]
        for idx, line in enumerate(lines[:2]):
            hl_text = urdu(line)
            b = font_hl.getbbox(hl_text)
            tw = b[2] - b[0]
            draw.text((512 - tw // 2, y_positions[idx]), hl_text, font=font_hl, fill=DARK_GREEN)

    # 5. Draw Description
    if description:
        desc_text = urdu(description)
        b = font_desc.getbbox(desc_text)
        tw = b[2] - b[0]
        draw.text((512 - tw // 2, 836), desc_text, font=font_desc, fill=DESC_TEXT)

    # 6. Draw Date
    if not date_str:
        # Format today's date in Urdu
        months_ur = [
            "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
            "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
        ]
        now = datetime.now()
        date_str = f"{now.day:02d} {months_ur[now.month - 1]} {now.year}ء"

    date_t = urdu(date_str)
    draw.text((115, 891), date_t, font=font_meta, fill=DARK_GREEN)

    # 7. Draw Source
    src_t = urdu(source_str)
    b = font_meta.getbbox(src_t)
    draw.text((935 - (b[2] - b[0]), 891), src_t, font=font_meta, fill=DARK_GREEN)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    img.save(output_path, quality=95)
    return output_path


# Backwards compatibility wrappers
def generate_news_card(title, source_name, category="BREAKING NEWS", output_path="card.png", photo_path=None):
    """Wrapper that routes to the official templated card generator."""
    # Create natural Urdu headline and short description
    desc = "تفصیلات اور تازہ ترین صورتحال جاننے کے لیے ہمارے پیج کو فالو کریں"
    return generate_templated_news_card(
        headline=title,
        description=desc,
        category="اہم خبر",
        photo_path=photo_path,
        source_str=f"حوالہ: {source_name}",
        output_path=output_path
    )


def generate_hero_card(hero, output_path="hero_card.png"):
    """Wrapper for hero tributes using the official template."""
    return generate_templated_news_card(
        headline=f"{hero['name_ur']}: گوجرانوالہ کا تاریخی اعزاز",
        description=hero.get("tagline", "پہلوانوں اور تاریخی ہیروز کا عظیم شہر"),
        category="گوجرانوالہ کا فخر",
        photo_path=None,
        source_str="حوالہ: ہمارا گوجرانوالہ",
        output_path=output_path
    )


if __name__ == "__main__":
    out = generate_templated_news_card(
        headline="گوجرانوالہ میں سموگ اور فضائی آلودگی کے خلاف بڑا ایکشن",
        description="ضلعی انتظامیہ کی جانب سے شہریوں کی صحت اور ماحول کے تحفظ کے لیے سخت احکامات جاری",
        category="اہم خبر",
        output_path="test_templated_card.png"
    )
    print("Generated:", out)
