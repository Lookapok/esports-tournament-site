#!/bin/bash
# Render 自動部署腳本
# Force rebuild: 2025-11-29 23:00

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

# 運行診斷檢查
echo "🔍 運行資料庫診斷..."
python manage.py diagnose 2>&1

# 強制執行資料庫遷移
echo "🗄️ 檢查並執行資料庫遷移..."
python manage.py makemigrations tournaments --noinput
python manage.py migrate --noinput

# 檢查是否需要從 Docker 遷移資料
echo "🔍 檢查資料遷移需求..."
if [ -f "production_data.json" ]; then
    echo "✅ 找到 Docker 資料檔案"
    echo "📊 檔案大小: $(du -h production_data.json)"
    
    echo "�️ 執行完整資料庫重置並匯入Docker資料..."
    python manage.py reset_and_import 2>&1
    
    if [ $? -ne 0 ]; then
        echo "❌ 重置匯入失敗，嘗試其他方法..."
        echo "� 嘗試安全匯入..."
        python manage.py safe_import 2>&1 || {
            echo "🔄 嘗試強制重新匯入..."
            python manage.py force_reimport 2>&1 || echo "⚠️ 所有匯入方法都失敗"
        }
    fi
else
    echo "ℹ️ 沒有 Docker 資料檔案，跳過匯入"
fi

# 驗證資料匯入結果
echo "🔍 驗證資料匯入結果..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player, PlayerGameStat
print(f'錦標賽數量: {Tournament.objects.count()}')
print(f'隊伍數量: {Team.objects.count()}')
print(f'選手數量: {Player.objects.count()}')
print(f'選手統計數據: {PlayerGameStat.objects.count()}')
" || echo "⚠️ 資料驗證失敗"

# 生成範例選手統計數據（如果沒有的話）
echo "📊 檢查選手統計數據..."
STATS_COUNT=$(python manage.py shell -c "from tournaments.models import PlayerGameStat; print(PlayerGameStat.objects.count())" 2>/dev/null || echo "0")
if [ "$STATS_COUNT" = "0" ]; then
    echo "🎯 生成範例選手統計數據..."
    python manage.py generate_sample_stats || echo "⚠️ 生成範例統計數據失敗"
else
    echo "✅ 選手統計數據已存在 ($STATS_COUNT 筆)"
fi

# 檢查 media 文件是否存在
echo "📁 檢查 media 文件..."
if [ -d "media/team_logos" ]; then
    echo "✅ team_logos 目錄存在，包含 $(ls media/team_logos | wc -l) 個文件"
else
    echo "ℹ️ team_logos 目錄不存在，將在上傳 logo 時自動建立"
    mkdir -p media/team_logos
fi

echo "🎉 部署完成！WTACS 電競賽事系統已就緒！"
