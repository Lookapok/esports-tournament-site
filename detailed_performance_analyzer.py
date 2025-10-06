#!/usr/bin/env python3
"""
深入性能分析工具
分析資料庫查詢、快取效果、頁面組件載入時間等
"""

import requests
import time
import json
import re
from datetime import datetime
from urllib.parse import urljoin

class DetailedPerformanceAnalyzer:
    def __init__(self, base_url="https://winnerstakesall.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.analysis_results = {}
        
    def analyze_page_components(self, path, description):
        """分析頁面各組件的載入時間"""
        url = f"{self.base_url}{path}"
        
        print(f"\n🔍 分析頁面: {description}")
        print("=" * 60)
        
        # 1. 整體頁面載入分析
        start_time = time.time()
        try:
            response = self.session.get(url, timeout=30)
            total_load_time = time.time() - start_time
            
            if response.status_code != 200:
                print(f"❌ 頁面載入失敗: HTTP {response.status_code}")
                return
                
            print(f"✅ 整體載入時間: {total_load_time:.2f}秒")
            print(f"📄 頁面大小: {len(response.content)/1024:.1f} KB")
            print(f"📊 狀態碼: {response.status_code}")
            
            # 2. 分析響應標頭
            self.analyze_response_headers(response)
            
            # 3. 分析頁面內容
            self.analyze_page_content(response.text, path)
            
            # 4. 分析快取效果
            self.analyze_cache_performance(url, description)
            
            self.analysis_results[path] = {
                'description': description,
                'total_load_time': total_load_time,
                'page_size_kb': len(response.content)/1024,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 分析失敗: {e}")
            
    def analyze_response_headers(self, response):
        """分析響應標頭"""
        print("\n📋 響應標頭分析:")
        
        important_headers = [
            'Content-Type', 'Content-Length', 'Content-Encoding',
            'Cache-Control', 'ETag', 'Last-Modified',
            'X-Cache', 'Server', 'CF-Cache-Status'
        ]
        
        for header in important_headers:
            if header in response.headers:
                print(f"   {header}: {response.headers[header]}")
                
        # 檢查快取相關標頭
        cache_headers = ['Cache-Control', 'ETag', 'Last-Modified']
        cache_count = sum(1 for h in cache_headers if h in response.headers)
        
        if cache_count > 0:
            print(f"✅ 快取標頭: {cache_count}/{len(cache_headers)} 個設定")
        else:
            print("⚠️  無快取標頭設定")
            
    def analyze_page_content(self, html_content, path):
        """分析頁面內容結構"""
        print("\n🎯 頁面內容分析:")
        
        # 分析 HTML 元素數量
        img_count = len(re.findall(r'<img[^>]*>', html_content))
        css_count = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\']', html_content))
        js_count = len(re.findall(r'<script[^>]*src=', html_content))
        
        print(f"   🖼️  圖片數量: {img_count}")
        print(f"   🎨 CSS 檔案: {css_count}")
        print(f"   ⚡ JS 檔案: {js_count}")
        
        # 檢查特定內容
        if 'tournament' in path:
            # 分析賽事相關內容
            match_count = len(re.findall(r'class=["\'][^"\']*match[^"\']*["\']', html_content))
            team_count = len(re.findall(r'class=["\'][^"\']*team[^"\']*["\']', html_content))
            
            print(f"   🏆 比賽元素: {match_count}")
            print(f"   👥 隊伍元素: {team_count}")
            
        if 'teams' in path:
            # 分析隊伍相關內容
            team_card_count = len(re.findall(r'class=["\'][^"\']*card[^"\']*["\']', html_content))
            print(f"   📋 隊伍卡片: {team_card_count}")
            
        # 檢查錯誤指示
        if 'error' in html_content.lower() or '404' in html_content:
            print("⚠️  頁面可能含有錯誤內容")
            
    def analyze_cache_performance(self, url, description):
        """分析快取性能"""
        print("\n⚡ 快取性能分析:")
        
        # 清除快取，測試冷載入
        self.session.cookies.clear()
        cold_times = []
        
        for i in range(3):
            start = time.time()
            response = self.session.get(url, timeout=30)
            cold_time = time.time() - start
            cold_times.append(cold_time)
            time.sleep(1)  # 避免請求過快
            
        # 測試熱載入（有快取）
        hot_times = []
        for i in range(3):
            start = time.time()
            response = self.session.get(url, timeout=30)
            hot_time = time.time() - start
            hot_times.append(hot_time)
            time.sleep(0.5)
            
        avg_cold = sum(cold_times) / len(cold_times)
        avg_hot = sum(hot_times) / len(hot_times)
        improvement = ((avg_cold - avg_hot) / avg_cold) * 100 if avg_cold > 0 else 0
        
        print(f"   ❄️  平均冷載入: {avg_cold:.2f}秒 (範圍: {min(cold_times):.2f}-{max(cold_times):.2f})")
        print(f"   🔥 平均熱載入: {avg_hot:.2f}秒 (範圍: {min(hot_times):.2f}-{max(hot_times):.2f})")
        print(f"   📈 快取改善: {improvement:.1f}%")
        
        # 快取效果評級
        if improvement > 50:
            cache_grade = "優秀 🏆"
        elif improvement > 20:
            cache_grade = "良好 ✅"
        elif improvement > 0:
            cache_grade = "普通 ⚠️"
        else:
            cache_grade = "需改善 ❌"
            
        print(f"   🎯 快取評級: {cache_grade}")
        
    def analyze_database_patterns(self):
        """分析可能的資料庫查詢模式"""
        print("\n💾 資料庫查詢模式分析:")
        
        test_cases = [
            ("/", "首頁 - 賽事列表"),
            ("/tournaments/9/", "賽事詳情 - 完整資料"),
            ("/tournaments/9/?page=2", "賽事詳情 - 分頁"),
            ("/teams/", "隊伍列表 - 第一頁"),
            ("/teams/?page=2", "隊伍列表 - 第二頁"),
        ]
        
        for path, desc in test_cases:
            print(f"\n   🔍 測試: {desc}")
            
            # 測試多次載入的一致性
            times = []
            for i in range(5):
                start = time.time()
                try:
                    response = self.session.get(f"{self.base_url}{path}", timeout=15)
                    load_time = time.time() - start
                    times.append(load_time)
                except:
                    times.append(999)  # 標記失敗
                time.sleep(0.5)
                
            valid_times = [t for t in times if t < 30]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                std_dev = (sum((t - avg_time) ** 2 for t in valid_times) / len(valid_times)) ** 0.5
                
                print(f"      ⏱️  平均載入: {avg_time:.2f}秒")
                print(f"      📊 標準差: {std_dev:.2f}秒")
                
                if std_dev < 0.5:
                    consistency = "穩定 ✅"
                elif std_dev < 1.0:
                    consistency = "普通 ⚠️"
                else:
                    consistency = "不穩定 ❌"
                    
                print(f"      🎯 穩定性: {consistency}")
                
    def analyze_specific_bottlenecks(self):
        """分析特定的性能瓶頸"""
        print("\n🚨 瓶頸分析:")
        
        # 測試大型頁面 (WTACS S1 - 144場比賽)
        print("\n   🏆 大型賽事分析 (WTACS S1):")
        
        # 測試不同分組的載入時間
        group_times = {}
        for page in range(1, 5):  # 測試前4組
            try:
                start = time.time()
                response = self.session.get(
                    f"{self.base_url}/tournaments/9/?page={page}", 
                    timeout=30
                )
                load_time = time.time() - start
                group_times[f"第{page}組"] = load_time
                print(f"      第{page}組載入: {load_time:.2f}秒")
            except Exception as e:
                print(f"      第{page}組失敗: {str(e)[:30]}...")
                
        if group_times:
            fastest = min(group_times.values())
            slowest = max(group_times.values())
            print(f"      📊 分組載入差異: {slowest - fastest:.2f}秒")
            
    def run_comprehensive_analysis(self):
        """執行全面性能分析"""
        print("🔬 開始深入性能分析...")
        print("=" * 70)
        
        # 主要頁面分析
        pages_to_analyze = [
            ("/", "首頁/賽事列表"),
            ("/tournaments/9/", "WTACS S1 賽事詳情 (A組)"),
            ("/tournaments/9/?page=2", "WTACS S1 賽事詳情 (B組)"),
            ("/teams/", "隊伍列表"),
        ]
        
        for path, description in pages_to_analyze:
            self.analyze_page_components(path, description)
            
        # 資料庫查詢模式分析
        self.analyze_database_patterns()
        
        # 瓶頸分析
        self.analyze_specific_bottlenecks()
        
        # 生成分析報告
        self.generate_analysis_report()
        
    def generate_analysis_report(self):
        """生成分析報告"""
        print("\n" + "=" * 70)
        print("📈 深入性能分析報告")
        print("=" * 70)
        
        if self.analysis_results:
            total_pages = len(self.analysis_results)
            avg_load_time = sum(r['total_load_time'] for r in self.analysis_results.values()) / total_pages
            avg_page_size = sum(r['page_size_kb'] for r in self.analysis_results.values()) / total_pages
            
            print(f"📊 整體統計:")
            print(f"   分析頁面數: {total_pages}")
            print(f"   平均載入時間: {avg_load_time:.2f}秒")
            print(f"   平均頁面大小: {avg_page_size:.1f} KB")
            
            # 性能分級
            if avg_load_time < 2.0:
                grade = "優秀 🏆"
                recommendations = ["維持當前優化策略", "考慮進一步的前端優化"]
            elif avg_load_time < 5.0:
                grade = "良好 ✅"
                recommendations = ["優化大型頁面載入", "增強快取策略", "考慮 CDN"]
            elif avg_load_time < 10.0:
                grade = "普通 ⚠️"
                recommendations = ["急需資料庫優化", "實施更積極的快取", "減少頁面複雜度"]
            else:
                grade = "需改善 ❌"
                recommendations = ["全面檢查資料庫查詢", "重新設計頁面架構", "考慮分散式快取"]
                
            print(f"\n🎯 整體性能評級: {grade}")
            
            print(f"\n💡 優化建議:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
                
        # 保存詳細報告
        with open('detailed_performance_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_pages_analyzed': len(self.analysis_results),
                    'average_load_time': avg_load_time if self.analysis_results else 0,
                    'average_page_size_kb': avg_page_size if self.analysis_results else 0,
                },
                'detailed_results': self.analysis_results
            }, f, ensure_ascii=False, indent=2)
            
        print(f"\n📋 詳細報告已保存到: detailed_performance_analysis.json")

if __name__ == "__main__":
    analyzer = DetailedPerformanceAnalyzer()
    analyzer.run_comprehensive_analysis()
