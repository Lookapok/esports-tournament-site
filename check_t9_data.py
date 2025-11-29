#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check tournament 9 database status
"""

import requests

def check_tournament_9_data():
    """Check tournament 9 in database"""
    print("🗄️ 檢查錦標賽 9 的數據庫狀況...")
    
    try:
        # Check health with focus on tournament 9
        health_response = requests.get("https://winnertakesall-tw.onrender.com/health/", timeout=30)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("📊 數據庫總計:")
            print(f"  - 錦標賽: {health_data.get('tournament_count', 0)}")
            print(f"  - 隊伍: {health_data.get('team_count', 0)}")
            print(f"  - 分組: {health_data.get('group_count', 0)}")
            print(f"  - 比賽: {health_data.get('match_count', 0)}")
            print(f"  - 積分榜: {health_data.get('standing_count', 0)}")
            print(f"  - 選手統計: {health_data.get('playergamestat_count', 0)}")
            
            # The issue is that health check shows total across all tournaments
            # We need to identify which data belongs to tournament 9
            
        else:
            print(f"❌ 健康檢查失敗: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    # Since tournament 1 gives 500 error and tournament 9 works,
    # the issue might be that most data is in tournament 9 but display logic fails
    
    print("\n💡 分析:")
    print("- 錦標賽 9 可訪問但只顯示 A 組")
    print("- 錦標賽 1 返回 500 錯誤") 
    print("- 資料庫顯示有 4 個分組和 144 場比賽")
    print("- 問題：為什麼只顯示 A 組？其他分組和賽程哪裡去了？")

if __name__ == "__main__":
    check_tournament_9_data()
