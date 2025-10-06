#!/usr/bin/env python3
"""
電競賽事網站性能測試腳本
測試第一階段和第二階段優化效果
"""

import requests
import time
import json
from datetime import datetime

class PerformanceTest:
    def __init__(self, base_url="https://winnerstakesall.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
        
    def wait_for_deployment(self, max_attempts=10):
        """等待部署完成"""
        print("⏳ 等待 Render 部署完成...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.get(self.base_url, timeout=30)
                if response.status_code == 200:
                    print(f"✅ 部署完成！(嘗試 {attempt}/{max_attempts})")
                    return True
                else:
                    print(f"🔄 嘗試 {attempt}/{max_attempts} - 狀態碼: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"🔄 嘗試 {attempt}/{max_attempts} - {str(e)[:50]}...")
            
            if attempt < max_attempts:
                print("   等待 30 秒後重試...")
                time.sleep(30)
        
        print("❌ 部署可能還未完成，但我們將繼續測試")
        return False
        
    def test_page_load_time(self, path, description):
        """測試頁面載入時間"""
        url = f"{self.base_url}{path}"
        
        # 冷快取測試（清除 cookies）
        self.session.cookies.clear()
        start_time = time.time()
        
        try:
            response = self.session.get(url, timeout=30)  # 增加超時時間
            cold_load_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ {description}")
                print(f"   冷快取載入時間: {cold_load_time:.2f}秒")
                
                # 檢查是否有快取相關標頭
                cache_info = ""
                if 'X-Cache' in response.headers:
                    cache_info = f" (快取: {response.headers['X-Cache']})"
                
                # 熱快取測試（保持 cookies）
                start_time = time.time()
                response = self.session.get(url, timeout=30)
                hot_load_time = time.time() - start_time
                print(f"   熱快取載入時間: {hot_load_time:.2f}秒{cache_info}")
                
                if cold_load_time > 0:
                    improvement = ((cold_load_time - hot_load_time) / cold_load_time) * 100
                    print(f"   快取改善: {improvement:.1f}%")
                else:
                    improvement = 0
                
                # 檢查頁面內容大小
                content_size = len(response.content) / 1024  # KB
                print(f"   頁面大小: {content_size:.1f} KB")
                
                self.results[path] = {
                    'description': description,
                    'cold_load': cold_load_time,
                    'hot_load': hot_load_time,
                    'improvement': improvement,
                    'content_size_kb': content_size,
                    'status': 'success'
                }
            else:
                print(f"❌ {description} - HTTP {response.status_code}")
                self.results[path] = {'status': 'failed', 'code': response.status_code}
                
        except requests.exceptions.Timeout:
            print(f"⏰ {description} - 連接超時（可能仍在部署）")
            self.results[path] = {'status': 'timeout'}
        except Exception as e:
            print(f"❌ {description} - 錯誤: {e}")
            self.results[path] = {'status': 'error', 'error': str(e)}
            
        print("-" * 50)
        
    def run_full_test(self):
        """執行完整的性能測試"""
        print("🚀 開始性能測試...")
        print("=" * 50)
        
        # 等待部署完成
        self.wait_for_deployment()
        
        print("\n📋 基本功能測試")
        self.test_page_load_time("/", "賽事列表首頁")
        
        # 第一階段優化測試
        print("\n🏆 第一階段優化測試 - 分組分頁")
        self.test_page_load_time("/tournaments/9/", "賽事詳情（WTACS S1 - A組）")
        self.test_page_load_time("/tournaments/9/?page=2", "賽事詳情 - B組")
        self.test_page_load_time("/tournaments/9/?page=3", "賽事詳情 - C組")
        self.test_page_load_time("/teams/", "隊伍列表")
        self.test_page_load_time("/teams/?page=2", "隊伍列表 - 第2頁")
        
        # 第二階段優化測試 - 快取效果
        print("\n⚡ 第二階段優化測試 - 快取系統")
        print("重複訪問測試快取改善效果...")
        
        # 測試賽事詳情快取
        for i in range(3):
            print(f"\n快取測試 #{i+1}:")
            self.test_page_load_time("/tournaments/9/", f"賽事詳情快取測試 #{i+1}")
            time.sleep(2)  # 短暫等待
            
        print("\n📊 測試完成!")
        self.print_summary()
        
    def print_summary(self):
        """打印測試摘要"""
        print("\n" + "=" * 50)
        print("📈 性能測試摘要")
        print("=" * 50)
        
        successful_tests = [r for r in self.results.values() if r.get('status') == 'success']
        
        if successful_tests:
            avg_cold = sum(r['cold_load'] for r in successful_tests) / len(successful_tests)
            avg_hot = sum(r['hot_load'] for r in successful_tests) / len(successful_tests)
            avg_improvement = sum(r['improvement'] for r in successful_tests) / len(successful_tests)
            
            print(f"平均冷快取載入時間: {avg_cold:.2f}秒")
            print(f"平均熱快取載入時間: {avg_hot:.2f}秒")
            print(f"平均快取改善: {avg_improvement:.1f}%")
            
            # 性能評級
            if avg_hot < 1.0:
                grade = "優秀 🏆"
            elif avg_hot < 2.0:
                grade = "良好 ✅"
            elif avg_hot < 3.0:
                grade = "普通 ⚠️"
            else:
                grade = "需改善 ❌"
                
            print(f"整體性能評級: {grade}")
        
        # 保存結果到文件
        with open('performance_test_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
            
        print(f"詳細結果已保存到: performance_test_results.json")

if __name__ == "__main__":
    tester = PerformanceTest()
    tester.run_full_test()
