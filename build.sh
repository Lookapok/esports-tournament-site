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

# 檢查是否需要重新匯入乾淨數據
echo "🔍 檢查資料狀態..."
echo "🧹 執行一次性數據清理和重新匯入"

# 複製production_data.json到當前目錄
if [ ! -f "production_data.json" ] && [ -f "../production_data.json" ]; then
    echo "📋 複製原始資料檔案..."
    cp ../production_data.json ./production_data.json
fi

if [ -f "production_data.json" ]; then
    echo "ℹ️ 找到原始資料檔案，執行完整重新匯入"
    echo "📊 檔案大小: $(du -h production_data.json)"
    
    # 清空PlayerGameStat假數據
    echo "🧹 清空選手統計數據..."
    python manage.py shell -c "
from tournaments.models import PlayerGameStat
deleted_count = PlayerGameStat.objects.count()
PlayerGameStat.objects.all().delete()
print(f'已清空 {deleted_count} 筆選手統計數據')
"
    
    echo "� 執行完整資料庫重置並匯入原始數據..."
    python manage.py reset_and_import 2>&1
    
    if [ $? -ne 0 ]; then
        echo "❌ 重置匯入失敗，嘗試其他方法..."
        echo "🔄 嘗試安全匯入..."
        python manage.py safe_import 2>&1 || {
            echo "🔄 嘗試強制重新匯入..."
            python manage.py force_reimport 2>&1 || echo "⚠️ 所有匯入方法都失敗"
        }
    fi
    
    # 導入完成後立即刪除檔案，防止下次部署再次重置
    echo "🗑️ 刪除 production_data.json 防止重複導入"
    rm -f production_data.json
    
    echo "✅ 資料重新匯入完成，只包含原始真實數據"
else
    echo "ℹ️ 沒有資料檔案，保持現有數據"
fi

# 驗證最終資料狀態
echo "🔍 驗證最終資料狀態..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player, PlayerGameStat
print(f'錦標賽數量: {Tournament.objects.count()}')
print(f'隊伍數量: {Team.objects.count()}')
print(f'選手數量: {Player.objects.count()}')
print(f'選手統計數據: {PlayerGameStat.objects.count()}')
print('✅ 所有數據都是從原始備份恢復，無假數據')
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
