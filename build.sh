#!/bin/bash
# Render 自動部署腳本

set -e  # 遇到錯誤就停止

echo "🚀 開始部署 WTACS 電競賽事系統..."

# 更新 pip
echo "📦 更新 pip..."
python -m pip install --upgrade pip

# 強制重新安裝 PostgreSQL 驅動 (多重策略)
echo "📦 安裝 PostgreSQL 驅動..."
python -m pip install --force-reinstall psycopg2-binary==2.9.5

# 備用方案: 嘗試 psycopg (newer version)
echo "📦 嘗試新版 PostgreSQL 驅動..."
python -m pip install --force-reinstall 'psycopg[binary]>=3.1.8' || echo "⚠️ 新版驅動安裝失敗，使用舊版"

# 安裝依賴
echo "📦 安裝 Python 套件..."
if [ -f "requirements.production.txt" ]; then
    python -m pip install -r requirements.production.txt
else
    python -m pip install -r requirements.txt
fi

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
echo "🔍 檢查環境變數..."
echo "DATABASE_URL 是否存在: ${DATABASE_URL:+是}"
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

# 匯入初始資料（強制執行，多次重試）
echo "📊 強制匯入錦標賽資料..."
echo "🔍 檢查資料檔案是否存在..."
if [ -f "production_data.json" ]; then
    echo "✅ production_data.json 檔案存在"
    
    # 多次嘗試匯入資料
    for i in 1 2 3; do
        echo "📊 第 $i 次嘗試匯入資料..."
        if python manage.py load_tournament_data; then
            echo "✅ 資料匯入成功！"
            break
        else
            echo "⚠️ 第 $i 次匯入失敗，$([ $i -lt 3 ] && echo "重試中..." || echo "最終失敗")"
            if [ $i -eq 3 ]; then
                echo "❌ 資料匯入最終失敗，但繼續部署"
            fi
        fi
    done
else
    echo "❌ production_data.json 檔案不存在！"
fi

# 驗證資料匯入結果
echo "🔍 驗證資料匯入結果..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player
print(f'錦標賽數量: {Tournament.objects.count()}')
print(f'隊伍數量: {Team.objects.count()}')
print(f'選手數量: {Player.objects.count()}')
" || echo "⚠️ 資料驗證失敗"

# 檢查 media 文件是否存在
echo "📁 檢查 media 文件..."
if [ -d "media/team_logos" ]; then
    echo "✅ team_logos 目錄存在，包含 $(ls media/team_logos | wc -l) 個文件"
else
    echo "ℹ️ team_logos 目錄不存在，將在上傳 logo 時自動建立"
    mkdir -p media/team_logos
fi

echo "🎉 部署完成！WTACS 電競賽事系統已就緒！"
