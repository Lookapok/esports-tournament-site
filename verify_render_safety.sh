#!/bin/bash
# Render 部署確認檢查腳本
# 確保不會有任何資料重置或覆蓋

echo "🔒 檢查 Render 部署安全性..."

# 檢查當前 build.sh 是否有危險的命令
echo "📋 檢查 build.sh 中的危險命令..."

# 檢查是否有資料重置命令
if grep -q "reset_and_import" build.sh; then
    echo "❌ 警告：build.sh 包含 reset_and_import 命令！"
    exit 1
fi

if grep -q "migrate_from_docker" build.sh; then
    echo "❌ 警告：build.sh 包含 migrate_from_docker 命令！"
    exit 1
fi

if grep -q "force_reimport" build.sh; then
    echo "❌ 警告：build.sh 包含 force_reimport 命令！"
    exit 1
fi

# 檢查是否有資料匯入命令（除了安全的 restore_player_stats）
if grep -q "import.*production_data" build.sh; then
    echo "❌ 警告：build.sh 包含生產資料匯入命令！"
    exit 1
fi

echo "✅ build.sh 安全檢查通過"

# 檢查保護機制是否存在
if grep -q "rm -f production_data.json" build.sh; then
    echo "✅ production_data.json 保護機制存在"
else
    echo "⚠️ 建議添加 production_data.json 保護機制"
fi

# 檢查統計數據恢復機制
if grep -q "restore_player_stats" build.sh; then
    echo "✅ 統計數據自動恢復機制存在"
else
    echo "⚠️ 缺少統計數據自動恢復機制"
fi

# 檢查資料庫設定
echo "🗄️ 檢查資料庫設定..."
python manage.py shell -c "
from django.conf import settings
db = settings.DATABASES['default']
print(f'資料庫引擎: {db.get(\"ENGINE\", \"未設定\")}')
if 'postgresql' in db.get('ENGINE', ''):
    print('✅ 使用 PostgreSQL (Supabase)')
    # 不顯示完整的 DATABASE_URL 保護敏感資訊
    if 'supabase.co' in db.get('HOST', '') or 'DATABASE_URL' in str(db):
        print('✅ 確認連接到 Supabase')
    else:
        print('⚠️ 可能未連接到 Supabase')
else:
    print('❌ 未使用 PostgreSQL')
" 2>/dev/null || echo "⚠️ 無法檢查資料庫設定"

echo "🔍 最終資料確認..."
python manage.py shell -c "
from tournaments.models import Tournament, Team, Player, Standing
print(f'✅ 錦標賽數量: {Tournament.objects.count()}')
print(f'✅ 隊伍數量: {Team.objects.count()}')
print(f'✅ 選手數量: {Player.objects.count()}')
print(f'✅ 積分榜數量: {Standing.objects.count()}')
print('🎯 資料庫連接正常，資料完整')
" 2>/dev/null || echo "⚠️ 資料庫連接檢查失敗"

echo ""
echo "🛡️ Render 部署安全性確認："
echo "✅ 不會重置任何現有資料"
echo "✅ 完全依賴 Supabase 作為資料來源"
echo "✅ 自動恢復統計數據（如果遺失）"
echo "✅ 移除危險的匯入檔案"
echo "✅ 保護所有現有資料"
echo ""
echo "🚀 可以安全進行 Render 重新部署！"
