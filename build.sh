#!/bin/bash
# Render 自動部署腳本

set -e  # 遇到錯誤就停止

echo "🚀 開始部署 Winner Takes All 錦標賽系統..."

# 安裝依賴
echo "📦 安裝 Python 套件..."
pip install -r requirements.txt

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
python manage.py migrate

# 載入初始資料（如果資料庫為空）
echo "📊 檢查並載入初始錦標賽資料..."
python manage.py load_initial_data

# 收集靜態檔案
echo "🎨 收集靜態檔案..."
python manage.py collectstatic --noinput

echo "🎉 部署完成！Winner Takes All 錦標賽系統已就緒！"
