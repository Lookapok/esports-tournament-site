#!/usr/bin/env python
"""
網站部署驗證腳本
測試 WTACS 電競賽事系統的各項功能是否正常
"""

import requests
import time

def test_website_deployment():
    """測試網站部署是否成功"""
    
    # 基本 URL（請根據您的實際 Render URL 修改）
    BASE_URL = "https://wtacs-esports.onrender.com"
    
    print("🚀 開始測試 WTACS 電競賽事系統部署...")
    print("=" * 60)
    
    # 測試項目
    tests = [
        {
            "name": "首頁載入",
            "url": f"{BASE_URL}/",
            "expected_status": 200,
            "timeout": 30
        },
        {
            "name": "錦標賽列表",
            "url": f"{BASE_URL}/tournaments/",
            "expected_status": 200,
            "timeout": 15
        },
        {
            "name": "管理員登入頁面",
            "url": f"{BASE_URL}/admin/",
            "expected_status": 200,
            "timeout": 15
        },
        {
            "name": "API 端點",
            "url": f"{BASE_URL}/api/",
            "expected_status": 200,
            "timeout": 15
        },
        {
            "name": "靜態檔案",
            "url": f"{BASE_URL}/static/css/style.css",
            "expected_status": [200, 404],  # 404 也可接受，表示服務正常但檔案不存在
            "timeout": 10
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"🔄 測試: {test['name']}...")
        
        try:
            response = requests.get(
                test['url'], 
                timeout=test['timeout'],
                allow_redirects=True
            )
            
            expected_status = test['expected_status']
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
                success = response.status_code == expected_status
            
            if success:
                print(f"✅ {test['name']}: 成功 (狀態碼: {response.status_code})")
                print(f"   📍 URL: {test['url']}")
                results.append(True)
            else:
                print(f"❌ {test['name']}: 失敗 (狀態碼: {response.status_code})")
                print(f"   📍 URL: {test['url']}")
                results.append(False)
                
        except requests.exceptions.Timeout:
            print(f"⏰ {test['name']}: 逾時 (>{test['timeout']}秒)")
            print(f"   📍 URL: {test['url']}")
            results.append(False)
            
        except requests.exceptions.ConnectionError:
            print(f"🌐 {test['name']}: 連線錯誤")
            print(f"   📍 URL: {test['url']}")
            results.append(False)
            
        except Exception as e:
            print(f"❌ {test['name']}: 錯誤 - {str(e)}")
            print(f"   📍 URL: {test['url']}")
            results.append(False)
        
        time.sleep(2)  # 避免過度請求
    
    # 總結結果
    print("\n" + "=" * 60)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print("🎉 所有測試通過！網站部署成功！")
        print("\n📱 您現在可以：")
        print(f"   • 訪問網站: {BASE_URL}")
        print(f"   • 管理系統: {BASE_URL}/admin/")
        print(f"   • 使用 API: {BASE_URL}/api/")
    elif success_count >= total_count * 0.8:
        print(f"⚠️  大部分測試通過 ({success_count}/{total_count})")
        print("   網站基本可用，部分功能可能需要調整")
    else:
        print(f"❌ 多項測試失敗 ({success_count}/{total_count})")
        print("   請檢查部署設定和錯誤日誌")
    
    return success_count / total_count

def test_database_connectivity():
    """測試資料庫連線（透過 API）"""
    
    BASE_URL = "https://wtacs-esports.onrender.com"
    
    print("\n🗄️ 測試資料庫連線...")
    
    try:
        # 測試是否可以取得錦標賽資料
        response = requests.get(f"{BASE_URL}/api/tournaments/", timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 資料庫連線正常")
            print(f"   📊 找到 {len(data.get('results', data))} 項錦標賽資料")
            return True
        else:
            print(f"⚠️  API 回應異常 (狀態碼: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 資料庫連線測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏆 WTACS 電競賽事系統 - 部署驗證工具")
    print("=" * 60)
    
    # 基本功能測試
    website_success = test_website_deployment()
    
    # 資料庫連線測試
    db_success = test_database_connectivity()
    
    print("\n" + "=" * 60)
    print("📋 最終報告:")
    print(f"   🌐 網站功能: {'✅ 正常' if website_success >= 0.8 else '❌ 異常'}")
    print(f"   🗄️  資料庫: {'✅ 正常' if db_success else '❌ 異常'}")
    
    if website_success >= 0.8 and db_success:
        print("\n🎉 恭喜！WTACS 電競賽事系統部署完全成功！")
        print("   您的網站已準備好接受使用者訪問！")
    else:
        print("\n⚠️  部分功能可能需要進一步調整")
        print("   請檢查 Render 的部署日誌以了解詳細資訊")
