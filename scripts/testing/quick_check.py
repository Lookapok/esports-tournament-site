#!/usr/bin/env python3
"""
快速檢查生產網站狀態
"""
import requests
import time

def check_website_status():
    """檢查網站各個頁面的狀態"""
    base_url = "https://winnertakesall-tw.onrender.com"
    
    pages = [
        "/",
        "/teams/",
        "/tournaments/9/",
        "/tournaments/9/stats/",
        "/stats/"
    ]
    
    print("🔍 檢查網站狀態...")
    print(f"🌐 基礎URL: {base_url}")
    print("=" * 50)
    
    for page in pages:
        try:
            url = f"{base_url}{page}"
            print(f"📄 檢查: {page}")
            
            response = requests.get(url, timeout=10)
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text.lower()
                # 檢查是否有選手數據的指標
                if "選手" in content or "player" in content:
                    if "目前尚無選手資料" in content or "no players" in content:
                        print("   ❌ 沒有選手數據")
                    else:
                        print("   ✅ 有選手數據")
                
                # 檢查是否有賽程數據
                if "賽程" in content or "schedule" in content:
                    if "此分組尚無賽程" in content or "no schedule" in content:
                        print("   ❌ 沒有賽程數據")
                    else:
                        print("   ✅ 有賽程數據")
                        
            elif response.status_code == 404:
                print("   ❌ 頁面不存在")
            elif response.status_code >= 500:
                print("   ⚠️ 服務器錯誤")
            else:
                print(f"   ⚠️ 其他狀態: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏱️ 請求超時")
        except requests.exceptions.ConnectionError:
            print("   🚫 連接失敗")
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
        
        print()
        time.sleep(1)  # 避免請求過於頻繁

if __name__ == "__main__":
    check_website_status()
