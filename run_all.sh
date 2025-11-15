#!/bin/bash

PROJECT_DIR="/home/khoahotran/news-today"
PYTHON_EXEC="$PROJECT_DIR/venv/bin/python"
LOG_FILE="$PROJECT_DIR/logs/etl_cron.log"

# Di chuyển vào thư mục project
cd $PROJECT_DIR

export PYTHONPATH="$PROJECT_DIR"

# ==================================

echo "==========================================" >> $LOG_FILE
echo "Bắt đầu chạy ETL lúc: $(date)" >> $LOG_FILE

echo "--- Chạy Gold ETL ---" >> $LOG_FILE
$PYTHON_EXEC $PROJECT_DIR/load/load_gold.py >> $LOG_FILE 2>&1

echo "--- Chạy Crypto ETL ---" >> $LOG_FILE
$PYTHON_EXEC $PROJECT_DIR/load/load_crypto.py >> $LOG_FILE 2>&1

echo "--- Chạy Weather ETL ---" >> $LOG_FILE
$PYTHON_EXEC $PROJECT_DIR/load/load_weather.py >> $LOG_FILE 2>&1

echo "Kết thúc ETL lúc: $(date)" >> $LOG_FILE
echo "==========================================" >> $LOG_FILE