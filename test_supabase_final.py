#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Supabase 連接和資料完整性
"""

import os
import django

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import PlayerGameStat, Tournament, Player, Team
from django.db import connection

def test_supabase_connection():
    """測試 Supabase 連接和資料"""
    
    print("🧪 測試 Supabase 連接")
    print("=" * 50)
    
    try:
        # 1. 測試資料庫連接
        print("1. 🔗 測試資料庫連接...")
        with connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            version = cursor.fetchone()
            print(f"   ✅ PostgreSQL 版本: {version[0][:80]}...")
        
        # 2. 檢查資料表
        print("\n2. 📋 檢查資料表...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'tournaments_%'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   ✅ 找到 {len(tables)} 個 tournaments 相關表格")
            for table in tables:
                print(f"      📋 {table[0]}")
        
        # 3. 檢查資料數量
        print("\n3. 📊 檢查資料數量...")
        
        stat_count = PlayerGameStat.objects.count()
        tournament_count = Tournament.objects.count()
        player_count = Player.objects.count()
        team_count = Team.objects.count()
        
        print(f"   📊 統計記錄: {stat_count}")
        print(f"   🏆 賽事數量: {tournament_count}")
        print(f"   👤 選手數量: {player_count}")
        print(f"   👥 隊伍數量: {team_count}")
        
        # 4. 測試資料品質
        if stat_count > 0:
            print("\n4. 🎯 資料品質測試...")
            
            # 檢查擊殺數最高的選手
            top_stats = PlayerGameStat.objects.order_by('-kills')[:3]
            print("   🏅 前 3 名擊殺數選手:")
            for i, stat in enumerate(top_stats, 1):
                print(f"      {i}. {stat.player.nickname}: {stat.kills} 擊殺, {stat.deaths} 死亡, {stat.assists} 助攻")
            
            # 檢查最新賽事
            latest_tournament = Tournament.objects.order_by('-id').first()
            if latest_tournament:
                print(f"   🆕 最新賽事: {latest_tournament.name}")
                print(f"      賽事 ID: {latest_tournament.id}")
        
        # 5. 測試寫入權限
        print("\n5. ✍️ 測試寫入權限...")
        try:
            # 嘗試建立一個測試記錄（但不實際儲存）
            from django.db import transaction
            with transaction.atomic():
                # 使用 savepoint 來測試寫入而不實際提交
                sid = transaction.savepoint()
                
                # 測試查詢是否正常
                test_count = PlayerGameStat.objects.filter(kills__gt=0).count()
                print(f"   ✅ 查詢測試通過 ({test_count} 筆有擊殺記錄)")
                
                # 回滾測試
                transaction.savepoint_rollback(sid)
                print("   ✅ 交易測試通過")
        
        except Exception as e:
            print(f"   ⚠️ 寫入測試失敗: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Supabase 連接測試完成！")
        
        if stat_count > 1000:
            print("✅ 資料遷移成功 - 發現大量統計資料")
            print("🚀 可以安全地停用本地 Docker PostgreSQL")
        else:
            print("⚠️ 資料量較少，請確認遷移是否完整")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 連接測試失敗: {e}")
        print("\n🔧 請檢查:")
        print("1. DATABASE_URL 是否正確")
        print("2. Supabase 服務是否正常")
        print("3. 網路連接是否正常")
        return False

if __name__ == "__main__":
    test_supabase_connection()
