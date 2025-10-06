#!/usr/bin/env python3
"""
快取管理和診斷工具
用於測試快取配置、清除快取、監控快取效果
"""

import os
import django
import sys

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.cache import cache
from django.conf import settings
import time
import json
from datetime import datetime

class CacheManager:
    def __init__(self):
        self.cache_backend = settings.CACHES['default']['BACKEND']
        self.cache_version = getattr(settings, 'CACHE_VERSION', 1)
        
    def diagnose_cache_config(self):
        """診斷快取配置"""
        print("🔍 快取配置診斷")
        print("=" * 50)
        
        print(f"快取後端: {self.cache_backend}")
        print(f"快取版本: {self.cache_version}")
        
        if 'redis' in self.cache_backend.lower():
            print("✅ 使用 Redis 快取")
            try:
                location = settings.CACHES['default'].get('LOCATION', 'N/A')
                print(f"Redis 位置: {location}")
                timeout = settings.CACHES['default'].get('TIMEOUT', 'N/A')
                print(f"預設超時: {timeout} 秒")
            except Exception as e:
                print(f"⚠️  Redis 設定檢查失敗: {e}")
        else:
            print("💻 使用本地記憶體快取")
            try:
                location = settings.CACHES['default'].get('LOCATION', 'N/A')
                print(f"快取位置: {location}")
                max_entries = settings.CACHES['default'].get('OPTIONS', {}).get('MAX_ENTRIES', 'N/A')
                print(f"最大條目: {max_entries}")
            except Exception as e:
                print(f"⚠️  本地快取設定檢查失敗: {e}")
                
    def test_cache_functionality(self):
        """測試快取基本功能"""
        print("\n🧪 快取功能測試")
        print("=" * 50)
        
        test_cases = [
            ('simple_string', 'Hello Cache!', 60),
            ('complex_dict', {'name': 'test', 'data': [1, 2, 3]}, 60),
            ('large_data', 'x' * 10000, 60),  # 10KB 測試數據
        ]
        
        results = []
        
        for key, value, timeout in test_cases:
            test_key = f'cache_test_{key}_v{self.cache_version}'
            
            # 測試寫入
            try:
                write_start = time.time()
                cache.set(test_key, value, timeout)
                write_time = time.time() - write_start
                
                # 測試讀取
                read_start = time.time()
                cached_value = cache.get(test_key)
                read_time = time.time() - read_start
                
                # 驗證數據正確性
                if cached_value == value:
                    status = "✅ 成功"
                    print(f"{key}: {status} (寫入: {write_time:.3f}s, 讀取: {read_time:.3f}s)")
                else:
                    status = "❌ 數據不匹配"
                    print(f"{key}: {status}")
                    
                results.append({
                    'key': key,
                    'status': status,
                    'write_time': write_time,
                    'read_time': read_time,
                    'data_size': len(str(value))
                })
                
                # 清理測試數據
                cache.delete(test_key)
                
            except Exception as e:
                status = f"❌ 錯誤: {e}"
                print(f"{key}: {status}")
                results.append({
                    'key': key,
                    'status': status,
                    'error': str(e)
                })
                
        return results
        
    def test_cache_keys(self):
        """測試應用程式快取鍵"""
        print("\n🔑 應用程式快取鍵測試")
        print("=" * 50)
        
        app_cache_keys = [
            f'tournament_list_v{self.cache_version}',
            f'tournament_detail_v{self.cache_version}_9_page_1',
            f'team_list_v{self.cache_version}_page_1',
        ]
        
        for cache_key in app_cache_keys:
            try:
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    print(f"✅ {cache_key}: 已快取")
                else:
                    print(f"⚪ {cache_key}: 未快取")
            except Exception as e:
                print(f"❌ {cache_key}: 錯誤 - {e}")
                
    def clear_all_cache(self):
        """清除所有快取"""
        print("\n🗑️ 清除快取")
        print("=" * 50)
        
        try:
            cache.clear()
            print("✅ 所有快取已清除")
        except Exception as e:
            print(f"❌ 快取清除失敗: {e}")
            
    def benchmark_cache_performance(self):
        """快取性能基準測試"""
        print("\n⚡ 快取性能基準測試")
        print("=" * 50)
        
        test_data = {
            'small': 'x' * 100,      # 100 bytes
            'medium': 'x' * 10000,   # 10 KB
            'large': 'x' * 100000,   # 100 KB
        }
        
        results = {}
        
        for size_name, data in test_data.items():
            print(f"\n📊 測試 {size_name} 數據 ({len(data)} bytes):")
            
            # 多次測試取平均值
            write_times = []
            read_times = []
            
            for i in range(5):
                test_key = f'benchmark_{size_name}_{i}_v{self.cache_version}'
                
                # 寫入測試
                write_start = time.time()
                cache.set(test_key, data, 300)
                write_time = time.time() - write_start
                write_times.append(write_time)
                
                # 讀取測試
                read_start = time.time()
                cached_data = cache.get(test_key)
                read_time = time.time() - read_start
                read_times.append(read_time)
                
                # 清理
                cache.delete(test_key)
                
            avg_write = sum(write_times) / len(write_times)
            avg_read = sum(read_times) / len(read_times)
            
            print(f"   平均寫入時間: {avg_write:.4f}s")
            print(f"   平均讀取時間: {avg_read:.4f}s")
            print(f"   寫入速度: {len(data) / avg_write / 1024:.1f} KB/s")
            print(f"   讀取速度: {len(data) / avg_read / 1024:.1f} KB/s")
            
            results[size_name] = {
                'data_size': len(data),
                'avg_write_time': avg_write,
                'avg_read_time': avg_read,
                'write_speed_kbps': len(data) / avg_write / 1024,
                'read_speed_kbps': len(data) / avg_read / 1024
            }
            
        return results
        
    def generate_cache_report(self):
        """生成快取診斷報告"""
        print("\n📋 生成快取診斷報告")
        print("=" * 70)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_backend': self.cache_backend,
            'cache_version': self.cache_version,
            'config_info': {
                'backend': self.cache_backend,
                'timeout': settings.CACHES['default'].get('TIMEOUT', 'N/A'),
                'location': settings.CACHES['default'].get('LOCATION', 'N/A'),
            }
        }
        
        # 執行各項測試
        print("執行功能測試...")
        report['functionality_tests'] = self.test_cache_functionality()
        
        print("執行性能測試...")
        report['performance_tests'] = self.benchmark_cache_performance()
        
        # 保存報告
        with open('cache_diagnostic_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ 快取診斷報告已保存到: cache_diagnostic_report.json")
        
        # 快取狀態總結
        self.print_cache_summary(report)
        
    def print_cache_summary(self, report):
        """打印快取狀態總結"""
        print("\n📈 快取狀態總結")
        print("=" * 50)
        
        # 功能測試結果
        func_tests = report.get('functionality_tests', [])
        successful_tests = sum(1 for test in func_tests if '✅' in test.get('status', ''))
        total_tests = len(func_tests)
        
        print(f"功能測試: {successful_tests}/{total_tests} 通過")
        
        # 性能測試結果
        perf_tests = report.get('performance_tests', {})
        if perf_tests:
            avg_read_speed = sum(test['read_speed_kbps'] for test in perf_tests.values()) / len(perf_tests)
            avg_write_speed = sum(test['write_speed_kbps'] for test in perf_tests.values()) / len(perf_tests)
            
            print(f"平均讀取速度: {avg_read_speed:.1f} KB/s")
            print(f"平均寫入速度: {avg_write_speed:.1f} KB/s")
            
        # 建議
        print("\n💡 建議:")
        if 'locmem' in self.cache_backend.lower():
            print("1. 考慮升級到 Redis 快取以獲得更好的性能")
        
        if successful_tests < total_tests:
            print("2. 檢查快取配置，部分功能測試失敗")
            
        print("3. 定期清除快取以確保數據新鮮度")
        print("4. 監控快取命中率以優化快取策略")

if __name__ == "__main__":
    manager = CacheManager()
    
    print("🚀 開始快取診斷...")
    
    manager.diagnose_cache_config()
    manager.test_cache_keys()
    manager.generate_cache_report()
    
    print("\n🎯 快取診斷完成！")
    print("如需清除快取，請執行: python cache_manager.py --clear")
