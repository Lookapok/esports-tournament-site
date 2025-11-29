#!/usr/bin/env python
"""
動態 URL 測試腳本
"""

import requests

def test_custom_url():
    """測試自訂 URL"""
    
    print("🔍 URL 測試工具")
    print("=" * 40)
    
    # 請用戶輸入實際的 URL
    url = input("請輸入您在 Render 上的實際網站 URL: ").strip()
    
    if not url:
        print("❌ 未提供 URL")
        return
    
    if not url.startswith('http'):
        url = f"https://{url}"
    
    print(f"\n🔄 測試 URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"✅ 回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 網站運行正常！")
            
            # 測試其他端點
            endpoints = ["/admin/", "/api/", "/tournaments/"]
            for endpoint in endpoints:
                try:
                    test_url = url.rstrip('/') + endpoint
                    test_response = requests.get(test_url, timeout=10)
                    print(f"   {endpoint}: {test_response.status_code}")
                except:
                    print(f"   {endpoint}: 連線失敗")
                    
        elif response.status_code == 404:
            print("⚠️  可能原因：")
            print("   1. URL 不正確")
            print("   2. 服務還在部署中")
            print("   3. Root Directory 設定問題")
            
        else:
            print(f"⚠️  收到非預期的狀態碼: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ 連線逾時 - 服務可能還在啟動中")
    except requests.exceptions.ConnectionError:
        print("🌐 連線錯誤 - 請檢查 URL 是否正確")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

if __name__ == "__main__":
    test_custom_url()
