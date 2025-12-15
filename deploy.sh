#!/bin/bash

echo "🚀 開始部署 WTACS 電競賽事系統到 Render..."

# 更新 pip
echo "📦 更新 pip..."
pip install --upgrade pip

# 安裝相依套件
echo "📦 安裝相依套件..."
pip install -r requirements.txt

# 收集靜態檔案
echo "📁 收集靜態檔案..."
python manage.py collectstatic --noinput

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
python manage.py migrate --noinput

# 建立超級使用者（如果需要的話）
echo "👤 檢查是否需要建立管理員帳戶..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@wtacs.com', 'admin123456')
    print('✅ 管理員帳戶已建立: admin / admin123456')
else:
    print('ℹ️ 管理員帳戶已存在')
"

echo "✅ 部署準備完成！"
