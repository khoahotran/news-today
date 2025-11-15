import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
from warehouse.dimension_helpers import get_or_create_time, get_or_create_asset

engine = create_engine(DB_URL)

def transform_crypto():
    df = pd.read_sql("SELECT * FROM stg_crypto_prices", engine)

    if df.empty:
        print("No data in stg_crypto_prices")
        return

    with engine.begin() as conn:
        for _, row in df.iterrows():

            # --- FIX QUAN TRỌNG: pandas.Timestamp -> python datetime ---
            fetched_at = pd.to_datetime(row["fetched_at"]).to_pydatetime()

            symbol = str(row["symbol"]).upper()
            name = row["name"]

            time_id = get_or_create_time(conn, fetched_at)
            asset_id = get_or_create_asset(conn, "crypto", symbol, name)

            conn.execute(
                text("""
                INSERT INTO fact_crypto (asset_id, time_id, price_usd, volume_24h, market_cap)
                VALUES (:asset_id, :time_id, :price, :vol, :cap)
                """),
                {
                    "asset_id": asset_id,
                    "time_id": time_id,
                    "price": row["price_usd_raw"],
                    "vol": row["volume_24h_raw"],
                    "cap": row["market_cap_raw"],
                }
            )
        print(f"Processed {len(df)} rows. Clearing staging table...")
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM stg_crypto_prices"))
            
    print("Transform crypto OK!")

if __name__ == "__main__":
    transform_crypto()
