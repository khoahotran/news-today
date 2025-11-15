import datetime
import requests
from sqlalchemy import create_engine, text
from config.settings import DB_URL, COINGECKO_BASE_URL

engine = create_engine(DB_URL)

COINS = ["bitcoin", "ethereum"]

def fetch_crypto():
    endpoint = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    resp = requests.get(endpoint, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    fetched_at = datetime.datetime.utcnow()

    with engine.begin() as conn:
        for coin_id, values in data.items():
            conn.execute(
                text("""
                INSERT INTO stg_crypto_prices
                (fetched_at, symbol, name, price_usd_raw, volume_24h_raw, market_cap_raw)
                VALUES (:fetched_at, :symbol, :name, :price, :vol, :cap)
                """),
                {
                    "fetched_at": fetched_at,
                    "symbol": coin_id.upper(),
                    "name": coin_id.capitalize(),
                    "price": values.get("usd"),
                    "vol": values.get("usd_24h_vol"),
                    "cap": values.get("usd_market_cap"),
                }
            )

if __name__ == "__main__":
    fetch_crypto()