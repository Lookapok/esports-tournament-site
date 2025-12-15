#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
診斷錦標賽 9 的分組和比賽數據
"""

import requests

def diagnose_tournament_9():
    """診斷錦標賽 9 的詳細數據"""
    
    print("🔍 診斷錦標賽 9 的分組和比賽數據...")
    
    # 檢查分組數據
    url = "https://winnertakesall-tw.onrender.com/api/diagnose-tournament-9/"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功獲取診斷數據")
            
            print(f"\n📊 錦標賽 9 統計:")
            print(f"  - 分組數: {data.get('group_count', 0)}")
            print(f"  - 比賽數: {data.get('match_count', 0)}")
            print(f"  - 隊伍數: {data.get('team_count', 0)}")
            
            print(f"\n🗂️  分組詳情:")
            for group in data.get('groups', []):
                print(f"  - {group['name']}: {group['team_count']} 支隊伍")
                for team in group['teams']:
                    print(f"    • {team}")
            
            print(f"\n⚔️  比賽詳情:")
            for match in data.get('matches', [])[:10]:  # 只顯示前10場
                team1 = match.get('team1', '待定')
                team2 = match.get('team2', '待定')
                status = match.get('status', '未知')
                print(f"  - R{match.get('round_number', 0)}: {team1} vs {team2} ({status})")
            
        else:
            print(f"❌ 請求失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    diagnose_tournament_9()
