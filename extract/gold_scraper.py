import datetime
import requests
from sqlalchemy import create_engine, text
from config.settings import DB_URL
import pandas as pd

engine = create_engine(DB_URL)

PNJ_API = "https://edge-api.pnj.io/ecom-frontend/v3/get-gold-price"

def parse_price(p):
    """Convert '152.500' -> 152500000 (VND)."""
    try:
        return float(p.replace(".", "")) * 1000  # pnj format actually thousands
    except:
        return None

def parse_datetime(dt_str):
    """Convert '14/11/2025 13:39:32' -> python datetime."""
    return pd.to_datetime(dt_str, format="%d/%m/%Y %H:%M:%S").to_pydatetime()

def fetch_gold():
    resp = requests.get(PNJ_API, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    with engine.begin() as conn:
        for loc in data.get("locations", []):
            location = loc.get("name", "")

            for item in loc.get("gold_type", []):
                name = item.get("name")
                buy = parse_price(item.get("gia_mua"))
                sell = parse_price(item.get("gia_ban"))
                updated_at = parse_datetime(item.get("updated_at"))

                conn.execute(
                    text("""
                    INSERT INTO stg_gold_prices
                    (scraped_at, source, product_name, buy_price_raw, sell_price_raw, currency)
                    VALUES (:scraped_at, :source, :product_name, :buy, :sell, :currency)
                    """),
                    {
                        "scraped_at": updated_at,   # theo updated_at thật
                        "source": location,        # location: TPHCM / Hà Nội…
                        "product_name": name,       # PNJ / SJC / Nhẫn PNJ…
                        "buy": buy,
                        "sell": sell,
                        "currency": "VND",
                    }
                )

    print("Extract gold OK!")

if __name__ == "__main__":
    fetch_gold()
