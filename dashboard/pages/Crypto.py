import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
import altair as alt

from helper.normalize_date_range import normalize_date_range

# -- Cấu hình trang & Engine --
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
engine = create_engine(DB_URL)

@st.cache_data(ttl=600) # Cache 10 phút
def load_crypto_data():
    query = text("""
    SELECT
        t.timestamp, a.symbol,
        f.price_usd, f.volume_24h, f.market_cap
    FROM fact_crypto f
    JOIN dim_time t ON f.time_id = t.time_id
    JOIN dim_asset a ON f.asset_id = a.asset_id
    ORDER BY t.timestamp DESC
    LIMIT 2000 -- Giới hạn 2000 điểm dữ liệu mới nhất
    """)
    df = pd.read_sql(query, engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_crypto_data()

st.title("📈 Dashboard Crypto")

if df.empty:
    st.warning("Chưa có dữ liệu. Hãy chạy ETL: python run_etl_crypto.py")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Bộ lọc")
    
    coins = df["symbol"].unique().tolist()
    selected_coin = st.sidebar.selectbox("Chọn coin", coins, index=coins.index('BTC') if 'BTC' in coins else 0)
    
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    date_range = st.sidebar.date_input("Chọn khoảng thời gian", [min_date, max_date])
    start_date, end_date = normalize_date_range(date_range, min_date, max_date)

    # --- Áp dụng Filter ---
    filtered_df = df[
        (df["symbol"] == selected_coin) &
        (df['timestamp'].dt.date >= start_date) &
        (df['timestamp'].dt.date <= end_date)
    ].sort_values("timestamp")

    if filtered_df.empty:
        st.warning("Không có dữ liệu cho lựa chọn này.")
    else:
        # --- Hiển thị KPI ---
        latest_data = filtered_df.iloc[-1]
        st.metric(
            label=f"Giá {selected_coin} mới nhất",
            value=f"${latest_data['price_usd']:,.2f}",
            help=f"Cập nhật lúc {latest_data['timestamp']}"
        )

        # --- Biểu đồ giá ---
        st.subheader(f"Giá {selected_coin} theo thời gian")
        price_chart = alt.Chart(filtered_df).mark_line().encode(
            x=alt.X('timestamp', title='Thời gian'),
            y=alt.Y('price_usd', title=f'Giá (USD)', scale=alt.Scale(zero=False)),
            tooltip=['timestamp', 'price_usd']
        ).interactive()
        st.altair_chart(price_chart, use_container_width=True)
        
        # --- Biểu đồ Volume & Market Cap ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Volume 24h")
            vol_chart = alt.Chart(filtered_df).mark_area(opacity=0.7).encode(
                x=alt.X('timestamp', title='Thời gian'),
                y=alt.Y('volume_24h', title='Volume'),
                tooltip=['timestamp', 'volume_24h']
            ).interactive()
            st.altair_chart(vol_chart, use_container_width=True)

        with col2:
            st.subheader("Market Cap")
            cap_chart = alt.Chart(filtered_df).mark_area(opacity=0.7, color='orange').encode(
                x=alt.X('timestamp', title='Thời gian'),
                y=alt.Y('market_cap', title='Market Cap'),
                tooltip=['timestamp', 'market_cap']
            ).interactive()
            st.altair_chart(cap_chart, use_container_width=True)

        st.subheader("Dữ liệu thô (đã lọc)")
        st.dataframe(filtered_df)