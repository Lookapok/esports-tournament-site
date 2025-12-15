#!/usr/bin/env python3
"""
緊急恢復原始數據腳本
使用Django管理命令恢復完整的原始數據
"""
import os
import django

# 設置Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.core import management
from tournaments.models import *
import json

def emergency_restore():
    """緊急恢復原始數據"""
    print("🚨 緊急恢復原始數據")
    print("=" * 50)
    
    # 檢查當前狀態
    print(f"當前數據狀態:")
    print(f"  選手: {Player.objects.count()}")
    print(f"  隊伍: {Team.objects.count()}")
    print(f"  賽事: {Tournament.objects.count()}")
    print(f"  統計: {PlayerGameStat.objects.count()}")
    
    # 檢查是否有備份檔案
    backup_files = [
        "../production_data.json",
        "production_data.json",
        "backup_data.json"
    ]
    
    data_file = None
    for file_path in backup_files:
        if os.path.exists(file_path):
            data_file = file_path
            print(f"✅ 找到備份檔案: {file_path}")
            break
    
    if not data_file:
        print("❌ 找不到任何備份檔案")
        print("可用的恢復選項:")
        print("1. 手動上傳 production_data.json")
        print("2. 使用管理後台重新建立數據")
        return
    
    # 顯示備份檔案資訊
    file_size = os.path.getsize(data_file)
    print(f"📊 備份檔案大小: {file_size:,} bytes")
    
    # 詢問是否執行恢復
    confirm = input("\n確定要執行完整資料恢復嗎? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 已取消恢復操作")
        return
    
    try:
        # 複製檔案到當前目錄
        if data_file != "production_data.json":
            import shutil
            shutil.copy2(data_file, "production_data.json")
            print("📋 已複製備份檔案")
        
        # 執行恢復
        print("\n🔄 開始恢復數據...")
        
        # 嘗試使用 reset_and_import
        try:
            management.call_command('reset_and_import')
            print("✅ 使用 reset_and_import 恢復成功")
        except Exception as e:
            print(f"❌ reset_and_import 失敗: {e}")
            
            # 嘗試 safe_import
            try:
                management.call_command('safe_import')
                print("✅ 使用 safe_import 恢復成功")
            except Exception as e:
                print(f"❌ safe_import 失敗: {e}")
                
                # 嘗試 force_reimport
                try:
                    management.call_command('force_reimport')
                    print("✅ 使用 force_reimport 恢復成功")
                except Exception as e:
                    print(f"❌ 所有恢復方法都失敗: {e}")
                    return
        
        # 清理恢復檔案
        if os.path.exists("production_data.json"):
            os.remove("production_data.json")
            print("🗑️ 已清理恢復檔案")
        
        # 驗證恢復結果
        print("\n📊 恢復後數據狀態:")
        print(f"  選手: {Player.objects.count()}")
        print(f"  隊伍: {Team.objects.count()}")
        print(f"  賽事: {Tournament.objects.count()}")
        print(f"  統計: {PlayerGameStat.objects.count()}")
        
        if PlayerGameStat.objects.count() > 0:
            print("\n✅ 恢復成功！統計數據已恢復")
            
            # 顯示一些樣本數據
            sample_stats = PlayerGameStat.objects.select_related('player', 'team')[:3]
            print("\n樣本統計數據:")
            for stat in sample_stats:
                print(f"  {stat.player.name} ({stat.team.name}): K{stat.kills} D{stat.deaths} ACS{stat.acs}")
        else:
            print("\n⚠️ 統計數據仍為空，可能需要手動處理")
        
    except Exception as e:
        print(f"❌ 恢復過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    emergency_restore()
