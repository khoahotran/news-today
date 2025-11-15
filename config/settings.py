import os
import json
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

# Load .env
load_dotenv(ENV_PATH)

DB_URL = os.getenv("DB_URL", "postgresql://multidata_user:multidata_pass@localhost:5432/multidata")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")

# Gold
try:
    GOLD_SOURCES = json.loads(os.getenv("GOLD_SOURCES", "[]"))
except:
    GOLD_SOURCES = []

# Weather cities
try:
    WEATHER_CITIES = json.loads(os.getenv("WEATHER_CITIES", "[]"))
except:
    WEATHER_CITIES = []
