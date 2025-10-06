#!/usr/bin/env python3
"""
Django 查詢和快取深入分析工具
"""

import os
import django
import sys

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.conf import settings

from django.db import connection
from django.core.cache import cache
from tournaments.models import Tournament, Match, Team
from tournaments.views import tournament_detail
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import time

class DjangoqueryAnalyzer:
    def __init__(self):
        self.factory = RequestFactory()
        
    def analyze_database_queries(self):
        """分析資料庫查詢性能"""
        print("💾 Django 資料庫查詢分析")
        print("=" * 50)
        
        # 重置查詢計數
        connection.queries_log.clear()
        
        # 測試大型賽事查詢 (WTACS S1)
        print("\n🏆 分析 WTACS S1 賽事查詢:")
        
        start_time = time.time()
        try:
            tournament = Tournament.objects.get(id=9)
            print(f"   賽事基本資料: {tournament.name}")
            
            # 分析比賽查詢
            matches_query_time = time.time()
            matches = Match.objects.filter(tournament=tournament).select_related(
                'team1', 'team2', 'winner'
            ).prefetch_related('team1', 'team2')
            
            match_count = matches.count()
            matches_time = time.time() - matches_query_time
            
            print(f"   比賽總數: {match_count}")
            print(f"   比賽查詢時間: {matches_time:.3f}秒")
            
            # 分析隊伍查詢
            teams_query_time = time.time()
            teams = Team.objects.filter(tournaments=tournament).distinct()
            team_count = teams.count()
            teams_time = time.time() - teams_query_time
            
            print(f"   隊伍總數: {team_count}")
            print(f"   隊伍查詢時間: {teams_time:.3f}秒")
            
            total_time = time.time() - start_time
            print(f"   總查詢時間: {total_time:.3f}秒")
            
            # 分析執行的 SQL 查詢
            query_count = len(connection.queries)
            print(f"   SQL 查詢數量: {query_count}")
            
            if query_count > 0:
                total_sql_time = sum(float(q['time']) for q in connection.queries)
                print(f"   SQL 執行總時間: {total_sql_time:.3f}秒")
                
                # 顯示最慢的查詢
                slowest_queries = sorted(connection.queries, 
                                       key=lambda x: float(x['time']), reverse=True)[:3]
                
                print("\n   🐌 最慢的 3 個查詢:")
                for i, query in enumerate(slowest_queries, 1):
                    print(f"      {i}. 時間: {query['time']}秒")
                    print(f"         SQL: {query['sql'][:100]}...")
                    
        except Exception as e:
            print(f"   ❌ 查詢分析失敗: {e}")
            
    def analyze_cache_status(self):
        """分析快取狀態"""
        print("\n⚡ Django 快取分析")
        print("=" * 50)
        
        # 檢查快取後端設定
        print(f"快取後端: {settings.CACHES['default']['BACKEND']}")
        
        if 'redis' in settings.CACHES['default']['BACKEND'].lower():
            print("✅ 使用 Redis 快取")
            try:
                location = settings.CACHES['default'].get('LOCATION', 'N/A')
                print(f"Redis 位置: {location}")
            except:
                print("⚠️  Redis 設定資訊無法取得")
        else:
            print("⚠️  使用本地記憶體快取")
            
        # 測試快取功能
        print("\n🧪 快取功能測試:")
        
        test_key = "performance_test_key"
        test_value = "performance_test_value"
        
        # 設定快取
        cache.set(test_key, test_value, 60)
        
        # 讀取快取
        cached_value = cache.get(test_key)
        
        if cached_value == test_value:
            print("✅ 快取讀寫功能正常")
        else:
            print("❌ 快取功能異常")
            
        # 清理測試快取
        cache.delete(test_key)
        
        # 檢查現有快取鍵 (如果支援)
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'keys'):
                keys = list(cache._cache.keys())
                print(f"當前快取鍵數量: {len(keys)}")
                if keys:
                    print("快取鍵樣本:")
                    for key in keys[:5]:
                        print(f"   - {key}")
            else:
                print("📝 無法檢查快取鍵 (Redis 或其他後端)")
        except Exception as e:
            print(f"⚠️  快取檢查失敗: {e}")
            
    def analyze_view_performance(self):
        """分析視圖性能"""
        print("\n🎯 Django 視圖性能分析")
        print("=" * 50)
        
        # 創建模擬請求
        request = self.factory.get('/tournaments/9/')
        request.user = AnonymousUser()
        
        # 清除快取以測試冷載入
        cache.clear()
        
        print("🧪 測試賽事詳情視圖:")
        
        # 測試冷載入
        connection.queries_log.clear()
        cold_start = time.time()
        
        try:
            # 這裡我們無法直接呼叫視圖函數，因為它需要完整的 Django 環境
            # 但我們可以分析相關的資料庫操作
            
            tournament = Tournament.objects.select_related().get(id=9)
            matches = Match.objects.filter(tournament=tournament).select_related(
                'team1', 'team2', 'winner'
            )[:36]  # 第一頁的比賽
            
            cold_time = time.time() - cold_start
            cold_queries = len(connection.queries)
            
            print(f"   ❄️  冷載入時間: {cold_time:.3f}秒")
            print(f"   ❄️  冷載入查詢: {cold_queries} 個")
            
        except Exception as e:
            print(f"   ❌ 視圖測試失敗: {e}")
            
    def analyze_pagination_performance(self):
        """分析分頁性能"""
        print("\n📄 分頁性能分析")
        print("=" * 50)
        
        try:
            tournament = Tournament.objects.get(id=9)
            total_matches = Match.objects.filter(tournament=tournament).count()
            
            print(f"賽事: {tournament.name}")
            print(f"總比賽數: {total_matches}")
            
            per_page = 36
            total_pages = (total_matches + per_page - 1) // per_page
            print(f"每頁比賽數: {per_page}")
            print(f"總頁數: {total_pages}")
            
            # 測試不同頁面的載入時間
            page_times = {}
            
            for page in [1, 2, 3, total_pages]:
                if page <= total_pages:
                    start_time = time.time()
                    
                    offset = (page - 1) * per_page
                    page_matches = Match.objects.filter(
                        tournament=tournament
                    ).select_related(
                        'team1', 'team2', 'winner'
                    )[offset:offset + per_page]
                    
                    # 強制執行查詢
                    list(page_matches)
                    
                    page_time = time.time() - start_time
                    page_times[f"第{page}頁"] = page_time
                    
                    print(f"   第{page}頁載入時間: {page_time:.3f}秒")
                    
            if len(page_times) > 1:
                times = list(page_times.values())
                max_time = max(times)
                min_time = min(times)
                print(f"\n   📊 分頁載入差異: {max_time - min_time:.3f}秒")
                
                if max_time - min_time < 0.1:
                    print("   ✅ 分頁載入時間一致")
                else:
                    print("   ⚠️  分頁載入時間不一致")
                    
        except Exception as e:
            print(f"   ❌ 分頁分析失敗: {e}")
            
    def generate_optimization_recommendations(self):
        """生成優化建議"""
        print("\n💡 優化建議")
        print("=" * 50)
        
        recommendations = []
        
        # 檢查快取配置
        if 'locmem' in settings.CACHES['default']['BACKEND'].lower():
            recommendations.append({
                'priority': 'HIGH',
                'category': '快取',
                'issue': '使用本地記憶體快取',
                'solution': '設定 Redis 快取以提高效能'
            })
            
        # 檢查資料庫連接設定
        db_config = settings.DATABASES['default']
        if 'sqlite' in db_config.get('ENGINE', '').lower():
            recommendations.append({
                'priority': 'HIGH',
                'category': '資料庫',
                'issue': '使用 SQLite 資料庫',
                'solution': '升級到 PostgreSQL 以提高效能'
            })
            
        # 一般性能建議
        recommendations.extend([
            {
                'priority': 'MEDIUM',
                'category': '查詢優化',
                'issue': '大型賽事載入緩慢',
                'solution': '實施更精細的快取策略和查詢優化'
            },
            {
                'priority': 'MEDIUM',
                'category': '前端優化',
                'issue': '頁面資源載入',
                'solution': '實施 CDN 和資源壓縮'
            },
            {
                'priority': 'LOW',
                'category': '監控',
                'issue': '性能監控不足',
                'solution': '設定性能監控和警報系統'
            }
        ])
        
        # 按優先級排序並顯示
        priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            print(f"{i}. {priority_emoji[rec['priority']]} {rec['category']}: {rec['issue']}")
            print(f"   💡 解決方案: {rec['solution']}")
            print()
            
    def run_full_analysis(self):
        """執行完整分析"""
        print("🔬 Django 深入性能分析")
        print("=" * 70)
        
        self.analyze_database_queries()
        self.analyze_cache_status()
        self.analyze_view_performance()
        self.analyze_pagination_performance()
        self.generate_optimization_recommendations()
        
        print("\n✅ Django 分析完成!")

if __name__ == "__main__":
    analyzer = DjangoqueryAnalyzer()
    analyzer.run_full_analysis()
