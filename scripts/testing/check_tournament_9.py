#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check tournament 9 groups and matches
"""

import requests

def check_tournament_9():
    """Check tournament 9 details"""
    print("🎯 檢查錦標賽 9 的詳細數據...")
    
    try:
        # Get tournament 9 main page and check content
        response = requests.get("https://winnertakesall-tw.onrender.com/tournaments/9/", timeout=30)
        if response.status_code == 200:
            content = response.text
            print("✅ 錦標賽 9 可正常訪問")
            
            # Check for group content
            groups = ['A組', 'B組', 'C組', 'D組']
            for group in groups:
                if group in content:
                    print(f"  ✅ 找到 {group}")
                else:
                    print(f"  ❌ 沒有找到 {group}")
            
            # Check for match content
            if '賽程' in content:
                print("  ✅ 找到賽程內容")
            else:
                print("  ❌ 沒有找到賽程內容")
                
            if '支隊伍' in content:
                print("  ✅ 找到隊伍統計")
            else:
                print("  ❌ 沒有找到隊伍統計")
                
            if '積分榜' in content:
                print("  ✅ 找到積分榜")
            else:
                print("  ❌ 沒有找到積分榜")
                
            # Check if there are any matches displayed
            if 'vs' in content:
                print("  ✅ 找到比賽對戰")
                vs_count = content.count(' vs ')
                print(f"    比賽對戰數量: {vs_count}")
            else:
                print("  ❌ 沒有找到比賽對戰")
                
        else:
            print(f"❌ 錦標賽 9 訪問失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    check_tournament_9()
