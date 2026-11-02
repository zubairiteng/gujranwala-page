"""
Card Generator for Hamara Gujranwala Facebook Page.
Renders branded news cards using the official Hamara Gujranwala Template (1024x1024)
and genuine Jameel Noori Nastaleeq Kasheeda typography via headless browser engine.
"""

import os
import shutil
import subprocess
from datetime import datetime
from PIL import Image

TEMPLATE_PATH = "assets/template.jpg"
FONT_PATH = "assets/fonts/Jameel_Noori_Nastaleeq_Kasheeda.ttf"
DEFAULT_PHOTO = "assets/sample_news_photo.jpg"


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


def generate_templated_news_card(
    headline,
    description="ضلعی انتظامیہ کی جانب سے شہریوں کے تحفظ اور امن و امان کے لیے اقدامات جاری",
    category="اہم خبر",
    photo_path=None,
    date_str=None,
    source_str="حوالہ: گوجرانوالہ پیج / ذرائع",
    output_path="news_card.png"
):
    """
    Renders the official 1024x1024 news card with exact typography
    in Jameel Noori Nastaleeq Kasheeda.
    """
    browser_exe = get_browser_executable()
    if not browser_exe:
        raise RuntimeError("No compatible headless browser (Edge/Chrome/Chromium) found for Nastaleeq rendering.")

    template_abs = os.path.abspath(TEMPLATE_PATH).replace("\\", "/")
    font_abs = os.path.abspath(FONT_PATH).replace("\\", "/")
    
    photo_to_use = photo_path if (photo_path and os.path.exists(photo_path)) else DEFAULT_PHOTO
    photo_abs = os.path.abspath(photo_to_use).replace("\\", "/")

    if not date_str:
        now = datetime.now()
        date_str = f"🗓️ {now.day:02d} {now.strftime('%b %Y')}"
    elif not date_str.startswith("🗓️"):
        date_str = f"🗓️ {date_str}"

    if not source_str.startswith("📷"):
        source_str = f"📷 {source_str}"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
  @font-face {{
    font-family: 'JameelKasheeda';
    src: url('file:///{font_abs}');
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
    font-family: 'JameelKasheeda', 'Noto Nastaliq Urdu', 'Segoe UI', Tahoma, sans-serif;
    direction: rtl;
    -webkit-font-smoothing: antialiased;
  }}
  /* Category Pill */
  .category-pill {{
    position: absolute;
    top: 168px;
    left: 405px;
    width: 214px;
    height: 30px;
    background: #2a4735;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fde047;
    font-size: 24px;
    line-height: 30px;
    text-align: center;
    padding-bottom: 4px;
  }}
  /* Photo Frame in Green Arch */
  .photo-frame {{
    position: absolute;
    top: 250px;
    left: 222px;
    width: 580px;
    height: 315px;
    border: 3px solid #ca8a04;
    border-radius: 8px;
    overflow: hidden;
    background: #062c1a;
  }}
  .photo-frame img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  /* Headline Area */
  .text-cover {{
    position: absolute;
    top: 618px;
    left: 75px;
    width: 874px;
    height: 198px;
    background: #fbf8e9;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0 25px;
  }}
  .headline {{
    color: #062c1a;
    font-size: 46px;
    line-height: 1.45;
    font-weight: bold;
    text-shadow: 0 1px 1px rgba(0,0,0,0.05);
  }}
  /* Description Area */
  .desc-cover {{
    position: absolute;
    top: 832px;
    left: 75px;
    width: 874px;
    height: 44px;
    background: #fbf8e9;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1e293b;
    font-size: 28px;
    line-height: 36px;
    text-align: center;
    padding: 0 20px;
  }}
  /* Meta Row */
  .meta-date {{
    position: absolute;
    top: 888px;
    left: 75px;
    width: 320px;
    height: 32px;
    background: #fbf8e9;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: #062c1a;
    font-size: 22px;
    direction: ltr;
    padding-left: 35px;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-weight: 600;
  }}
  .meta-source {{
    position: absolute;
    top: 888px;
    right: 75px;
    width: 440px;
    height: 32px;
    background: #fbf8e9;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: #062c1a;
    font-size: 22px;
    direction: rtl;
    padding-right: 35px;
    font-weight: bold;
  }}
</style>
</head>
<body>
  <div class='category-pill'>{category}</div>
  <div class='photo-frame'>
    <img src='file:///{photo_abs}'>
  </div>
  <div class='text-cover'>
    <div class='headline'>{headline}</div>
  </div>
  <div class='desc-cover'>{description}</div>
  <div class='meta-date'>{date_str}</div>
  <div class='meta-source'>{source_str}</div>
</body>
</html>"""

    temp_html = "temp_render_card.html"
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


def generate_news_card(title, source_name, category="اہم خبر", output_path="card.png", photo_path=None):
    """Wrapper routing to templated card generator."""
    return generate_templated_news_card(
        headline=title,
        description="تفصیلات اور تازہ ترین صورتحال کے لیے ہمارے پیج کو فالو کریں",
        category=category,
        photo_path=photo_path,
        source_str=f"ذریعہ: گوجرانوالہ پیج / {source_name}",
        output_path=output_path
    )


def generate_hero_card(hero, output_path="hero_card.png"):
    """Wrapper for hero tributes."""
    return generate_templated_news_card(
        headline=f"{hero['name_ur']}: گوجرانوالہ کا تاریخی فخر",
        description=hero.get("tagline", "پہلوانوں اور روایات کا عظیم شہر"),
        category="گوجرانوالہ کا فخر",
        photo_path=None,
        source_str="ذریعہ: ہمارا گوجرانوالہ",
        output_path=output_path
    )


if __name__ == "__main__":
    out = generate_templated_news_card(
        headline="گوجرانوالہ میں سموگ اور فضائی آلودگی کے خلاف بڑا ایکشن، فیکٹریاں سیل",
        description="ضلعی انتظامیہ کی جانب سے شہریوں کی صحت اور ماحول کے تحفظ کے لیے احکامات جاری",
        category="اہم خبر",
        output_path="test_perfect_render.png"
    )
    print("Rendered:", out, "Size:", os.path.getsize(out))
