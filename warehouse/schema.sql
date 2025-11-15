-- ========== DIMENSIONS ==========

CREATE TABLE IF NOT EXISTS dim_time (
    time_id     SERIAL PRIMARY KEY,
    timestamp   TIMESTAMPTZ NOT NULL,
    date        DATE NOT NULL,
    hour        INT,
    minute      INT,
    day_name    TEXT,
    month       INT,
    year        INT
);

CREATE TABLE IF NOT EXISTS dim_asset (
    asset_id    SERIAL PRIMARY KEY,
    asset_type  TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    name        TEXT,
    UNIQUE(asset_type, symbol)
);

CREATE TABLE IF NOT EXISTS dim_city (
    city_id     SERIAL PRIMARY KEY,
    city_name   TEXT NOT NULL,
    country     TEXT,
    UNIQUE(city_name, country)
);

-- ========== FACTS ==========
CREATE TABLE IF NOT EXISTS fact_gold (
    id          SERIAL PRIMARY KEY,
    asset_id    INT REFERENCES dim_asset(asset_id),
    time_id     INT REFERENCES dim_time(time_id),
    buy_price   NUMERIC,
    sell_price  NUMERIC,
    source      TEXT
);

CREATE TABLE IF NOT EXISTS fact_crypto (
    id          SERIAL PRIMARY KEY,
    asset_id    INT REFERENCES dim_asset(asset_id),
    time_id     INT REFERENCES dim_time(time_id),
    price_usd   NUMERIC,
    volume_24h  NUMERIC,
    market_cap  NUMERIC
);

CREATE TABLE IF NOT EXISTS fact_weather (
    id          SERIAL PRIMARY KEY,
    city_id     INT REFERENCES dim_city(city_id),
    time_id     INT REFERENCES dim_time(time_id),
    temperature NUMERIC,
    humidity    NUMERIC,
    wind_speed  NUMERIC,
    description TEXT
);

-- ========== STAGING TABLES ==========
CREATE TABLE IF NOT EXISTS stg_crypto_prices (
    id              SERIAL PRIMARY KEY,
    fetched_at      TIMESTAMPTZ,
    symbol          TEXT,
    name            TEXT,
    price_usd_raw   NUMERIC,
    volume_24h_raw  NUMERIC,
    market_cap_raw  NUMERIC,
    processed_at    TIMESTAMPTZ DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS stg_gold_prices (
    id              SERIAL PRIMARY KEY,
    scraped_at      TIMESTAMPTZ,
    source          TEXT,
    product_name    TEXT,
    buy_price_raw   TEXT,
    sell_price_raw  TEXT,
    currency        TEXT DEFAULT 'VND',
    processed_at    TIMESTAMPTZ DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS stg_weather (
    id              SERIAL PRIMARY KEY,
    fetched_at      TIMESTAMPTZ,
    city_name       TEXT,
    country         TEXT,
    temp_raw        NUMERIC,
    humidity_raw    NUMERIC,
    wind_speed_raw  NUMERIC,
    weather_desc_raw TEXT,
    processed_at    TIMESTAMPTZ DEFAULT NULL
);