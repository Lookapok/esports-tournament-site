# 這是 Render.com 部署腳本
#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝 Python 套件
pip install --upgrade pip
pip install -r requirements.txt

# 收集靜態檔案
python manage.py collectstatic --no-input

# 執行資料庫遷移
python manage.py migrate

echo "部署完成！"
