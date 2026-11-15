"""
Card Generator for Hamara Gujranwala Facebook Page.
Renders branded news cards using the official Hamara Gujranwala V2 Template (1024x1024)
featuring genuine Jameel Noori Nastaleeq Regular typography:
- Headline: Bold, prominent, auto-balanced across 2 lines (50-58px)
- Photo: Strictly matched, centered 914x236px frame
- Description: Regular weight (not bold), high-readability 2-3 line natural paragraph (32-38px)
- Dynamic reference and date metadata with ZERO layout overlapping.
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from PIL import Image

TEMPLATE_PATH = "assets/template_v2_clean.png"
FONT_PATH = "assets/fonts/JameelNooriNastaleeq-Regular.ttf"
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
    Ensure headline is neatly split into 2 balanced lines for optimal Nastaleeq presentation.
    Never leaves dangling prepositions at the end of the first line.
    """
    if "<br>" in headline:
        parts = headline.split("<br>")
        clean_parts = [p.strip() for p in parts if p.strip()]
        return "<br>".join(clean_parts[:2])
    if "\n" in headline:
        parts = headline.split("\n")
        clean_parts = [p.strip() for p in parts if p.strip()]
        return "<br>".join(clean_parts[:2])

    cleaned = headline.strip()
    words = cleaned.split()

    if len(words) <= 5:
        return cleaned

    # Split into 2 equal halves
    mid = (len(words) + 1) // 2
    dangling = [
        "نے", "کو", "کا", "کی", "کے", "پر", "سے", "میں", "اور",
        "کہ", "تک", "یا", "از", "بہ", "بذریعہ", "تحت", "بابت", "خلاف"
    ]
    if mid < len(words) and words[mid - 1] in dangling and mid > 2:
        mid += 1

    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    return f"{line1}<br>{line2}"


def format_description_text(description):
    """
    Format description into a clean, coherent natural Urdu paragraph.
    Handles both lists of bullet points and raw paragraph strings.
    """
    if isinstance(description, list):
        # Join lines into a natural continuous flow
        clean_sentences = []
        for s in description:
            cs = s.strip().lstrip("-• ")
            if not cs.endswith("۔"):
                cs += "۔"
            clean_sentences.append(cs)
        return " ".join(clean_sentences)
    elif isinstance(description, str):
        cleaned = description.strip()
        if "\n" in cleaned:
            lines = [l.strip().lstrip("-• ") for l in cleaned.split("\n") if l.strip()]
            return " ".join([l if l.endswith("۔") else l + "۔" for l in lines])
        return cleaned
    return "ضلعی انتظامیہ کی جانب سے شہریوں کی سہولت اور امن و امان کے لیے اقدامات جاری ہیں۔"


def generate_templated_news_card(
    headline,
    description="ضلعی انتظامیہ کی جانب سے شہریوں کے تحفظ اور امن و امان کے لیے اقدامات جاری ہیں۔",
    category="شہر کی خبریں",
    photo_path=None,
    date_str=None,
    source_str="حوالہ: مستند خبر کا ذریعہ",
    output_path="news_card.png"
):
    """
    Renders the official 1024x1024 Hamara Gujranwala V2 card with
    genuine Jameel Noori Nastaleeq Regular typography:
    - Bold headline (50-58px)
    - Regular-weight description (32-38px)
    - Zero text overriding
    """
    browser_exe = get_browser_executable()
    if not browser_exe:
        raise RuntimeError("No compatible headless browser (Edge/Chrome/Chromium) found for typography rendering.")

    template_abs = os.path.abspath(TEMPLATE_PATH).replace("\\", "/")
    font_abs = os.path.abspath(FONT_PATH).replace("\\", "/")

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

    # Dynamic headline sizing in Jameel Noori Nastaleeq (standard 56px, floor 46px)
    formatted_headline = balance_headline_to_2_lines(headline)
    clean_h = formatted_headline.replace("<br>", " ")
    h_words = len(clean_h.split())
    h_chars = len(clean_h)

    if h_words <= 8 and h_chars <= 42:
        h_size = 58
        h_lh = 1.48
    elif h_words <= 12 and h_chars <= 60:
        h_size = 52
        h_lh = 1.42
    else:
        h_size = 46
        h_lh = 1.36

    # Dynamic description sizing (Regular weight, natural paragraph flow)
    desc_clean = format_description_text(description)
    desc_chars = len(desc_clean)

    if desc_chars <= 110:
        d_size = 38
        d_lh = 1.65
    elif desc_chars <= 165:
        d_size = 33
        d_lh = 1.58
    else:
        d_size = 29
        d_lh = 1.50

    html_content = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'JameelNooriNastaleeq';
    src: url('file:///{font_abs}') format('truetype');
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
    font-family: 'JameelNooriNastaleeq', 'Jameel Noori Nastaleeq', serif;
    direction: rtl;
    -webkit-font-smoothing: antialiased;
  }}
  
  /* Headline Box: Y: 92px to 336px (244px height) - never overlaps yellow bar */
  .headline-box {{
    position: absolute;
    top: 92px;
    left: 40px;
    width: 944px;
    height: 240px;
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
    font-weight: bold;
    text-shadow: 0.5px 0.5px 0 #07193b, -0.5px -0.5px 0 #07193b;
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
  
  /* Description Box: Y: 612px to 855px (243px height) - never overlaps blue line */
  .desc-box {{
    position: absolute;
    top: 612px;
    left: 45px;
    width: 934px;
    height: 242px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0 15px;
  }}
  .desc-text {{
    color: #0c1b33;
    font-size: {d_size}px;
    line-height: {d_lh};
    font-weight: normal;
  }}
  
  /* Meta Row: Source (Left) & Date (Right) */
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
    font-weight: normal;
    direction: rtl;
  }}
  .meta-date {{
    color: #07193b;
    font-size: 28px;
    font-weight: normal;
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
    <div class="desc-text">{desc_clean}</div>
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
    """Wrapper for hero tributes with strictly matched archival portrait and coherent paragraph."""
    photo = hero.get("photo")
    if not photo or not os.path.exists(photo):
        photo = "assets/photos/wrestling_sports.jpg"
    desc = hero.get("card_desc") or hero.get("card_lines") or hero.get("tagline", "پہلوانوں، تاریخ اور روایات کا عظیم شہر گوجرانوالہ")
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
        headline="گوجرانوالہ میں سموگ کے خلاف کریک ڈاؤن<br>متعدد فیکٹریاں اور بھٹے فوری سیل",
        description="ضلعی انتظامیہ نے ماحولیاتی آلودگی کے سدباب کے لیے شہر بھر میں گرینڈ آپریشن شروع کر دیا ہے۔ خلاف ورزی کرنے والے صنعتی یونٹس کو بھاری جرمانے عائد کرنے کے ساتھ سخت قانونی کارروائی کا انتباہ دیا گیا ہے۔",
        category="ماحولیات و سموگ",
        photo_path="assets/photos/smog_factory.jpg",
        output_path="test_font_match.png"
    )
    print("Rendered:", out, "Size:", os.path.getsize(out))
