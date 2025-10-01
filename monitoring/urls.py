"""
監控系統的 URL 配置
"""
from django.urls import path
from .admin import monitoring_dashboard

urlpatterns = [
    # 監控儀表板主頁
    path('', monitoring_dashboard.monitoring_view, name='monitoring_dashboard'),
    # 監控 API 統計資料
    path('api/stats/', monitoring_dashboard.api_stats, name='monitoring_api_stats'),
]
