# Multi-Source Real-time Data Pipeline

Project thu thập, xử lý và hiển thị dữ liệu Vàng, Crypto, Thời tiết.

## Cài đặt

1. Clone repo
2. Tạo file `.env` từ file mẫu
3. Chạy Docker: `docker-compose up -d`
4. Cài thư viện: `pip install -r requirements.txt`

## Chạy
- ETL: `python run_etl_crypto.py` (tương tự cho gold, weather)
- Dashboard: `streamlit run dashboard/app.py`