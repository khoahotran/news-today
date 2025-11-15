import datetime
import requests
from sqlalchemy import create_engine, text
from config.settings import DB_URL, OPENWEATHER_API_KEY, WEATHER_CITIES

engine = create_engine(DB_URL)

def parse_city_entry(entry: str):
    """
    entry dạng: "Ho Chi Minh City,VN"
    Trả về: ("Ho Chi Minh City", "VN")
    """
    parts = [p.strip() for p in entry.split(",")]
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]

def fetch_weather():
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set in .env")

    if not WEATHER_CITIES:
        raise RuntimeError("WEATHER_CITIES is empty in .env")

    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    fetched_at = datetime.datetime.utcnow()

    with engine.begin() as conn:
        for entry in WEATHER_CITIES:
            city_name, country = parse_city_entry(entry)
            if country:
                q = f"{city_name},{country}"
            else:
                q = city_name

            params = {
                "q": q,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            }

            resp = requests.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            weather_desc = data["weather"][0]["description"]
            city = data["name"]
            country_code = data.get("sys", {}).get("country")

            conn.execute(
                text("""
                INSERT INTO stg_weather
                (fetched_at, city_name, country, temp_raw, humidity_raw, wind_speed_raw, weather_desc_raw)
                VALUES (:fetched_at, :city_name, :country, :temp, :humidity, :wind_speed, :desc)
                """),
                {
                    "fetched_at": fetched_at,
                    "city_name": city,
                    "country": country_code,
                    "temp": temp,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "desc": weather_desc,
                }
            )

if __name__ == "__main__":
    fetch_weather()