"""
Card Generator for Hamara Gujranwala Facebook Page.
Renders branded news cards using the official Hamara Gujranwala V2 Template (1024x1024)
featuring genuine Noto Naskh Arabic Bold typography,
balanced 2-line headlines (standard 80px, floor 72px),
a centered 914x236 photo frame, 3 structured bullet description lines (standard 50px, floor 42px),
and dynamic reference & date metadata.
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from PIL import Image

TEMPLATE_PATH = "assets/template_v2_clean.png"
FONT_BOLD = "assets/fonts/NotoNaskhArabic-Bold.ttf"
FONT_SEMIBOLD = "assets/fonts/NotoNaskhArabic-SemiBold.ttf"
FONT_REGULAR = "assets/fonts/NotoNaskhArabic-Regular.ttf"
DEFAULT_PHOTO = "assets/photos/civic_city.jpg"


def get_browser_executable():
    """Locate headless Chrome / Edge / Chromium across Windows and Linux."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def get_urdu_date(dt=None):
    """Format date into standard Urdu string."""
    months_ur = [
        "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
        "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
    ]
    d = dt or datetime.now()
    return f"{d.day:02d} {months_ur[d.month - 1]} {d.year}ء"


def balance_headline_to_2_lines(headline):
    """
    Ensure headline is neatly split into 2 balanced lines for optimal 72-80px presentation.
    Never leaves dangling prepositions at the end of the first line.
    """
    if "<br>" in headline or "\n" in headline:
        parts = headline.replace("\n", "<br>").split("<br>")
        clean_parts = [p.strip() for p in parts if p.strip()]
        return "<br>".join(clean_parts[:2])

    cleaned = headline.strip()
    words = cleaned.split()

    if len(words) <= 5:
        if len(cleaned) <= 24:
            return cleaned
        mid = len(words) // 2
        return " ".join(words[:mid]) + "<br>" + " ".join(words[mid:])

    # Split into 2 equal halves
    mid = (len(words) + 1) // 2
    dangling = ["نے", "کو", "کا", "کی", "کے", "پر", "سے", "میں", "اور", "کہ", "تک"]
    if mid < len(words) and words[mid - 1] in dangling and mid > 2:
        mid += 1

    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    return f"{line1}<br>{line2}"


def format_description_to_bullet_lines(description):
    """
    Convert raw description string or list into exactly 2 to 3
    high-impact, bulleted Urdu lines matching the user's template.
    """
    if isinstance(description, list):
        clean_lines = [line.strip().lstrip("-• ") for line in description if line.strip()]
    elif isinstance(description, str):
        if "\n" in description:
            clean_lines = [l.strip().lstrip("-• ") for l in description.split("\n") if l.strip()]
        elif "۔" in description:
            clean_lines = [s.strip().lstrip("-• ") + "۔" for s in description.split("۔") if s.strip()]
        elif "،" in description and len(description.split("،")) >= 3:
            clean_lines = [p.strip().lstrip("-• ") for p in description.split("،") if p.strip()]
        else:
            clean_lines = [description.strip().lstrip("-• ")]
    else:
        clean_lines = ["ضلعی انتظامیہ کی جانب سے شہریوں کی سہولت اور امن و امان کے لیے اقدامات جاری۔"]

    # Keep at most 3 clear lines
    return clean_lines[:3]


def generate_templated_news_card(
    headline,
    description="ضلعی انتظامیہ کی جانب سے شہریوں کے تحفظ اور امن و امان کے لیے اقدامات جاری۔",
    category="شہر کی خبریں",
    photo_path=None,
    date_str=None,
    source_str="حوالہ: مستند خبر کا ذریعہ",
    output_path="news_card.png"
):
    """
    Renders the official 1024x1024 Hamara Gujranwala V2 card with
    Noto Naskh Arabic Bold typography, 72-80px headline, and 42-50px description.
    """
    browser_exe = get_browser_executable()
    if not browser_exe:
        raise RuntimeError("No compatible headless browser (Edge/Chrome/Chromium) found for typography rendering.")

    template_abs = os.path.abspath(TEMPLATE_PATH).replace("\\", "/")
    font_bold_abs = os.path.abspath(FONT_BOLD).replace("\\", "/")
    font_semi_abs = os.path.abspath(FONT_SEMIBOLD).replace("\\", "/")
    font_reg_abs = os.path.abspath(FONT_REGULAR).replace("\\", "/")

    photo_to_use = photo_path if (photo_path and os.path.exists(photo_path)) else DEFAULT_PHOTO
    photo_abs = os.path.abspath(photo_to_use).replace("\\", "/")

    if not date_str:
        date_str = f"تاریخ: {get_urdu_date()}"
    elif not date_str.startswith("تاریخ:"):
        date_str = f"تاریخ: {date_str.lstrip('🗓️ ')}"

    if not source_str:
        source_str = "حوالہ: مستند خبر کا ذریعہ"
    elif not source_str.startswith("حوالہ:"):
        source_str = f"حوالہ: {source_str.lstrip('📷 ')}"

    # Dynamic headline sizing strictly within user's rule: standard 80px, floor 72px
    formatted_headline = balance_headline_to_2_lines(headline)
    h_lines = formatted_headline.split("<br>")
    max_h_words = max(len(l.split()) for l in h_lines)
    max_h_chars = max(len(l) for l in h_lines)

    if max_h_words <= 4 and max_h_chars <= 24 and len(h_lines) <= 2:
        h_size = 80
        h_lh = 1.25
    elif max_h_words <= 6 and max_h_chars <= 34 and len(h_lines) <= 2:
        h_size = 76
        h_lh = 1.20
    else:
        h_size = 72
        h_lh = 1.18

    # Format 2 to 3 bullet description lines strictly within user's rule: standard 50px, floor 42px
    lines = format_description_to_bullet_lines(description)
    clean_lines = [l.strip().lstrip("-• ") for l in lines]
    max_desc_chars = max(len(l) for l in clean_lines) if clean_lines else 0

    if max_desc_chars <= 36:
        desc_size = 50
        desc_lh = 1.34
    elif max_desc_chars <= 44:
        desc_size = 46
        desc_lh = 1.30
    else:
        desc_size = 42
        desc_lh = 1.26

    desc_html = "\n".join([f'    <div class="desc-line">- {l}</div>' for l in clean_lines])

    html_content = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'Noto Naskh Arabic Bold';
    src: url('file:///{font_bold_abs}') format('truetype');
    font-weight: 700;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'Noto Naskh Arabic Bold';
    src: url('file:///{font_semi_abs}') format('truetype');
    font-weight: 600;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'Noto Naskh Arabic Bold';
    src: url('file:///{font_reg_abs}') format('truetype');
    font-weight: 400;
    font-style: normal;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    width: 1024px;
    height: 1024px;
    overflow: hidden;
    position: relative;
    background-image: url('file:///{template_abs}');
    background-size: 1024px 1024px;
    font-family: 'Noto Naskh Arabic Bold', 'Noto Naskh Arabic', serif;
    direction: rtl;
    -webkit-font-smoothing: antialiased;
  }}
  
  /* Top Headline Box: Bold centered in deep navy blue (#07193b) matching user template */
  .headline-box {{
    position: absolute;
    top: 92px;
    left: 35px;
    width: 954px;
    height: 236px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0 10px;
  }}
  .headline {{
    color: #07193b;
    font-size: {h_size}px;
    line-height: {h_lh};
    font-weight: 700;
    text-shadow: 0 1px 1px rgba(0,0,0,0.06);
  }}
  
  /* Center Photo Frame: 914 x 236 px */
  .photo-frame {{
    position: absolute;
    top: 360px;
    left: 55px;
    width: 914px;
    height: 236px;
    border-radius: 6px;
    overflow: hidden;
    background: #07193b;
  }}
  .photo-frame img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  
  /* Description Area: 3 readable bullet lines in 42-50px Bold */
  .desc-box {{
    position: absolute;
    top: 606px;
    left: 35px;
    width: 954px;
    height: 244px;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;
    text-align: center;
    padding: 0 10px;
  }}
  .desc-line {{
    color: #0c1b33;
    font-size: {desc_size}px;
    line-height: {desc_lh};
    font-weight: 700;
    text-align: center;
  }}
  
  /* Meta Row: Source (Left) & Date (Right) above bottom bar */
  .meta-bar {{
    position: absolute;
    top: 864px;
    left: 55px;
    width: 914px;
    height: 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    direction: ltr;
  }}
  .meta-source {{
    color: #07193b;
    font-size: 28px;
    font-weight: 700;
    direction: rtl;
  }}
  .meta-date {{
    color: #07193b;
    font-size: 28px;
    font-weight: 700;
    direction: rtl;
  }}
</style>
</head>
<body>
  <div class="headline-box">
    <div class="headline">{formatted_headline}</div>
  </div>
  <div class="photo-frame">
    <img src="file:///{photo_abs}">
  </div>
  <div class="desc-box">
{desc_html}
  </div>
  <div class="meta-bar">
    <div class="meta-source">{source_str}</div>
    <div class="meta-date">{date_str}</div>
  </div>
</body>
</html>"""

    temp_html = "temp_render_v2_card.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_html = os.path.abspath(temp_html).replace("\\", "/")
    abs_out = os.path.abspath(output_path).replace("\\", "/")

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        f"--screenshot={abs_out}",
        "--window-size=1024,1024",
        "--hide-scrollbars",
        f"file:///{abs_html}"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    finally:
        if os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except Exception:
                pass

    if not os.path.exists(output_path):
        raise RuntimeError(f"Card rendering failed to produce {output_path}")

    return output_path


def generate_news_card(title, source_name, category="شہر کی خبریں", output_path="card.png", photo_path=None, description="ضلعی انتظامیہ کی جانب سے شہریوں کی سہولت اور امن و امان کے لیے اقدامات جاری۔"):
    """Wrapper routing to templated card generator."""
    if not photo_path or not os.path.exists(photo_path):
        photo_path = "assets/photos/civic_city.jpg"
    return generate_templated_news_card(
        headline=title,
        description=description,
        category=category,
        photo_path=photo_path,
        source_str=f"حوالہ: گوجرانوالہ پیج / {source_name}",
        output_path=output_path
    )


def generate_hero_card(hero, output_path="hero_card.png"):
    """Wrapper for hero tributes with strictly matched archival portrait and 3-line context."""
    photo = hero.get("photo")
    if not photo or not os.path.exists(photo):
        photo = "assets/photos/wrestling_sports.jpg"
    desc = hero.get("card_lines") or hero.get("card_desc") or hero.get("tagline", "پہلوانوں، تاریخ اور روایات کا عظیم شہر گوجرانوالہ")
    return generate_templated_news_card(
        headline=f"{hero['name_ur']}<br>گوجرانوالہ کا تاریخی فخر",
        description=desc,
        category="گوجرانوالہ کا فخر",
        photo_path=photo,
        source_str="حوالہ: ہمارا گوجرانوالہ",
        output_path=output_path
    )


if __name__ == "__main__":
    out = generate_templated_news_card(
        headline="گوجرانوالہ کی اہم خبر\nتفصیلات ایک نظر میں",
        description=[
            "یہاں خبر کی پہلی اہم تفصیل درج کریں۔",
            "دوسری سطر میں ضروری پس منظر واضح کریں۔",
            "تیسری سطر میں اہم نتیجہ یا اگلا قدم لکھیں۔"
        ],
        category="شہر کی خبریں",
        output_path="test_font_match.png"
    )
    print("Rendered:", out, "Size:", os.path.getsize(out))
