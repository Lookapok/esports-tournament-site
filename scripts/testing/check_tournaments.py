#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check all tournaments and their data
"""

import requests

def check_all_tournaments():
    """Check all tournaments"""
    print("🔍 檢查所有錦標賽...")
    
    # Check tournament list
    try:
        response = requests.get("https://winnertakesall-tw.onrender.com/api/tournaments/", timeout=30)
        if response.status_code == 200:
            tournaments = response.json()
            print(f"📊 找到 {len(tournaments)} 個錦標賽：")
            for t in tournaments:
                print(f"  - ID {t.get('id')}: {t.get('name')} (狀態: {t.get('status')})")
                
                # Check each tournament detail
                try:
                    detail_url = f"https://winnertakesall-tw.onrender.com/tournaments/{t.get('id')}/"
                    detail_response = requests.get(detail_url, timeout=10)
                    print(f"    狀態碼: {detail_response.status_code}")
                except Exception as e:
                    print(f"    ❌ 無法訪問: {e}")
        else:
            print(f"❌ API 失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    # Also check specific IDs
    print("\n🎯 檢查特定錦標賽 ID...")
    for tid in [1, 9]:
        try:
            url = f"https://winnertakesall-tw.onrender.com/tournaments/{tid}/"
            response = requests.get(url, timeout=10)
            print(f"錦標賽 {tid}: 狀態碼 {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 可訪問")
            elif response.status_code == 404:
                print(f"  ❌ 不存在")
            else:
                print(f"  ⚠️ 其他錯誤")
        except Exception as e:
            print(f"錦標賽 {tid}: ❌ {e}")

if __name__ == "__main__":
    check_all_tournaments()
