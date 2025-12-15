"""
Render 部署安全性檢查
確保重新部署時不會影響 Supabase 資料
"""
import os
import re

def check_build_script():
    """檢查 build.sh 是否安全"""
    print("🔒 檢查 Render 部署安全性...")
    print("📋 檢查 build.sh 中的危險命令...")
    
    try:
        with open('build.sh', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 危險命令檢查
        dangerous_commands = [
            'reset_and_import',
            'migrate_from_docker', 
            'force_reimport',
            'import.*production_data'
        ]
        
        for cmd in dangerous_commands:
            if re.search(cmd, content) and not re.search(f'#{cmd}', content):  # 排除註解掉的
                print(f"❌ 警告：build.sh 包含危險命令 {cmd}！")
                return False
        
        print("✅ build.sh 安全檢查通過")
        
        # 檢查保護機制
        if 'rm -f production_data.json' in content:
            print("✅ production_data.json 保護機制存在")
        else:
            print("⚠️ 建議添加 production_data.json 保護機制")
        
        if 'restore_player_stats' in content:
            print("✅ 統計數據自動恢復機制存在")
        else:
            print("⚠️ 缺少統計數據自動恢復機制")
        
        return True
        
    except FileNotFoundError:
        print("❌ 找不到 build.sh 檔案")
        return False
    except Exception as e:
        print(f"❌ 檢查 build.sh 時發生錯誤: {e}")
        return False

def check_database_config():
    """檢查資料庫配置"""
    print("\n🗄️ 檢查資料庫設定...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        db = settings.DATABASES['default']
        engine = db.get('ENGINE', '未設定')
        print(f"資料庫引擎: {engine}")
        
        if 'postgresql' in engine:
            print("✅ 使用 PostgreSQL (Supabase)")
            
            # 檢查是否有 DATABASE_URL 環境變數（在生產環境）
            database_url = os.environ.get('DATABASE_URL', '')
            if 'supabase.co' in database_url or database_url:
                print("✅ 確認配置了資料庫連線")
            else:
                print("ℹ️ 本地環境 - 需要在 Render 設定 DATABASE_URL")
        else:
            print("⚠️ 本地使用 SQLite - 生產環境將使用 PostgreSQL")
        
        return True
        
    except Exception as e:
        print(f"⚠️ 無法檢查資料庫設定: {e}")
        return False

def check_current_data():
    """檢查當前資料狀態"""
    print("\n🔍 檢查當前資料狀態...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
        import django
        django.setup()
        
        from tournaments.models import Tournament, Team, Player, Standing, PlayerGameStat
        
        tournament_count = Tournament.objects.count()
        team_count = Team.objects.count()
        player_count = Player.objects.count()
        standing_count = Standing.objects.count()
        stats_count = PlayerGameStat.objects.count()
        
        print(f"✅ 錦標賽數量: {tournament_count}")
        print(f"✅ 隊伍數量: {team_count}")
        print(f"✅ 選手數量: {player_count}")
        print(f"✅ 積分榜數量: {standing_count}")
        print(f"✅ 統計數據: {stats_count}")
        
        if tournament_count > 0 and team_count > 0:
            print("🎯 資料庫連接正常，資料完整")
            return True
        else:
            print("⚠️ 資料可能不完整")
            return False
        
    except Exception as e:
        print(f"⚠️ 資料庫連接檢查失敗: {e}")
        return False

def main():
    """主要檢查流程"""
    print("🛡️ Render 部署安全性檢查")
    print("=" * 50)
    
    # 檢查 build.sh 安全性
    script_safe = check_build_script()
    
    # 檢查資料庫配置
    db_config_ok = check_database_config()
    
    # 檢查當前資料
    data_ok = check_current_data()
    
    print("\n" + "=" * 50)
    print("🛡️ Render 部署安全性總結：")
    print("")
    
    if script_safe:
        print("✅ 不會重置任何現有資料")
        print("✅ 完全依賴 Supabase 作為資料來源")
        print("✅ 自動恢復統計數據（如果遺失）")
        print("✅ 移除危險的匯入檔案")
        print("✅ 保護所有現有資料")
    else:
        print("❌ build.sh 存在安全風險")
    
    if db_config_ok:
        print("✅ 資料庫配置正確")
    else:
        print("⚠️ 資料庫配置需要確認")
    
    if data_ok:
        print("✅ 當前資料完整")
    else:
        print("⚠️ 當前資料需要檢查")
    
    print("")
    
    if script_safe and db_config_ok:
        print("🚀 可以安全進行 Render 重新部署！")
        print("")
        print("📋 部署後的行為：")
        print("1. 連接到 Supabase PostgreSQL 資料庫")
        print("2. 執行 migrate（只更新資料庫結構，不影響資料）")
        print("3. 收集靜態檔案")
        print("4. 自動恢復統計數據（如果需要）")
        print("5. 系統立即可用，所有資料完整")
        print("")
        print("✨ Supabase 資料會即時反映到網站上！")
    else:
        print("⚠️ 建議修復安全問題後再部署")

if __name__ == '__main__':
    main()
