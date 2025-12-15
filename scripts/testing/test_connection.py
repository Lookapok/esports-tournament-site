#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test database connection and basic operations
"""

import os
import django
from django.conf import settings

# 設定Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

def test_connection():
    try:
        from django.db import connection
        from tournaments.models import Tournament, Team, Player
        
        print("🔗 Testing database connection...")
        
        # 測試基本連接
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # 測試表格存在
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public' AND table_name LIKE 'tournaments_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📊 Tournament tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 測試基本查詢
        print(f"\n📈 Current data counts:")
        print(f"  - Tournaments: {Tournament.objects.count()}")
        print(f"  - Teams: {Team.objects.count()}")
        print(f"  - Players: {Player.objects.count()}")
        
        # 測試寫入權限
        print(f"\n✍️  Testing write permissions...")
        try:
            # 嘗試創建一個測試錦標賽
            test_tournament = Tournament.objects.create(
                name="連接測試",
                game="Test",
                status="testing"
            )
            print(f"✅ Write test successful - created tournament ID: {test_tournament.id}")
            
            # 清理測試資料
            test_tournament.delete()
            print(f"✅ Cleanup successful")
            
        except Exception as e:
            print(f"❌ Write test failed: {e}")
        
        print(f"\n🎯 Database connection test completed!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_connection()
