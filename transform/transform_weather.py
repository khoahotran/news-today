import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
from warehouse.dimension_helpers import get_or_create_time, get_or_create_city

engine = create_engine(DB_URL)

def transform_weather():
    df = pd.read_sql("SELECT * FROM stg_weather", engine)

    if df.empty:
        print("No data in stg_weather")
        return

    with engine.begin() as conn:
        for _, row in df.iterrows():
            # fetched_at có thể là string -> convert
            fetched_at = pd.to_datetime(row["fetched_at"]).to_pydatetime()

            city_name = row["city_name"]
            country = row["country"]

            time_id = get_or_create_time(conn, fetched_at)
            city_id = get_or_create_city(conn, city_name, country)

            conn.execute(
                text("""
                INSERT INTO fact_weather
                (city_id, time_id, temperature, humidity, wind_speed, description)
                VALUES (:city_id, :time_id, :temp, :humidity, :wind_speed, :desc)
                """),
                {
                    "city_id": city_id,
                    "time_id": time_id,
                    "temp": row["temp_raw"],
                    "humidity": row["humidity_raw"],
                    "wind_speed": row["wind_speed_raw"],
                    "desc": row["weather_desc_raw"],
                }
            )

        print(f"Processed {len(df)} rows. Clearing staging table...")
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM stg_weather"))

    print("Transform weather OK!")

if __name__ == "__main__":
    transform_weather()