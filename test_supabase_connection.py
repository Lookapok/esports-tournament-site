#!/usr/bin/env python
"""
Supabase 資料庫連線測試腳本
用於驗證 Supabase PostgreSQL 資料庫連線是否正常
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_supabase_connection():
    """測試 Supabase 資料庫連線"""
    
    # 請在這裡替換成您從 Supabase 取得的連線字串
    # 格式：postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
    DATABASE_URL = input("請輸入您的 Supabase 資料庫連線字串: ").strip()
    
    if not DATABASE_URL:
        print("❌ 請提供有效的資料庫連線字串！")
        return False
    
    try:
        print("🔄 正在測試連線到 Supabase...")
        
        # 解析連線字串
        url = urlparse(DATABASE_URL)
        
        print(f"📡 連接到主機: {url.hostname}")
        print(f"🏷️  資料庫名稱: {url.path[1:]}")
        print(f"👤 使用者: {url.username}")
        
        # 建立連線
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 測試查詢
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print(f"✅ 連線成功！")
        print(f"📊 PostgreSQL 版本: {db_version[0]}")
        
        # 檢查是否可以建立表格
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            );
        """)
        
        # 插入測試資料
        cursor.execute("""
            INSERT INTO connection_test (message) 
            VALUES ('WTACS 電競賽事系統連線測試成功！');
        """)
        
        # 查詢測試資料
        cursor.execute("SELECT COUNT(*) FROM connection_test;")
        count = cursor.fetchone()[0]
        
        print(f"🗄️  資料庫操作測試成功！測試記錄數: {count}")
        
        # 清理測試資料
        cursor.execute("DROP TABLE connection_test;")
        
        # 提交並關閉
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Supabase 資料庫連線完全正常！")
        print("📝 您可以將此連線字串用於部署設定。")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 連線失敗: {str(e)}")
        print("🔍 請檢查：")
        print("   1. 連線字串格式是否正確")
        print("   2. 密碼是否正確")
        print("   3. 網路連線是否正常")
        print("   4. Supabase 專案是否已完成建立")
        return False
        
    except Exception as e:
        print(f"❌ 發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 WTACS Supabase 連線測試工具")
    print("=" * 50)
    
    if test_supabase_connection():
        print("\n✅ 測試完成！您的 Supabase 資料庫已準備就緒。")
    else:
        print("\n❌ 測試失敗！請檢查設定後重試。")
