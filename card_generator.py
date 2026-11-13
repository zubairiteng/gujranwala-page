"""
Card Generator for Hamara Gujranwala Facebook Page.
Renders branded news cards using the official Hamara Gujranwala V2 Template (1024x1024)
featuring large, high-readability typography in Noto Sans Arabic (ExtraBold / Bold),
a centered 914x254 photo frame, 3 structured bullet description lines,
and dynamic reference & date metadata.
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from PIL import Image

TEMPLATE_PATH = "assets/template_v2_clean.png"
FONT_PATH = "assets/fonts/NotoSansArabic-Variable.ttf"
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
    clean_lines = clean_lines[:3]
    return clean_lines


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
    enlarged, crystal-clear Noto Sans Arabic ExtraBold typography.
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

    # Dynamic headline sizing for optimal fill and zero clipping
    words = len(headline.split())
    if words > 14:
        h_size = 48
    elif words > 10:
        h_size = 52
    else:
        h_size = 56

    # Format 2 to 3 bullet description lines
    lines = format_description_to_bullet_lines(description)
    desc_html = "".join([f'<div class="desc-line">- {l}</div>' for l in lines])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'UrduNewsFont';
    src: url('file:///{font_abs}');
    font-weight: 100 900;
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
    font-family: 'UrduNewsFont', 'Segoe UI', Tahoma, sans-serif;
    direction: rtl;
    -webkit-font-smoothing: antialiased;
  }}
  
  /* Top Headline Box: Huge, bold, centered in navy blue matching user template */
  .headline-box {{
    position: absolute;
    top: 96px;
    left: 45px;
    width: 934px;
    height: 236px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0 25px;
  }}
  .headline {{
    color: #07193b;
    font-size: {h_size}px;
    line-height: 1.34;
    font-weight: 800;
    text-shadow: 0 1px 1px rgba(0,0,0,0.06);
  }}
  
  /* Center Photo Frame: 914 x 254 px */
  .photo-frame {{
    position: absolute;
    top: 366px;
    left: 55px;
    width: 914px;
    height: 254px;
    border-radius: 6px;
    overflow: hidden;
    background: #07193b;
  }}
  .photo-frame img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  
  /* Description Area: 2-3 readable bullet lines in 28px SemiBold */
  .desc-box {{
    position: absolute;
    top: 636px;
    left: 50px;
    width: 924px;
    height: 216px;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;
    text-align: center;
    padding: 0 10px;
  }}
  .desc-line {{
    color: #0c1b33;
    font-size: 28px;
    line-height: 1.55;
    font-weight: 600;
  }}
  
  /* Meta Row: Source (Left) & Date (Right) above bottom bar */
  .meta-bar {{
    position: absolute;
    top: 864px;
    left: 55px;
    width: 914px;
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    direction: ltr;
  }}
  .meta-source {{
    color: #07193b;
    font-size: 26px;
    font-weight: 700;
    direction: rtl;
  }}
  .meta-date {{
    color: #07193b;
    font-size: 26px;
    font-weight: 700;
    direction: rtl;
  }}
</style>
</head>
<body>
  <div class="headline-box">
    <div class="headline">{headline}</div>
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
    """Wrapper for hero tributes with strictly matched archival portrait and 2-3 line context."""
    photo = hero.get("photo")
    if not photo or not os.path.exists(photo):
        photo = "assets/photos/wrestling_sports.jpg"
    desc = hero.get("card_lines") or hero.get("card_desc") or hero.get("tagline", "پہلوانوں، تاریخ اور روایات کا عظیم شہر گوجرانوالہ")
    return generate_templated_news_card(
        headline=f"{hero['name_ur']}: گوجرانوالہ کا تاریخی فخر",
        description=desc,
        category="گوجرانوالہ کا فخر",
        photo_path=photo,
        source_str="حوالہ: ہمارا گوجرانوالہ",
        output_path=output_path
    )


if __name__ == "__main__":
    out = generate_templated_news_card(
        headline="گوجرانوالہ کی اہم خبر، تفصیلات ایک نظر میں",
        description=[
            "یہاں خبر کی پہلی اہم تفصیل درج کریں۔",
            "دوسری سطر میں ضروری پس منظر واضح کریں۔",
            "تیسری سطر میں اہم نتیجہ یا اگلا قدم لکھیں۔"
        ],
        category="شہر کی خبریں",
        output_path="test_font_match.png"
    )
    print("Rendered:", out, "Size:", os.path.getsize(out))
