import pandas as pd
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Connection

def get_or_create_time(conn: Connection, ts: datetime) -> int:
    """Trả về time_id trong dim_time, tạo mới nếu chưa có."""
    if not isinstance(ts, datetime):
        ts = pd.to_datetime(ts).to_pydatetime()
    
    if ts.tzinfo is None:
        pass

    row = conn.execute(
        text("SELECT time_id FROM dim_time WHERE timestamp = :ts"),
        {"ts": ts}
    ).fetchone()

    if row:
        return row[0]

    payload = {
        "ts": ts,
        "date": ts.date(),
        "hour": ts.hour,
        "minute": ts.minute,
        "day_name": ts.strftime("%a"),
        "month": ts.month,
        "year": ts.year,
    }

    result = conn.execute(
        text("""
        INSERT INTO dim_time (timestamp, date, hour, minute, day_name, month, year)
        VALUES (:ts, :date, :hour, :minute, :day_name, :month, :year)
        RETURNING time_id
        """),
        payload
    )
    
    new_id = result.scalar()

    assert new_id is not None, "INSERT...RETURNING không trả về time_id"
    return new_id

def get_or_create_asset(conn: Connection, asset_type: str, symbol: str, name: str | None) -> int:
    """Trả về asset_id, tạo mới nếu chưa có."""
    row = conn.execute(
        text("""
        SELECT asset_id FROM dim_asset
        WHERE asset_type = :atype AND symbol = :symbol
        """),
        {"atype": asset_type, "symbol": symbol}
    ).fetchone()

    if row:
        return row[0]

    result = conn.execute(
        text("""
        INSERT INTO dim_asset (asset_type, symbol, name)
        VALUES (:atype, :symbol, :name)
        RETURNING asset_id
        """),
        {"atype": asset_type, "symbol": symbol, "name": name}
    )
    
    new_id = result.scalar()
    
    assert new_id is not None, "INSERT...RETURNING không trả về asset_id"
    return new_id

def get_or_create_city(conn: Connection, city_name: str, country: str | None) -> int:
    """Trả về city_id trong dim_city, tạo mới nếu chưa có."""
    if country is None:
        query = text("""
            SELECT city_id FROM dim_city
            WHERE city_name = :city_name AND country IS NULL
            """)
        params = {"city_name": city_name}
    else:
        query = text("""
            SELECT city_id FROM dim_city
            WHERE city_name = :city_name AND country = :country
            """)
        params = {"city_name": city_name, "country": country}

    row = conn.execute(query, params).fetchone()

    if row:
        return row[0]

    result = conn.execute(
        text("""
        INSERT INTO dim_city (city_name, country)
        VALUES (:city_name, :country)
        RETURNING city_id
        """),
        {"city_name": city_name, "country": country}
    )
    
    new_id = result.scalar()
    
    assert new_id is not None, "INSERT...RETURNING không trả về city_id"
    return new_id