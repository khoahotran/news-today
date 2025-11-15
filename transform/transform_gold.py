import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
from warehouse.dimension_helpers import get_or_create_time, get_or_create_asset

engine = create_engine(DB_URL)

def normalize_symbol(text):
    """Convert 'Nhẫn Trơn PNJ 999.9' -> 'NHAN_TRON_PNJ_9999' """
    import re
    s = text.upper()
    s = re.sub(r"[^\w]+", "_", s)
    return s.strip("_")

def transform_gold():
    df = pd.read_sql("SELECT * FROM stg_gold_prices", engine)

    if df.empty:
        print("No data in stg_gold_prices")
        return

    with engine.begin() as conn:
        for _, row in df.iterrows():
            scraped_at = pd.to_datetime(row["scraped_at"]).to_pydatetime()
            source = row["source"]
            product = row["product_name"]

            symbol = normalize_symbol(product)

            time_id = get_or_create_time(conn, scraped_at)
            asset_id = get_or_create_asset(conn, "gold", symbol, product)

            conn.execute(
                text("""
                INSERT INTO fact_gold (asset_id, time_id, buy_price, sell_price, source)
                VALUES (:asset_id, :time_id, :buy, :sell, :source)
                """),
                {
                    "asset_id": asset_id,
                    "time_id": time_id,
                    "buy": row["buy_price_raw"],
                    "sell": row["sell_price_raw"],
                    "source": source
                }
            )

        print(f"Processed {len(df)} rows. Clearing staging table...")
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM stg_gold_prices"))

    print("Transform gold OK!")

if __name__ == "__main__":
    transform_gold()
