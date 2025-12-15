#!/usr/bin/env python
"""
資料匯出腳本 - 將本地資料匯出為 JSON 格式
用於從本地開發環境匯出資料到生產環境
"""

import os
import sys
import django
from django.core.management import call_command

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

def export_data():
    """匯出所有資料到 JSON 檔案"""
    try:
        print("🔄 正在匯出資料...")
        
        # 匯出所有資料到 JSON 檔案
        call_command('dumpdata', 
                    '--natural-foreign', 
                    '--natural-primary',
                    '--exclude=contenttypes',
                    '--exclude=auth.permission',
                    '--exclude=sessions.session',
                    '--exclude=admin.logentry',
                    '--output=production_data.json',
                    '--indent=2')
        
        print("✅ 資料匯出完成！檔案位置: production_data.json")
        print("📝 您可以將此檔案上傳到生產環境並執行載入")
        
    except Exception as e:
        print(f"❌ 匯出失敗: {str(e)}")

if __name__ == "__main__":
    export_data()
