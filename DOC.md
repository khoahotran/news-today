📘 Project Documentation
========================

**Tên project**: Multi-Source Real-time Data Pipeline (Gold, Crypto, Weather)  
**Tác giả**: _Khoa Tran_  
**Phiên bản**: v1.0

* * *

1\. Giới thiệu
--------------

### 1.1 Mục tiêu

Project này xây dựng một hệ thống **thu thập – xử lý – lưu trữ – trực quan hóa** dữ liệu từ nhiều nguồn khác nhau theo chuẩn **Data Engineering**:

*   Giá vàng (web scraping)
*   Giá crypto (API)
*   Thời tiết (API)

Hệ thống bao gồm:

*   **ETL pipelines** cho từng nguồn dữ liệu.
*   **Data Warehouse mini** với mô hình **star schema**.
*   **Dashboard** hiển thị các chỉ số và xu hướng thời gian thực hoặc gần thời gian thực.

### 1.2 Phạm vi (Scope)

Trong phạm vi phiên bản v1.0, hệ thống hỗ trợ:

*   Thu thập dữ liệu định kỳ (5–60 phút/lần).
*   Lưu trữ dữ liệu trong **PostgreSQL** hoặc **SQLite**.
*   Xây dựng **Data Warehouse** gồm:
    *   Các bảng dimension: thời gian, tài sản, thành phố.
    *   Các bảng fact: giá vàng, giá crypto, thời tiết.
*   Dashboard bằng **Streamlit** (hoặc công cụ tương đương).

### 1.3 Non-goals (Không nằm trong phạm vi)

*   Không sử dụng mô hình AI/ML phức tạp.
*   Không xử lý big data (hệ thống hướng tới dataset nhỏ–trung bình).
*   Không bao gồm hệ thống user authentication phức tạp cho dashboard (v1 có thể là public/local).

* * *

2\. Kiến trúc hệ thống
----------------------

### 2.1 Sơ đồ tổng quan

```text
              +-------------------+
              |  Gold Scraper     |
              | (Web Scraping)    |
              +-------------------+
                        |
                        v
              +-------------------+
              |  Crypto API       |
              | (CoinGecko, ...)  |
              +-------------------+
                        |
                        v
              +-------------------+
              |  Weather API      |
              | (OpenWeather, ...)|
              +-------------------+
                        |
                        v
             +----------------------+
             | Raw / Staging Layer  |
             | (PostgreSQL/SQLite)  |
             +----------------------+
                        |
                        v
             +----------------------+
             | Transform Jobs       |
             | (Python ETL)         |
             +----------------------+
                        |
                        v
             +----------------------+
             | Data Warehouse (DW)  |
             |  Star Schema         |
             +----------------------+
                        |
                        v
             +----------------------+
             | Dashboard / BI Layer |
             |  (Streamlit)         |
             +----------------------+
```

### 2.2 Các thành phần chính

1.  **Extract Layer**
    *   Thu thập dữ liệu từ:
        *   Website giá vàng (SJC, PNJ, DOJI, …).
        *   API crypto (CoinGecko).
        *   API thời tiết (OpenWeatherMap).
    *   Code: Python (`requests`, `BeautifulSoup`).
2.  **Staging Layer (Raw Data)**
    *   Lưu dữ liệu chưa transform vào các bảng staging.
    *   Phục vụ kiểm tra, debug và reproducibility.
3.  **Transform Layer**
    *   Làm sạch, chuẩn hóa dữ liệu:
        *   Định dạng thời gian.
        *   Đơn vị (Celsius, USD, …).
        *   Chuẩn hóa tên symbol tài sản.
    *   Join với dimension tables.
4.  **Data Warehouse (DW)**
    *   Thiết kế **star schema**.
    *   Bảng dimension + fact tối ưu cho truy vấn phân tích.
5.  **Orchestration / Scheduling**
    *   Sử dụng:
        *   **Cronjob** (default)
        *   (Optional) **Apache Airflow** nếu muốn nâng cấp.
6.  **Dashboard Layer**
    *   Xây bằng **Streamlit**:
        *   Giao diện web đơn giản.
        *   Hiển thị biểu đồ, KPI, filter theo thời gian.

* * *

3\. Tech Stack
--------------

### 3.1 Ngôn ngữ & Thư viện

*   **Python 3.10+**
*   Thư viện chính:
    *   `requests`: gọi API / GET HTML
    *   `beautifulsoup4`: parse HTML (giá vàng)
    *   `pandas`: xử lý data
    *   `sqlalchemy`: kết nối database
    *   `psycopg2` hoặc `asyncpg` (Postgres)
    *   `streamlit`: build dashboard
    *   `python-dotenv`: quản lý biến môi trường

### 3.2 Database

*   Dev/local: **SQLite**
*   Production/sẵn sàng scale hơn: **PostgreSQL**

### 3.3 Orchestration

*   Default: **cronjob** (Linux / WSL / MacOS).
*   Optional: **Apache Airflow** (chạy local bằng Docker).

* * *

4\. Nguồn dữ liệu
-----------------

> Lưu ý: API keys, URLs thực tế sẽ được cấu hình trong file `.env` hoặc `config/settings.py`.

### 4.1 Giá vàng (Gold)

*   **Nguồn**: Website các đơn vị như:
    *   SJC
    *   PNJ
    *   DOJI
*   **Phương thức**:
    *   Web scraping HTML bằng `requests` + `BeautifulSoup`.
*   **Dữ liệu tối thiểu cần lấy**:
    *   Tên loại vàng (VD: SJC 1L, PNJ 9999,…).
    *   Giá mua, giá bán.
    *   Đơn vị (lượng, chỉ, … nếu có).
    *   Thời gian cập nhật (nếu website có).

### 4.2 Crypto

*   **Nguồn**: API CoinGecko (không cần API key, free).
*   **Endpoint ví dụ** (pseudo):
    *   `/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true`
*   **Trường dữ liệu**:
    *   `symbol` (BTC, ETH, …)
    *   `price_usd`
    *   `market_cap`
    *   `volume_24h`
    *   `last_updated` (UTC)

### 4.3 Thời tiết (Weather)

*   **Nguồn**: OpenWeatherMap API.
*   **Yêu cầu**: API key.
*   **Endpoint ví dụ** (pseudo):
    *   `/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric`
*   **Trường dữ liệu**:
    *   `city_name`
    *   `country`
    *   `temperature`
    *   `humidity`
    *   `wind_speed`
    *   `weather_description`
    *   `timestamp`

* * *

5\. Data Model & Data Warehouse
-------------------------------

### 5.1 Tầng Staging (Raw Tables)

Các bảng staging lưu dữ liệu “thô” trước transform.

#### 5.1.1 `stg_gold_prices`

*   `id` (PK, auto)
*   `scraped_at` (timestamp)
*   `source` (text) – vd: 'SJC', 'PNJ'
*   `product_name` (text)
*   `buy_price_raw` (text)
*   `sell_price_raw` (text)
*   `currency` (text, default 'VND')

#### 5.1.2 `stg_crypto_prices`

*   `id` (PK)
*   `fetched_at` (timestamp)
*   `symbol` (text) – vd: 'BTC', 'ETH'
*   `name` (text) – 'Bitcoin', 'Ethereum'
*   `price_usd_raw` (numeric)
*   `volume_24h_raw` (numeric)
*   `market_cap_raw` (numeric)

#### 5.1.3 `stg_weather`

*   `id` (PK)
*   `fetched_at` (timestamp)
*   `city_name` (text)
*   `country` (text)
*   `temp_raw` (numeric)
*   `humidity_raw` (numeric)
*   `wind_speed_raw` (numeric)
*   `weather_desc_raw` (text)

* * *

### 5.2 Data Warehouse – Star Schema

#### 5.2.1 Dimension tables

##### a) `dim_time`

| Column | Type | Mô tả |
| --- | --- | --- |
| `time_id` | SERIAL PK | Khóa chính |
| `timestamp` | TIMESTAMP | Thời điểm đầy đủ |
| `date` | DATE | Ngày |
| `hour` | INT | Giờ (0–23) |
| `minute` | INT | Phút (0–59) |
| `day_name` | TEXT | Tên thứ (Mon, Tue, …) |
| `month` | INT | Tháng |
| `year` | INT | Năm |

##### b) `dim_asset`

| Column | Type | Mô tả |
| --- | --- | --- |
| `asset_id` | SERIAL PK | Khóa chính |
| `asset_type` | TEXT | 'gold' hoặc 'crypto' |
| `symbol` | TEXT | 'BTC', 'ETH', 'SJC\_1L', … |
| `name` | TEXT | 'Bitcoin', 'Ethereum', 'SJC 1 lượng', … |

##### c) `dim_city`

| Column | Type | Mô tả |
| --- | --- | --- |
| `city_id` | SERIAL PK | Khóa chính |
| `city_name` | TEXT | Tên thành phố |
| `country` | TEXT | Mã nước ISO hoặc tên quốc gia |

* * *

#### 5.2.2 Fact tables

##### a) `fact_gold`

| Column | Type | Mô tả |
| --- | --- | --- |
| `id` | SERIAL PK | Khóa chính |
| `asset_id` | INT FK → dim\_asset(asset\_id) |  |
| `time_id` | INT FK → dim\_time(time\_id) |  |
| `buy_price` | NUMERIC | Giá mua (VND) |
| `sell_price` | NUMERIC | Giá bán (VND) |
| `source` | TEXT | Trang web / đơn vị |

##### b) `fact_crypto`

| Column | Type | Mô tả |
| --- | --- | --- |
| `id` | SERIAL PK | Khóa chính |
| `asset_id` | INT FK |  |
| `time_id` | INT FK |  |
| `price_usd` | NUMERIC | Giá USD |
| `volume_24h` | NUMERIC | Volume 24h |
| `market_cap` | NUMERIC | Market cap |

##### c) `fact_weather`

| Column | Type | Mô tả |
| --- | --- | --- |
| `id` | SERIAL PK | Khóa chính |
| `city_id` | INT FK → dim\_city(city\_id) |  |
| `time_id` | INT FK → dim\_time(time\_id) |  |
| `temperature` | NUMERIC | Độ C |
| `humidity` | NUMERIC | % |
| `wind_speed` | NUMERIC | m/s hoặc km/h |
| `description` | TEXT | Mô tả thời tiết |

* * *

### 5.3 Ví dụ DDL (PostgreSQL)

```sql
CREATE TABLE dim_time (
    time_id     SERIAL PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    date        DATE NOT NULL,
    hour        INT,
    minute      INT,
    day_name    TEXT,
    month       INT,
    year        INT
);

CREATE TABLE dim_asset (
    asset_id    SERIAL PRIMARY KEY,
    asset_type  TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    name        TEXT
);

CREATE TABLE dim_city (
    city_id     SERIAL PRIMARY KEY,
    city_name   TEXT NOT NULL,
    country     TEXT
);

CREATE TABLE fact_gold (
    id          SERIAL PRIMARY KEY,
    asset_id    INT REFERENCES dim_asset(asset_id),
    time_id     INT REFERENCES dim_time(time_id),
    buy_price   NUMERIC,
    sell_price  NUMERIC,
    source      TEXT
);

CREATE TABLE fact_crypto (
    id          SERIAL PRIMARY KEY,
    asset_id    INT REFERENCES dim_asset(asset_id),
    time_id     INT REFERENCES dim_time(time_id),
    price_usd   NUMERIC,
    volume_24h  NUMERIC,
    market_cap  NUMERIC
);

CREATE TABLE fact_weather (
    id           SERIAL PRIMARY KEY,
    city_id      INT REFERENCES dim_city(city_id),
    time_id      INT REFERENCES dim_time(time_id),
    temperature  NUMERIC,
    humidity     NUMERIC,
    wind_speed   NUMERIC,
    description  TEXT
);
```

* * *

6\. Thiết kế ETL Pipelines
--------------------------

### 6.1 Quy ước chung

*   Mỗi nguồn dữ liệu có 3 bước:
    1.  `extract_*` → lưu vào `stg_*`.
    2.  `transform_*` → chuẩn hóa dữ liệu, mapping dimension.
    3.  `load_*` → ghi vào fact tables.
*   Các script Python được tổ chức theo thư mục:

```text
project/
├── extract/
│   ├── gold_scraper.py
│   ├── crypto_api.py
│   └── weather_api.py
├── transform/
│   ├── transform_gold.py
│   ├── transform_crypto.py
│   └── transform_weather.py
├── load/
│   ├── load_gold.py
│   ├── load_crypto.py
│   └── load_weather.py
└── warehouse/
    ├── schema.sql
    └── dimension_helpers.py
```

* * *

### 6.2 Pipeline: Giá vàng

#### 6.2.1 Extract (gold\_scraper.py)

*   Fetch HTML từ các URL cấu hình.
*   Locate bảng giá bằng selector (class/id).
*   Parse từng dòng dữ liệu:
    *   `product_name`, `buy_price_raw`, `sell_price_raw`, `source`.
*   Insert vào `stg_gold_prices`.

#### 6.2.2 Transform (transform\_gold.py)

*   Chuyển `buy_price_raw`, `sell_price_raw` → numeric (loại bỏ dấu phẩy, “đ”, …).
*   Chuẩn hóa `product_name` → mapping sang `dim_asset`:
    *   Nếu chưa tồn tại `asset` tương ứng thì insert mới vào `dim_asset`.
*   Map `timestamp` → `dim_time`:
    *   Nếu chưa có, insert record mới.

#### 6.2.3 Load (load\_gold.py)

*   Join staging với `dim_asset`, `dim_time`.
*   Insert vào `fact_gold`.

* * *

### 6.3 Pipeline: Crypto

#### 6.3.1 Extract (crypto\_api.py)

*   Gọi CoinGecko API với danh sách coin cấu hình sẵn (vd: BTC, ETH,…).
*   Parse JSON:
    *   `symbol`, `name`, `price_usd_raw`, `volume_24h_raw`, `market_cap_raw`.
*   Insert vào `stg_crypto_prices`.

#### 6.3.2 Transform (transform\_crypto.py)

*   Chuẩn hóa symbol (uppercase).
*   Sinh mapping `symbol` + `asset_type = 'crypto'` → `dim_asset`.
*   Map thời gian fetch → `dim_time`.

#### 6.3.3 Load (load\_crypto.py)

*   Join với `dim_asset` & `dim_time`.
*   Insert vào `fact_crypto`.

* * *

### 6.4 Pipeline: Thời tiết

#### 6.4.1 Extract (weather\_api.py)

*   Lặp qua danh sách thành phố (config).
*   Gọi OpenWeatherMap API cho mỗi city.
*   Parse JSON:
    *   `city_name`, `country`, `temp_raw`, `humidity_raw`, `wind_speed_raw`, `weather_desc_raw`.
*   Insert vào `stg_weather`.

#### 6.4.2 Transform (transform\_weather.py)

*   Đảm bảo temperature ở đơn vị °C.
*   Chuẩn hóa city, country → `dim_city` (insert nếu chưa có).
*   Map thời gian → `dim_time`.

#### 6.4.3 Load (load\_weather.py)

*   Join `stg_weather` với `dim_city`, `dim_time`.
*   Insert vào `fact_weather`.

* * *

### 6.5 Logging & Error Handling

*   Mỗi script ETL:
    *   Sử dụng `logging` (Python) với các mức: `INFO`, `WARNING`, `ERROR`.
    *   Log:
        *   Thời gian bắt đầu/kết thúc.
        *   Số bản ghi xử lý.
        *   Chi tiết lỗi (exception message, stack trace).
*   Có thể log ra file `logs/etl.log`.

* * *

7\. Orchestration & Scheduling
------------------------------

### 7.1 Sử dụng Cronjob (khuyến nghị cho máy yếu)

Ví dụ `crontab -e`:

```bash
# Chạy ETL mỗi 15 phút
*/15 * * * * /usr/bin/python3 /path/to/project/run_etl_gold.py >> /path/to/logs/gold.log 2>&1
*/15 * * * * /usr/bin/python3 /path/to/project/run_etl_crypto.py >> /path/to/logs/crypto.log 2>&1
*/30 * * * * /usr/bin/python3 /path/to/project/run_etl_weather.py >> /path/to/logs/weather.log 2>&1
```

`run_etl_gold.py` có thể gọi lần lượt:

*   `gold_scraper.py`
*   `transform_gold.py`
*   `load_gold.py`

### 7.2 Airflow (tùy chọn)

*   Tạo DAG:
    *   Task 1: `extract_gold`
    *   Task 2: `transform_gold`
    *   Task 3: `load_gold`
    *   Task 4–6 tương tự cho crypto, weather.
*   Đặt schedule interval: `*/15 * * * *` hoặc `@hourly`.

* * *

8\. Dashboard (Streamlit)
-------------------------

### 8.1 Cấu trúc app

`dashboard/app.py`:

*   Sidebar:
    *   Chọn source: Gold / Crypto / Weather / Overview.
    *   Chọn khoảng thời gian (from–to).
    *   Chọn loại tài sản/coin/city.
*   Pages:
    1.  **Overview**
        *   Giá vàng hiện tại.
        *   Giá BTC/ETH hiện tại.
        *   Nhiệt độ hiện tại của city chính.
    2.  **Gold**
        *   Biểu đồ line price theo thời gian.
        *   Bảng so sánh nhiều loại vàng.
    3.  **Crypto**
        *   Line chart giá BTC/ETH.
        *   Bar chart volume, market cap.
    4.  **Weather**
        *   Line chart nhiệt độ theo giờ/ngày.
        *   Bảng dữ liệu thời tiết theo city.

### 8.2 Các KPI gợi ý

*   Gold:
    *   Giá vàng SJC hiện tại vs 24h trước.
    *   % thay đổi giá.
*   Crypto:
    *   BTC price % change 24h.
    *   ETH vs BTC performance.
*   Weather:
    *   Nhiệt độ min/max trong ngày.
    *   City nóng nhất/lạnh nhất.

* * *

9\. Cấu hình & Quản lý bí mật
-----------------------------

### 9.1 File `.env` (không commit lên git)

Ví dụ:

```env
DB_URL=postgresql://user:password@localhost:5432/multidata
OPENWEATHER_API_KEY=your_api_key_here
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
GOLD_SOURCES='["https://...", "https://..."]'
```

### 9.2 `config/settings.py`

*   Đọc từ `.env` bằng `python-dotenv`.
*   Cung cấp các biến cấu hình chung.

* * *

10\. Cài đặt & Chạy
-------------------

### 10.1 Yêu cầu hệ thống

*   Python 3.10+
*   PostgreSQL hoặc SQLite
*   pip / venv
*   (Optional) Airflow, Docker

### 10.2 Các bước cài đặt

1.  Clone repo:
    ```bash
    git clone <repo_url>
    cd project
    ```
2.  Tạo virtual env & cài libs:
    ```bash
    python -m venv venv
    source venv/bin/activate  # hoặc venv\Scripts\activate trên Windows
    pip install -r requirements.txt
    ```
3.  Tạo database & chạy schema:
    ```bash
    # PostgreSQL
    createdb multidata
    psql -d multidata -f warehouse/schema.sql
    ```
4.  Tạo file `.env` từ template `.env.example`.
5.  Chạy thử ETL 1 lần:
    ```bash
    python extract/gold_scraper.py
    python transform/transform_gold.py
    python load/load_gold.py
    ```
6.  Chạy dashboard:
    ```bash
    cd dashboard
    streamlit run app.py
    ```

* * *

11\. Testing & Quality
----------------------

### 11.1 Unit Test

*   Test các hàm:
    *   Parse HTML (giá vàng).
    *   Gọi API (mock response).
    *   Hàm transform (clean dữ liệu, mapping).
*   Thư mục: `tests/`.

### 11.2 Integration Test

*   Test pipeline end-to-end:
    *   Chạy extract → transform → load trên sample data.
    *   Kiểm tra dữ liệu có vào đúng bảng không.

### 11.3 Data Quality Checks

*   Kiểm tra:
    *   Không có giá âm.
    *   Thời gian không null.
    *   Không insert trùng bản ghi (hoặc có cơ chế deduplicate).

* * *

12\. Bảo mật & Riêng tư
-----------------------

*   Không commit `.env` chứa API key.
*   Dùng user/password riêng cho database, không dùng superuser.
*   Hạn chế truy cập database từ bên ngoài (local hoặc private network).

* * *

13\. Hiệu năng & Giới hạn
-------------------------

*   Hệ thống thiết kế cho:
    *   Tần suất crawl thấp–trung bình (5–30 phút).
    *   Lượng data vừa phải (vài trăm nghìn dòng trở xuống).
*   Máy yếu vẫn chạy được vì:
    *   ETL chạy batch nhỏ.
    *   Không dùng ML hoặc xử lý nặng.
    *   Có thể dùng SQLite trong giai đoạn đầu.

* * *

14\. Hướng phát triển tương lai
-------------------------------

*   Thêm:
    *   Nhiều nguồn giá vàng / crypto hơn.
    *   Thêm dữ liệu chứng khoán.
*   Nâng cấp:
    *   Airflow + Docker +部署 lên cloud.
    *   Role-based access cho dashboard.
*   Phân tích nâng cao:
    *   Tính indicator tài chính (RSI, EMA, …).
    *   Dự báo bằng mô hình time series (khi cần).

* * *

15\. Tổng kết
-------------

Project này cung cấp một kiến trúc đầy đủ để bạn:

*   Thực hành **Data Engineering**: ETL, DW, pipeline, scheduling.
*   Thực hành **Data Analytics**: Dashboard, KPI, visualization.
*   Gom 3 loại dữ liệu thực tế (vàng, crypto, thời tiết) vào 1 hệ thống thống nhất.

* * *
