"""
日誌監控系統測試腳本
用於驗證日誌記錄功能是否正常工作
"""
import os
import sys
import django
from pathlib import Path

# 添加專案路徑
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')

# 初始化 Django
django.setup()

import logging
from django.test import RequestFactory
from tournaments.models import Tournament, Team, Match

# 取得各種日誌記錄器
api_logger = logging.getLogger('tournaments.api')
business_logger = logging.getLogger('tournaments.business')
monitoring_logger = logging.getLogger('monitoring')

def test_logging_system():
    """測試日誌記錄系統"""
    print("🧪 開始測試日誌監控系統...")
    
    # 測試 API 日誌
    print("1. 測試 API 日誌記錄...")
    api_logger.info('API Test Log', extra={
        'event_type': 'test_api',
        'method': 'POST',
        'path': '/api/test/',
        'status_code': 200,
        'duration_ms': 150.5,
        'test_message': '這是一個測試 API 日誌'
    })
    
    # 測試業務日誌
    print("2. 測試業務邏輯日誌...")
    business_logger.info('Business Logic Test', extra={
        'event_type': 'test_business',
        'operation': 'tournament_creation',
        'tournament_id': 999,
        'tournament_name': '測試錦標賽',
        'participant_count': 8,
        'user': 'test_user',
    })
    
    # 測試監控日誌
    print("3. 測試監控系統日誌...")
    monitoring_logger.info('Monitoring System Test', extra={
        'event_type': 'system_health_check',
        'cpu_usage': '25%',
        'memory_usage': '512MB',
        'active_connections': 15,
        'test_timestamp': '2025-09-26 11:45:00'
    })
    
    # 測試錯誤日誌
    print("4. 測試錯誤日誌記錄...")
    try:
        # 故意產生一個錯誤來測試錯誤日誌
        raise ValueError("這是一個測試錯誤，用於驗證錯誤日誌記錄功能")
    except Exception as e:
        api_logger.error('Test Error Log', extra={
            'event_type': 'test_error',
            'exception_type': type(e).__name__,
            'exception_message': str(e),
            'test_context': '錯誤日誌測試'
        })
    
    print("✅ 日誌測試完成！請檢查以下日誌文件：")
    print("   - logs/api.log (API 和錯誤日誌)")
    print("   - logs/business.log (業務邏輯日誌)")
    print("   - logs/django.log (Django 系統日誌)")
    print("   - logs/error.log (錯誤日誌)")

if __name__ == '__main__':
    test_logging_system()
