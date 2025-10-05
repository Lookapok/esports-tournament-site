#!/usr/bin/env python
import os
import sys
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.db import connection

def check_local_data():
    print("=== 檢查本地 PostgreSQL 資料庫狀態 ===")
    
    try:
        with connection.cursor() as cursor:
            # 檢查資料庫連線
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL 連線成功")
            print(f"📝 版本: {version}")
            
            # 檢查所有資料表
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\n=== 資料庫中的資料表 ({len(tables)}) ===")
            for table in tables:
                print(f"  📋 {table}")
                
            # 檢查 tournaments 相關資料表的資料量
            tournament_tables = [
                'tournaments_tournament',
                'tournaments_team', 
                'tournaments_player',
                'tournaments_group',
                'tournaments_match',
                'tournaments_game'
            ]
            
            print(f"\n=== 本地資料統計 ===")
            total_records = 0
            for table in tournament_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    emoji = "📊" if count > 0 else "📭"
                    print(f"  {emoji} {table}: {count} 筆記錄")
                    total_records += count
                else:
                    print(f"  ❌ {table}: 資料表不存在")
                    
            print(f"\n🔢 總記錄數: {total_records}")
            
            if total_records == 0:
                print("\n⚠️  本地資料庫沒有資料，需要恢復！")
            else:
                print(f"\n✅ 本地資料庫有 {total_records} 筆資料")
                
    except Exception as e:
        print(f"❌ 檢查本地資料庫時發生錯誤: {e}")

if __name__ == "__main__":
    check_local_data()
