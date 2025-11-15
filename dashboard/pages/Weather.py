import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_URL
import altair as alt

from helper.normalize_date_range import normalize_date_range

# -- Cấu hình trang & Engine --
st.set_page_config(page_title="Weather Dashboard", layout="wide")
engine = create_engine(DB_URL)

@st.cache_data(ttl=600) # Cache 10 phút
def load_weather_data():
    query = text("""
    SELECT
        t.timestamp, c.city_name, c.country,
        f.temperature, f.humidity, f.wind_speed, f.description
    FROM fact_weather f
    JOIN dim_time t ON f.time_id = t.time_id
    JOIN dim_city c ON f.city_id = c.city_id
    ORDER BY t.timestamp DESC
    LIMIT 1000 -- Giới hạn 1000 điểm dữ liệu mới nhất
    """)
    df = pd.read_sql(query, engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_weather_data()

st.title("🌦️ Dashboard Thời tiết")

if df.empty:
    st.warning("Chưa có dữ liệu. Hãy chạy ETL: python run_etl_weather.py")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Bộ lọc")
    
    cities = df["city_name"].unique().tolist()
    selected_city = st.sidebar.selectbox("Chọn thành phố", cities)
    
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    date_range = st.sidebar.date_input("Chọn khoảng thời gian", [min_date, max_date])
    start_date, end_date = normalize_date_range(date_range, min_date, max_date)

    # --- Áp dụng Filter ---
    filtered_df = df[
        (df["city_name"] == selected_city) &
        (df['timestamp'].dt.date >= start_date) &
        (df['timestamp'].dt.date <= end_date)
    ].sort_values("timestamp")

    if filtered_df.empty:
        st.warning("Không có dữ liệu cho lựa chọn này.")
    else:
        # --- Hiển thị KPI ---
        latest_data = filtered_df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Nhiệt độ", value=f"{latest_data['temperature']}°C")
        col2.metric(label="Độ ẩm", value=f"{latest_data['humidity']}%")
        col3.metric(label="Tốc độ gió", value=f"{latest_data['wind_speed']} m/s")

        # --- Biểu đồ Nhiệt độ & Độ ẩm ---
        st.subheader("Nhiệt độ và Độ ẩm theo thời gian")
        
        base = alt.Chart(filtered_df).encode(
            x=alt.X('timestamp', title='Thời gian'),
            tooltip=['timestamp', 'temperature', 'humidity']
        ).interactive()

        temp_line = base.mark_line(color='red').encode(
            y=alt.Y('temperature', title='Nhiệt độ (°C)', scale=alt.Scale(zero=False))
        )
        
        humidity_line = base.mark_line(color='blue').encode(
            y=alt.Y('humidity', title='Độ ẩm (%)', scale=alt.Scale(zero=False))
        )
        
        # Kết hợp 2 biểu đồ
        chart = alt.layer(temp_line, humidity_line).resolve_scale(
            y='independent'
        )
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Dữ liệu thô (đã lọc)")
        st.dataframe(filtered_df)