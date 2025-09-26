"""
監控系統的 URL 配置
"""
from django.urls import path
from .admin import monitoring_dashboard

urlpatterns = [
    path('admin/monitoring/', monitoring_dashboard.monitoring_view, name='monitoring_dashboard'),
    path('admin/monitoring/api/stats/', monitoring_dashboard.api_stats, name='monitoring_api_stats'),
]
