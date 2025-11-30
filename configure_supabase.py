#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置 esports_project 的 Supabase 連接
"""

def update_env_with_supabase():
    """更新 .env 檔案以包含 Supabase 連接"""
    
    print("📝 配置 Supabase 連接到 esports_project")
    print("=" * 50)
    
    # 讀取現有的 .env 檔案
    env_file_path = ".env"
    
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""
    
    print("📋 當前 .env 內容:")
    print(existing_content if existing_content.strip() else "(空檔案)")
    print()
    
    # 檢查是否已經有 DATABASE_URL
    if 'DATABASE_URL=' in existing_content:
        print("⚠️ .env 檔案中已經存在 DATABASE_URL")
        print("如果你想要更新它，請手動編輯 .env 檔案")
        return
    
    print("💡 請提供你的 Supabase DATABASE_URL")
    print("格式: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres")
    print()
    print("你可以從 Supabase 控制台取得這個連接字串：")
    print("1. https://supabase.com/dashboard")
    print("2. 選擇你的專案")
    print("3. Settings → Database → Connection string")
    print()
    
    # 暫停，讓使用者手動添加 DATABASE_URL
    print("🔧 一旦你有了 DATABASE_URL，請：")
    print("1. 編輯 esports_project/.env 檔案")
    print("2. 添加這一行：DATABASE_URL=你的完整Supabase連接字串")
    print("3. 確保沒有額外的空格或引號")
    print()
    print("範例：")
    print("DATABASE_URL=postgresql://postgres.abcdefg:yourpassword@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")

if __name__ == "__main__":
    update_env_with_supabase()
