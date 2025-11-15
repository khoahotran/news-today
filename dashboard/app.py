import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from config.settings import DB_URL


from config.settings import DB_URL

# -- Cấu hình trang & Engine --
st.set_page_config(page_title="Data Pipeline Dashboard", layout="wide")
engine = create_engine(DB_URL)

# --- Các hàm tải dữ liệu (chỉ lấy KPI mới nhất) ---

@st.cache_data(ttl=60) # Cache 60 giây
def load_latest_kpis():
    """Tải KPI mới nhất từ cả 3 nguồn."""
    kpis = {}
    
    with engine.connect() as conn:
        # 1. Crypto: Lấy giá BTC và ETH mới nhất
        crypto_sql = text("""
            SELECT DISTINCT ON (a.symbol)
                a.symbol, f.price_usd
            FROM fact_crypto f
            JOIN dim_asset a ON f.asset_id = a.asset_id
            JOIN dim_time t ON f.time_id = t.time_id
            WHERE a.symbol IN ('BTC', 'ETH')
            ORDER BY a.symbol, t.timestamp DESC;
        """)
        crypto_df = pd.read_sql(crypto_sql, conn)
        kpis['crypto'] = crypto_df.set_index('symbol')['price_usd'].to_dict()

        # 2. Gold: Lấy giá SJC mới nhất
        gold_sql = text("""
            SELECT DISTINCT ON (a.symbol)
                a.name, f.buy_price, f.sell_price
            FROM fact_gold f
            JOIN dim_asset a ON f.asset_id = a.asset_id
            JOIN dim_time t ON f.time_id = t.time_id
            WHERE a.symbol LIKE '%SJC%' -- Lấy SJC làm đại diện
            ORDER BY a.symbol, t.timestamp DESC
            LIMIT 1;
        """)
        gold_df = pd.read_sql(gold_sql, conn)
        if not gold_df.empty:
            kpis['gold'] = gold_df.iloc[0].to_dict()

        # 3. Weather: Lấy thời tiết TPHCM mới nhất
        weather_sql = text("""
            SELECT DISTINCT ON (c.city_name)
                c.city_name, f.temperature, f.humidity, f.description
            FROM fact_weather f
            JOIN dim_city c ON f.city_id = c.city_id
            JOIN dim_time t ON f.time_id = t.time_id
            WHERE c.city_name = 'Ho Chi Minh City'
            ORDER BY c.city_name, t.timestamp DESC;
        """)
        weather_df = pd.read_sql(weather_sql, conn)
        if not weather_df.empty:
            kpis['weather'] = weather_df.iloc[0].to_dict()
            
    kpis['last_updated'] = datetime.datetime.now()
    return kpis

# --- Giao diện trang Overview ---

st.title("📊 Tổng quan (Overview)")

kpis = load_latest_kpis()
st.write(f"Cập nhật lần cuối: {kpis.get('last_updated', 'N/A')}")

col1, col2, col3 = st.columns(3)

# Cột Crypto
with col1:
    st.header("📈 Crypto")
    btc_price = kpis.get('crypto', {}).get('BTC', 0)
    eth_price = kpis.get('crypto', {}).get('ETH', 0)
    st.metric(label="BTC Price", value=f"${btc_price:,.2f}")
    st.metric(label="ETH Price", value=f"${eth_price:,.2f}")

# Cột Vàng
with col2:
    st.header("💰 Vàng")
    gold_data = kpis.get('gold', {})
    gold_name = gold_data.get('name', 'N/A')
    buy_price = gold_data.get('buy_price', 0)
    sell_price = gold_data.get('sell_price', 0)
    st.metric(label=f"{gold_name} (Mua)", value=f"{buy_price:,.0f} VND")
    st.metric(label=f"{gold_name} (Bán)", value=f"{sell_price:,.0f} VND")

# Cột Thời tiết
with col3:
    st.header("🌦️ Thời tiết (TPHCM)")
    weather_data = kpis.get('weather', {})
    temp = weather_data.get('temperature', 0)
    humidity = weather_data.get('humidity', 0)
    desc = weather_data.get('description', 'N/A')
    st.metric(label="Nhiệt độ", value=f"{temp}°C", delta=f"{humidity}% Độ ẩm")
    st.info(f"Mô tả: {desc.capitalize()}")

st.divider()
st.markdown("Chọn một trang từ thanh bên (sidebar) để xem chi tiết.")