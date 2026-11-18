import os
import sys
import base64
import subprocess
import shutil
from datetime import datetime
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = shutil.which("msedge") or shutil.which("chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"

FONTS_DIR = os.path.abspath("assets/fonts").replace("\\", "/")

def get_base64_image(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    ext = os.path.splitext(file_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"

def render_html_to_png(html_content, output_png, width=1080, height=1080):
    html_file = output_png.replace(".png", ".html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={os.path.abspath(output_png)}",
        os.path.abspath(html_file)
    ]
    subprocess.run(cmd, check=True)
    
    # Generate mobile preview at exactly 360x360 px
    preview_png = output_png.replace(".png", "_preview_360.png")
    with Image.open(output_png) as img:
        img_preview = img.resize((360, 360), Image.Resampling.LANCZOS)
        img_preview.save(preview_png, "PNG")
        
    print(f"Generated 1080x1080: {output_png}")
    print(f"Generated 360x360 mobile preview: {preview_png}")

# ==============================================================================
# CSS CORE STYLESHEET (FONTS, COLOR PALETTE, SAFE MARGINS)
# ==============================================================================
BASE_CSS = f"""
  @font-face {{
    font-family: 'JameelNooriNastaleeq';
    src: url('file:///{FONTS_DIR}/JameelNooriNastaleeq-Regular.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'NotoSansArabic';
    src: url('file:///{FONTS_DIR}/NotoSansArabic-Variable.ttf') format('truetype');
    font-weight: 700;
  }}
  @font-face {{
    font-family: 'NotoSansArabic';
    src: url('file:///{FONTS_DIR}/NotoSansArabic-Variable.ttf') format('truetype');
    font-weight: 500;
  }}
  @font-face {{
    font-family: 'Inter';
    src: url('file:///{FONTS_DIR}/Inter-Variable.ttf') format('truetype');
    font-weight: 600 700;
  }}
  @font-face {{
    font-family: 'BarlowCondensed';
    src: url('file:///{FONTS_DIR}/BarlowCondensed-ExtraBold.ttf') format('truetype');
    font-weight: 800;
  }}

  /* Color System */
  :root {{
    --deep-navy: #102B3A;
    --burgundy: #700D22;
    --warm-white: #F7F7F2;
    --yellow-accent: #FFE044;
    --dark-text: #17212B;
    --muted-grey: #E3E8EB;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    width: 1080px;
    height: 1080px;
    background: var(--warm-white);
    color: var(--dark-text);
    font-family: 'NotoSansArabic', sans-serif;
    position: relative;
    overflow: hidden;
    padding: 60px; /* Outer safe margin: 60px */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
"""

# ==============================================================================
# LAYOUT A: NEWS
# ==============================================================================
def render_layout_a_news(
    category_label,
    headline_lines,
    supporting_text,
    photo_path,
    source_name,
    timestamp_str,
    output_png
):
    photo_b64 = get_base64_image(photo_path)
    
    if isinstance(headline_lines, str):
        if "<br>" in headline_lines:
            lines = headline_lines.split("<br>")
        elif "\n" in headline_lines:
            lines = headline_lines.split("\n")
        else:
            lines = [headline_lines]
    else:
        lines = headline_lines
        
    lines_html = "".join([f'<div class="hl-line">{l.strip()}</div>' for l in lines[:2]])
    
    html = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  {BASE_CSS}

  /* Header Bar (height: 50px) */
  .header-bar {{
    width: 960px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
  }}
  .brand-logo-group {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-monogram {{
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: var(--burgundy);
    color: var(--warm-white);
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .brand-name-en {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--deep-navy);
  }}
  .category-pill {{
    background: var(--burgundy);
    color: var(--warm-white);
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 34px;
    font-weight: 700;
    padding: 4px 22px;
    border-radius: 8px;
    line-height: 1.2;
    direction: rtl;
  }}

  /* Headline Panel (height: 320px) */
  .headline-panel {{
    width: 960px;
    height: 320px;
    background: var(--burgundy);
    border-radius: 16px;
    padding: 40px 40px 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    box-shadow: 0 4px 16px rgba(112, 13, 34, 0.22);
  }}
  .hl-line {{
    font-family: 'JameelNooriNastaleeq', serif;
    font-size: 74px; /* Standard authentic Jameel Noori Nastaleeq size */
    color: var(--warm-white);
    line-height: 1.55;
    white-space: nowrap;
    text-align: center;
  }}

  /* Photo Panel (height: 330px) */
  .photo-panel {{
    width: 960px;
    height: 330px;
    border-radius: 16px;
    overflow: hidden;
    position: relative;
    background: var(--deep-navy);
    box-shadow: 0 4px 14px rgba(16, 43, 58, 0.15);
  }}
  .photo-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 30%;
  }}

  /* Supporting Text Panel (height: 125px) */
  .supporting-panel {{
    width: 960px;
    height: 125px;
    background: var(--deep-navy);
    border-radius: 14px;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }}
  .supporting-text {{
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 40px; /* Essential text >= 40px */
    font-weight: 500;
    color: var(--warm-white);
    line-height: 1.35;
  }}

  /* Branded Footer (height: 40px) */
  .footer-bar {{
    width: 960px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
    padding: 0 4px;
  }}
  .source-meta {{
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    color: #556270;
    font-weight: 600;
    white-space: nowrap;
  }}
  .footer-urdu-brand {{
    font-family: 'JameelNooriNastaleeq', serif;
    font-size: 38px;
    color: var(--burgundy);
    direction: rtl;
    white-space: nowrap;
    line-height: 1;
  }}
</style>
</head>
<body>
  <!-- Header Bar -->
  <div class="header-bar">
    <div class="brand-logo-group">
      <div class="brand-monogram">HG</div>
      <span class="brand-name-en">Hamara Gujranwala</span>
    </div>
    <div class="category-pill">{category_label}</div>
  </div>

  <!-- Prominent Headline Panel -->
  <div class="headline-panel">
    {lines_html}
  </div>

  <!-- Relevant Photograph Panel -->
  <div class="photo-panel">
    <img class="photo-img" src="{photo_b64}" alt="News Visual">
  </div>

  <!-- Supporting Line Panel -->
  <div class="supporting-panel">
    <div class="supporting-text">{supporting_text}</div>
  </div>

  <!-- Branded Footer -->
  <div class="footer-bar">
    <div class="source-meta">{source_name} • {timestamp_str}</div>
    <div class="footer-urdu-brand">ہماری گوجرانوالہ</div>
  </div>
</body>
</html>"""
    render_html_to_png(html, output_png)

# ==============================================================================
# LAYOUT B: WEATHER / AQI / DATA
# ==============================================================================
def render_layout_b_weather_aqi(
    metric_title,
    statistic_value,
    statistic_unit,
    status_label,
    practical_points,
    station_name,
    timestamp_str,
    output_png,
    is_hazardous=True
):
    stat_bg = "var(--burgundy)" if is_hazardous else "var(--deep-navy)"
    
    points_html = "".join([
        f'<div class="point-item"><div class="point-bullet"></div><div class="point-text">{p}</div></div>'
        for p in practical_points[:3]
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  {BASE_CSS}

  /* Header Bar */
  .header-bar {{
    width: 960px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
  }}
  .brand-logo-group {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-monogram {{
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: var(--deep-navy);
    color: var(--warm-white);
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .brand-name-en {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--deep-navy);
  }}
  .metric-label-pill {{
    background: var(--deep-navy);
    color: var(--warm-white);
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 34px;
    font-weight: 700;
    padding: 4px 22px;
    border-radius: 8px;
    direction: rtl;
  }}

  /* Dominant Statistic Panel (height: 380px) */
  .stat-panel {{
    width: 960px;
    height: 380px;
    background: {stat_bg};
    border-radius: 20px;
    padding: 26px 36px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 20px rgba(16, 43, 58, 0.2);
  }}
  .stat-number-row {{
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 16px;
    direction: ltr;
  }}
  .stat-figure {{
    font-family: 'BarlowCondensed', sans-serif;
    font-size: 165px; /* Main statistic: 150–190 px */
    font-weight: 800;
    color: var(--yellow-accent);
    line-height: 0.9;
    letter-spacing: -2px;
  }}
  .stat-unit {{
    font-family: 'Inter', sans-serif;
    font-size: 48px;
    font-weight: 700;
    color: var(--warm-white);
    letter-spacing: 1px;
  }}
  .status-badge {{
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid var(--warm-white);
    color: var(--warm-white);
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 52px; /* Secondary headline: 54–60 px */
    font-weight: 700;
    padding: 6px 40px;
    border-radius: 40px;
    margin-top: 14px;
    line-height: 1.2;
    text-align: center;
  }}

  /* Practical Points Panel (height: 410px) */
  .points-panel {{
    width: 960px;
    height: 410px;
    background: var(--muted-grey);
    border-radius: 18px;
    padding: 24px 36px;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
  }}
  .point-item {{
    display: flex;
    align-items: center;
    gap: 18px;
    direction: rtl;
  }}
  .point-bullet {{
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--burgundy);
    flex-shrink: 0;
  }}
  .point-text {{
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 40px; /* Supporting text: 40–44 px */
    font-weight: 500;
    color: var(--dark-text);
    line-height: 1.3;
    text-align: right;
  }}

  /* Footer Panel (height: 40px) */
  .footer-bar {{
    width: 960px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
    padding: 0 4px;
  }}
  .station-meta {{
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    color: #556270;
    font-weight: 600;
    white-space: nowrap;
  }}
  .footer-urdu-brand {{
    font-family: 'JameelNooriNastaleeq', serif;
    font-size: 36px;
    color: var(--deep-navy);
    direction: rtl;
    white-space: nowrap;
    line-height: 1;
  }}
</style>
</head>
<body>
  <!-- Header Bar -->
  <div class="header-bar">
    <div class="brand-logo-group">
      <div class="brand-monogram">HG</div>
      <span class="brand-name-en">Hamara Gujranwala</span>
    </div>
    <div class="metric-label-pill">{metric_title}</div>
  </div>

  <!-- Dominant Statistic Panel -->
  <div class="stat-panel">
    <div class="stat-number-row">
      <span class="stat-figure">{statistic_value}</span>
      <span class="stat-unit">{statistic_unit}</span>
    </div>
    <div class="status-badge">{status_label}</div>
  </div>

  <!-- Practical Points Panel -->
  <div class="points-panel">
    {points_html}
  </div>

  <!-- Branded Footer -->
  <div class="footer-bar">
    <div class="station-meta">{station_name} • {timestamp_str}</div>
    <div class="footer-urdu-brand">گوجرانوالہ انوائرمنٹ بلیٹن</div>
  </div>
</body>
</html>"""
    render_html_to_png(html, output_png)

# ==============================================================================
# LAYOUT C: COMMUNITY / EDUCATION / JOBS
# ==============================================================================
def render_layout_c_community_jobs(
    category_label,
    headline_lines,
    photo_path,
    blocks,
    source_name,
    timestamp_str,
    output_png
):
    photo_b64 = get_base64_image(photo_path)
    
    if isinstance(headline_lines, str):
        if "<br>" in headline_lines:
            lines = headline_lines.split("<br>")
        elif "\n" in headline_lines:
            lines = headline_lines.split("\n")
        else:
            lines = [headline_lines]
    else:
        lines = headline_lines
        
    lines_html = "".join([f'<div class="hl-line">{l.strip()}</div>' for l in lines[:2]])
    
    # Render up to 3 separated information blocks
    blocks_html = ""
    for b in blocks[:3]:
        blocks_html += f"""
        <div class="info-block">
          <div class="block-label">{b['label']}</div>
          <div class="block-value">{b['value']}</div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  {BASE_CSS}

  /* Header Bar */
  .header-bar {{
    width: 960px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
  }}
  .brand-logo-group {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand-monogram {{
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: var(--deep-navy);
    color: var(--warm-white);
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .brand-name-en {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--deep-navy);
  }}
  .category-pill {{
    background: var(--deep-navy);
    color: var(--warm-white);
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 34px;
    font-weight: 700;
    padding: 4px 22px;
    border-radius: 8px;
    direction: rtl;
  }}

  /* Headline Panel (height: 260px) */
  .headline-panel {{
    width: 960px;
    height: 260px;
    background: var(--deep-navy);
    border-radius: 16px;
    padding: 35px 40px 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }}
  .hl-line {{
    font-family: 'JameelNooriNastaleeq', serif;
    font-size: 66px; /* Jameel Noori Nastaleeq calibrated size */
    color: var(--warm-white);
    line-height: 1.5;
    white-space: nowrap;
    text-align: center;
  }}

  /* Relevant Photograph Panel (height: 330px) */
  .photo-panel {{
    width: 960px;
    height: 330px;
    border-radius: 16px;
    overflow: hidden;
    position: relative;
    background: var(--deep-navy);
  }}
  .photo-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 40%;
  }}

  /* Three Separated Information Blocks (height: 240px) */
  .blocks-row {{
    width: 960px;
    height: 240px;
    display: flex;
    justify-content: space-between;
    gap: 24px; /* Gap between panels >= 24px */
  }}
  .info-block {{
    flex: 1;
    background: var(--muted-grey);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-top: 6px solid var(--burgundy);
    direction: rtl;
    text-align: right;
  }}
  .block-label {{
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 34px; /* Short labels: 34–38 px */
    font-weight: 700;
    color: var(--burgundy);
    line-height: 1.2;
  }}
  .block-value {{
    font-family: 'NotoSansArabic', sans-serif;
    font-size: 40px; /* Supporting text / value >= 40px */
    font-weight: 700;
    color: var(--dark-text);
    line-height: 1.25;
  }}

  /* Branded Footer (height: 40px) */
  .footer-bar {{
    width: 960px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: ltr;
    padding: 0 4px;
  }}
  .source-meta {{
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    color: #556270;
    font-weight: 600;
    white-space: nowrap;
  }}
  .footer-urdu-brand {{
    font-family: 'JameelNooriNastaleeq', serif;
    font-size: 36px;
    color: var(--deep-navy);
    direction: rtl;
    white-space: nowrap;
    line-height: 1;
  }}
</style>
</head>
<body>
  <!-- Header Bar -->
  <div class="header-bar">
    <div class="brand-logo-group">
      <div class="brand-monogram">HG</div>
      <span class="brand-name-en">Hamara Gujranwala</span>
    </div>
    <div class="category-pill">{category_label}</div>
  </div>

  <!-- Headline Panel -->
  <div class="headline-panel">
    {lines_html}
  </div>

  <!-- Relevant Photograph Panel -->
  <div class="photo-panel">
    <img class="photo-img" src="{photo_b64}" alt="Education/Employment Visual">
  </div>

  <!-- Three Separated Information Blocks -->
  <div class="blocks-row">
    {blocks_html}
  </div>

  <!-- Branded Footer -->
  <div class="footer-bar">
    <div class="source-meta">{source_name} • {timestamp_str}</div>
    <div class="footer-urdu-brand">گوجرانوالہ پبلک سروس</div>
  </div>
</body>
</html>"""
    render_html_to_png(html, output_png)

if __name__ == "__main__":
    os.makedirs("sample_renders/design_system", exist_ok=True)
    
    # 1. Test Layout A: NEWS
    render_layout_a_news(
        category_label="شہر کی خبریں",
        headline_lines=[
            "گوجرانوالہ: سموگ کے خلاف ایکشن",
            "متعدد غیر قانونی فیکٹریاں سیل"
        ],
        supporting_text="محکمہ تحفظ ماحول نے جی ٹی روڈ اور صنعتی علاقوں میں زہریلا دھواں خارج کرنے والے یونٹس بند کر دیے۔",
        photo_path="assets/photos/smog_factory.jpg",
        source_name="Dawn News",
        timestamp_str="17 Nov 2026, 10:00 PM PKT",
        output_png="sample_renders/design_system/layout_a_news.png"
    )

    # 2. Test Layout B: WEATHER / AQI / DATA
    render_layout_b_weather_aqi(
        metric_title="ایئر کوالٹی انڈیکس (AQI)",
        statistic_value="385",
        statistic_unit="AQI",
        status_label="انتہائی غیر صحت بخش",
        practical_points=[
            "گھر سے باہر ماسک کا لازمی استعمال کریں۔",
            "بزرگ اور بچے کھلی فضا میں سرگرمیاں محدود رکھیں۔",
            "صنعتی شاہراہوں پر غیر ضروری سفر سے گریز کریں۔"
        ],
        station_name="EPA Station, Civil Lines",
        timestamp_str="17 Nov 2026, 9 PM PKT",
        output_png="sample_renders/design_system/layout_b_aqi.png",
        is_hazardous=True
    )

    # 3. Test Layout C: COMMUNITY / EDUCATION / JOBS
    render_layout_c_community_jobs(
        category_label="ملازمت کے مواقع",
        headline_lines=[
            "گیپکو میں نئی تکنیکی اسامیاں",
            "درخواستیں جمع کروانے کا باضابطہ اعلان"
        ],
        photo_path="assets/photos/gepco_cropped.jpg",
        blocks=[
            {"label": "آخری تاریخ:", "value": "25 نومبر 2026"},
            {"label": "تعلیمی قابلیت:", "value": "ڈپلومہ / میٹرک"},
            {"label": "تعیناتی کا مقام:", "value": "گوجرانوالہ ڈویژن"}
        ],
        source_name="GEPCO Official Notice",
        timestamp_str="17 Nov 2026, 5 PM PKT",
        output_png="sample_renders/design_system/layout_c_jobs.png"
    )
    print("All 3 Jameel-powered layouts generated successfully!")
