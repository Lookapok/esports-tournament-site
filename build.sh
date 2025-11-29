#!/bin/bash
# Render 自動部署腳本
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

# 檢查是否需要從 Docker 遷移資料 (保護模式)
echo "🔍 檢查資料遷移需求..."
echo "⚠️ 資料匯入已停用，保護手動設定的分組資料"
if [ -f "production_data.json" ]; then
    echo "ℹ️ 找到 Docker 資料檔案但不執行匯入（保護現有資料）"
    echo "📊 檔案大小: $(du -h production_data.json)"
    echo "🔒 保護模式：不執行任何資料變更操作"
else
    echo "ℹ️ 沒有 Docker 資料檔案，跳過匯入"
fi

# 檢查並生成統計數據（如果需要）
echo "📊 檢查選手統計數據..."
STATS_COUNT=$(python manage.py shell -c "
from tournaments.models import PlayerGameStat, Game
try:
    stats_count = PlayerGameStat.objects.count()
    games_count = Game.objects.count()
    print(f'{stats_count}')
    if stats_count == 0 and games_count > 0:
        exit(1)  # 需要生成統計數據
    else:
        exit(0)  # 統計數據正常
except Exception as e:
    print('0')
    exit(2)  # 錯誤
" 2>/dev/null)

GENERATE_STATS=$?
if [ $GENERATE_STATS -eq 1 ]; then
    echo "🎯 生成選手統計數據..."
    python manage.py generate_sample_stats 2>&1 || echo "⚠️ 統計數據生成失敗"
elif [ $GENERATE_STATS -eq 0 ]; then
    echo "✅ 選手統計數據已存在 ($STATS_COUNT 筆)"
else
    echo "⚠️ 無法檢查統計數據狀態"
fi

# 驗證資料狀態
echo "🔍 驗證資料狀態..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player, PlayerGameStat
print(f'錦標賽數量: {Tournament.objects.count()}')
print(f'隊伍數量: {Team.objects.count()}')
print(f'選手數量: {Player.objects.count()}')
print(f'選手統計數據: {PlayerGameStat.objects.count()}')
" || echo "⚠️ 資料驗證失敗"

# 檢查 media 文件
echo "📁 檢查 media 文件..."
if [ -d "media/team_logos" ]; then
    echo "✅ team_logos 目錄存在，包含 $(ls media/team_logos | wc -l) 個文件"
else
    echo "ℹ️ team_logos 目錄不存在，將在上傳 logo 時自動建立"
    mkdir -p media/team_logos
fi

echo "🎉 部署完成！WTACS 電競賽事系統已就緒！"
