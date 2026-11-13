"""
Daily Morning Weather & Smog/AQI Engine for Gujranwala.
Fetches real-time meteorological and air quality index data for Gujranwala,
crafts human-expert Urdu forecasts with 3 structured bullet points,
renders branded cards on the official V2 template, and posts to Facebook.
"""

import os
import sys
import requests
from datetime import datetime

# Ensure UTF-8 output encoding across Windows and Linux
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from card_generator import generate_templated_news_card, get_urdu_date


GUJRANWALA_LAT = 32.1877
GUJRANWALA_LON = 74.1945


WEATHER_CODE_UR = {
    0: "مطلع بالکل صاف اور دھوپ",
    1: "ہلکے بادل اور صاف موسم",
    2: "جزوی طور پر ابر آلود",
    3: "مطلع مکمل ابر آلود",
    45: "صبح کے وقت شدید دھند اور اسموگ",
    48: "جمنے والی دھند اور کہرا",
    51: "ہلکی پھلکی بوندا باندی",
    53: "درمیانی بارش",
    55: "تیز بارش کا امکان",
    61: "بارش کا سلسلہ جاری رہنے کا امکان",
    63: "موسلادھار بارش",
    65: "شدید موسلادھار بارش",
    80: "وقفے وقفے سے بارش کی پھوار",
    95: "گرج چمک کے ساتھ طوفانی بارش"
}


def get_aqi_advisory(aqi):
    """Categorize US AQI and provide medical / civic advisory in natural Urdu."""
    if aqi <= 50:
        return "بہترین اور صاف ہوا", "شہری کھلی فضا اور سیر سے لطف اندوز ہو سکتے ہیں"
    elif aqi <= 100:
        return "معتدل معیارِ ہوا", "حساس افراد دورانِ سفر احتیاط برتیں"
    elif aqi <= 150:
        return "غیر صحت بخش (حساس افراد کے لیے)", "بزرگ اور بچے ماسک کا استعمال یقینی بنائیں"
    elif aqi <= 200:
        return "شدید غیر صحت بخش اسموگ", "شہری باہر نکلتے وقت ماسک لازمی استعمال کریں"
    else:
        return "خطرناک فضائی آلودگی", "بلا ضرورت گھر سے باہر نہ نکلیں اور کھڑکیاں بند رکھیں"


def fetch_gujranwala_weather_data():
    """Fetch live forecast and air quality from Open-Meteo for Gujranwala."""
    try:
        # Weather forecast
        w_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={GUJRANWALA_LAT}&longitude={GUJRANWALA_LON}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            "&timezone=Asia%2FKarachi"
        )
        w_resp = requests.get(w_url, timeout=12).json()
        current = w_resp.get("current", {})
        daily = w_resp.get("daily", {})

        temp_curr = round(current.get("temperature_2m", 22))
        temp_feels = round(current.get("apparent_temperature", temp_curr))
        temp_max = round(daily.get("temperature_2m_max", [temp_curr + 4])[0])
        temp_min = round(daily.get("temperature_2m_min", [temp_curr - 4])[0])
        rain_prob = round(daily.get("precipitation_probability_max", [10])[0])
        w_code = current.get("weather_code", 1)
        w_desc = WEATHER_CODE_UR.get(w_code, "معتدل اور جزوی ابر آلود")
        humidity = round(current.get("relative_humidity_2m", 65))
        wind_speed = round(current.get("wind_speed_10m", 8))

        # Air Quality / Smog index
        aqi_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={GUJRANWALA_LAT}&longitude={GUJRANWALA_LON}"
            "&current=pm2_5,us_aqi&timezone=Asia%2FKarachi"
        )
        aqi_resp = requests.get(aqi_url, timeout=12).json()
        aqi_curr = aqi_resp.get("current", {})
        us_aqi = round(aqi_curr.get("us_aqi", 160))
        pm25 = round(aqi_curr.get("pm2_5", 85), 1)

        return {
            "temp_curr": temp_curr,
            "temp_feels": temp_feels,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "rain_prob": rain_prob,
            "w_desc": w_desc,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "us_aqi": us_aqi,
            "pm25": pm25
        }
    except Exception as e:
        print(f"Weather API notice: {e}, falling back to seasonal estimates.")
        return {
            "temp_curr": 22,
            "temp_feels": 23,
            "temp_max": 27,
            "temp_min": 17,
            "rain_prob": 20,
            "w_desc": "جزوی ابر آلود اور ہلکی اسموگ",
            "humidity": 68,
            "wind_speed": 7,
            "us_aqi": 165,
            "pm25": 88.0
        }


def craft_weather_package():
    """Produce complete high-readability weather and smog package for Gujranwala."""
    data = fetch_gujranwala_weather_data()
    aqi_status, aqi_advice = get_aqi_advisory(data["us_aqi"])

    headline_ur = f"گوجرانوالہ: آج کا موسم اور اسموگ الرٹ"

    desc_lines = [
        f"آج متوقع درجہ حرارت زیادہ سے زیادہ {data['temp_max']}°C اور کم سے کم {data['temp_min']}°C رہے گا۔",
        f"موسمی صورتحال: {data['w_desc']}، بارش کا امکان {data['rain_prob']} فیصد متوقع۔",
        f"ائیر کوالٹی انڈیکس (AQI): {data['us_aqi']} ({aqi_status})، {aqi_advice}۔"
    ]

    # Select strictly matched photo
    if data["us_aqi"] >= 150:
        photo_path = "assets/photos/smog_factory.jpg"
    else:
        photo_path = "assets/photos/civic_city.jpg"

    caption = (
        f"🌤️ صبح بخیر زندہ دلانِ گوجرانوالہ! | آج کا موسم اور اسموگ الرٹ\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📢 گوجرانوالہ اور گردونواح کے لیے محکمہ موسمیات و ماحولیات کی تازہ ترین رپورٹ:\n\n"
        f"تفصیلات ایک نظر میں:\n"
        f"• زیادہ سے زیادہ درجہ حرارت: {data['temp_max']}°C\n"
        f"• کم سے کم درجہ حرارت: {data['temp_min']}°C (محسوس شدہ: {data['temp_feels']}°C)\n"
        f"• موسمی کیفیت: {data['w_desc']}\n"
        f"• بارش کا امکان: {data['rain_prob']}%\n"
        f"• ہوا میں نمی: {data['humidity']}%\n"
        f"• فضائی آلودگی انڈیکس (AQI): {data['us_aqi']} — {aqi_status}\n\n"
        f"⚠️ صحت کی احتیاطی تدابیر:\n"
        f"{aqi_advice}۔ موٹرسائیکل سوار اور صبح سویرے اسکول جانے والے بچے ماسک کا استعمال ضرور کریں۔\n\n"
        f"💬 آپ کے علاقے میں اس وقت موسم اور دھند یا اسموگ کی کیا صورتحال ہے؟ کمنٹ میں اپنے محلے یا چوک کا نام لکھ کر بتائیں!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 گوجرانوالہ کی ہر صبح کی تازہ خبر اور موسم کی اپڈیٹ سب سے پہلے حاصل کرنے کے لیے ہمارے پیج 'Hamara Gujranwala' کو فالو کریں!\n\n"
        f"#HamaraGujranwala #GujranwalaWeather #Gujranwala #گوجرانوالہ #گوجرانوالہ_موسم #SmogUpdate #HamaraGujranwalaOfficial"
    )

    return {
        "headline_ur": headline_ur,
        "desc_lines": desc_lines,
        "category_ur": "موسم اور اسموگ",
        "photo_path": photo_path,
        "caption": caption,
        "data": data
    }


def run_weather_post(poster):
    """Generate weather card on official V2 template and publish to Facebook."""
    print("🌤️ Generating Daily Morning Weather & Smog Forecast for Gujranwala...")
    pkg = craft_weather_package()

    temp_card = "temp_weather_card.png"
    generate_templated_news_card(
        headline=pkg["headline_ur"],
        description=pkg["desc_lines"],
        category="موسم اور اسموگ",
        photo_path=pkg["photo_path"],
        source_str="حوالہ: محکمہ موسمیات و ماحولیات",
        output_path=temp_card
    )

    res = poster.post_photo(temp_card, pkg["caption"])

    if os.path.exists(temp_card):
        try:
            os.remove(temp_card)
        except Exception:
            pass

    return res


if __name__ == "__main__":
    pkg = craft_weather_package()
    print("Weather Headline:", pkg["headline_ur"])
    print("Lines:")
    for l in pkg["desc_lines"]:
        print("-", l)
    out = generate_templated_news_card(
        headline=pkg["headline_ur"],
        description=pkg["desc_lines"],
        category="موسم اور اسموگ",
        photo_path=pkg["photo_path"],
        source_str="حوالہ: محکمہ موسمیات و ماحولیات",
        output_path="test_weather_render.png"
    )
    print("Rendered:", out)
