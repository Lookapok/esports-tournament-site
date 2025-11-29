#!/bin/bash
# Render 自動部署腳本

set -e  # 遇到錯誤就停止

echo "🚀 開始部署 WTACS 電競賽事系統..."

# 更新 pip
echo "📦 更新 pip..."
pip install --upgrade pip

# 安裝依賴
echo "📦 安裝 Python 套件..."
if [ -f "requirements.production.txt" ]; then
    pip install -r requirements.production.txt
else
    pip install -r requirements.txt
fi

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
python manage.py migrate

# 收集靜態檔案
echo "🎨 收集靜態檔案..."
python manage.py collectstatic --noinput

# 建立超級使用者（如果不存在）
echo "👤 檢查管理員帳戶..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@wtacs.com', 'wtacs2024')
    print('✅ 管理員帳戶已建立')
else:
    print('ℹ️ 管理員帳戶已存在')
" || echo "⚠️ 建立管理員帳戶失敗，請稍後手動建立"

# 匯入初始資料（如果資料庫為空）
echo "📊 檢查並匯入錦標賽資料..."
python manage.py shell -c "
from tournaments.models import Tournament
if Tournament.objects.count() == 0:
    print('資料庫為空，開始匯入資料...')
    from django.core.management import call_command
    call_command('load_tournament_data')
else:
    print('資料庫已有資料，跳過匯入')
" || echo "⚠️ 資料匯入檢查失敗"

# 檢查 media 文件是否存在
echo "📁 檢查 media 文件..."
if [ -d "media/team_logos" ]; then
    echo "✅ team_logos 目錄存在，包含 $(ls media/team_logos | wc -l) 個文件"
else
    echo "ℹ️ team_logos 目錄不存在，將在上傳 logo 時自動建立"
    mkdir -p media/team_logos
fi

echo "🎉 部署完成！WTACS 電競賽事系統已就緒！"
