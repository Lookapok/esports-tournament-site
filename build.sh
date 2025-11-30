#!/bin/bash
# Render 自動部署腳本 - 緊急保護版本
# Force rebuild: 2025-11-30

echo "🚀 開始部署 WTACS 電競賽事系統..."

# 更新 pip
echo "📦 更新 pip..."
python -m pip install --upgrade pip

# 強制重新安裝 PostgreSQL 驅動
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

# 緊急保護模式
echo "🔍 檢查資料狀態..."
echo "🔒 緊急保護模式：完全停用所有資料匯入功能"

# 移除任何可能觸發重置的檔案
if [ -f "production_data.json" ]; then
    echo "🗑️ 移除 production_data.json 防止意外重置"
    rm -f production_data.json
fi

echo "🛡️ 所有資料變更功能已停用，保護現有數據"

# 檢查並恢復統計數據
echo "📊 檢查統計數據狀態..."
STATS_COUNT=$(python manage.py shell -c "
from tournaments.models import PlayerGameStat
print(PlayerGameStat.objects.count())
" 2>/dev/null || echo "0")

echo "當前統計數據: $STATS_COUNT 筆"

if [ "$STATS_COUNT" = "0" ]; then
    echo "🔄 統計數據為空，自動恢復..."
    python manage.py restore_player_stats --real-data-only
    
    # 驗證恢復結果
    NEW_STATS_COUNT=$(python manage.py shell -c "
from tournaments.models import PlayerGameStat
print(PlayerGameStat.objects.count())
" 2>/dev/null || echo "0")
    
    echo "恢復後統計數據: $NEW_STATS_COUNT 筆"
    
    if [ "$NEW_STATS_COUNT" != "0" ]; then
        echo "✅ 統計數據恢復成功"
    else
        echo "❌ 統計數據恢復失敗"
    fi
else
    echo "✅ 統計數據已存在，無需恢復"
fi

# 驗證最終資料狀態
echo "🔍 驗證最終資料狀態..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player, PlayerGameStat
print(f'錦標賽數量: {Tournament.objects.count()}')
print(f'隊伍數量: {Team.objects.count()}')
print(f'選手數量: {Player.objects.count()}')
print(f'選手統計數據: {PlayerGameStat.objects.count()}')
if PlayerGameStat.objects.count() > 0:
    print('✅ 統計數據已恢復')
else:
    print('⚠️ 統計數據為空，需要手動恢復')
" || echo "⚠️ 資料驗證失敗"

# 檢查 media 文件
echo "📁 檢查 media 文件..."
if [ -d "media/team_logos" ]; then
    echo "✅ team_logos 目錄存在，包含 $(ls media/team_logos | wc -l) 個文件"
else
    echo "ℹ️ team_logos 目錄不存在，將在上傳 logo 時自動建立"
    mkdir -p media/team_logos
fi

echo "🎉 緊急恢復部署完成！"
echo "🔒 未來部署將完全保護數據，不再執行任何重置操作"
