import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
import altair as alt

from helper.normalize_date_range import normalize_date_range

# -- Cấu hình trang & Engine --
st.set_page_config(page_title="Gold Dashboard", layout="wide")
engine = create_engine(DB_URL)

@st.cache_data(ttl=600) # Cache 10 phút
def load_gold_data():
    query = text("""
    SELECT
        t.timestamp, a.symbol, a.name,
        f.buy_price, f.sell_price, f.source
    FROM fact_gold f
    JOIN dim_time t ON f.time_id = t.time_id
    JOIN dim_asset a ON f.asset_id = a.asset_id
    ORDER BY t.timestamp DESC
    LIMIT 1000 -- Giới hạn 1000 điểm dữ liệu mới nhất
    """)
    return pd.read_sql(query, engine)

df = load_gold_data()

st.title("💰 Dashboard Giá Vàng")

if df.empty:
    st.warning("Chưa có dữ liệu. Hãy chạy ETL: python run_etl_gold.py")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Bộ lọc")
    
    # Lọc theo loại vàng (symbol)
    asset_symbols = df["symbol"].unique().tolist()
    selected_symbols = st.sidebar.multiselect("Chọn loại vàng", asset_symbols, default=asset_symbols[:3]) # Mặc định 3 loại đầu
    
    # Lọc theo nguồn (SJC, PNJ, ...)
    sources = df["source"].unique().tolist()
    selected_sources = st.sidebar.multiselect("Chọn nguồn (Khu vực)", sources, default=sources[:1]) # Mặc định 1 nguồn
    
    # Lọc theo ngày
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    date_range = st.sidebar.date_input("Chọn khoảng thời gian", [min_date, max_date])
    start_date, end_date = normalize_date_range(date_range, min_date, max_date)

    # --- Áp dụng Filter ---
    filtered_df = df[
        (df["symbol"].isin(selected_symbols)) &
        (df["source"].isin(selected_sources)) &
        (df['timestamp'].dt.date >= start_date) &
        (df['timestamp'].dt.date <= end_date)
    ]
    
    st.subheader("Biểu đồ giá theo thời gian")
    
    # Cần "melt" dataframe để vẽ nhiều line
    df_melted = filtered_df.melt(
        id_vars=['timestamp', 'symbol', 'name', 'source'],
        value_vars=['buy_price', 'sell_price'],
        var_name='Loại giá',
        value_name='Giá (VND)'
    )

    # Tạo màu sắc theo 'symbol' + 'Loại giá'
    df_melted['legend'] = df_melted['symbol'] + ' (' + df_melted['Loại giá'] + ')'

    # Biểu đồ Altair
    chart = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('timestamp', title='Thời gian'),
        y=alt.Y('Giá (VND)'),
        color=alt.Color('legend', title="Loại vàng/giá"),
        tooltip=['timestamp', 'legend', 'Giá (VND)', 'source']
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Dữ liệu thô (đã lọc)")
    st.dataframe(filtered_df)