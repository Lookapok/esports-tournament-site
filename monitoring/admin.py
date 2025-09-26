"""
簡單的監控儀表板
透過 Django Admin 查看系統日誌和監控資料
"""
import json
import os
from datetime import datetime, timedelta
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render
from django.conf import settings

class MonitoringDashboard:
    """監控儀表板類別"""
    
    def get_urls(self):
        """註冊自定義 URL"""
        return [
            path('monitoring/', self.monitoring_view, name='monitoring_dashboard'),
            path('monitoring/api/stats/', self.api_stats, name='monitoring_api_stats'),
        ]
    
    def monitoring_view(self, request):
        """監控儀表板主頁面"""
        context = {
            'title': '系統監控儀表板',
            'has_permission': request.user.is_staff,
        }
        return render(request, 'admin/monitoring_dashboard.html', context)
    
    def api_stats(self, request):
        """提供 API 統計資料"""
        try:
            # 讀取最近的 API 日誌
            api_log_path = settings.LOGS_DIR / 'api.log'
            stats = self._parse_log_file(api_log_path)
            
            return JsonResponse({
                'status': 'success',
                'data': stats
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    def _parse_log_file(self, log_path, max_lines=1000):
        """解析日誌文件並返回統計資料"""
        stats = {
            'total_requests': 0,
            'success_requests': 0,
            'error_requests': 0,
            'avg_response_time': 0,
            'recent_errors': [],
            'request_methods': {},
            'status_codes': {},
        }
        
        if not os.path.exists(log_path):
            return stats
        
        response_times = []
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 只處理最近的日誌行
            recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            
            for line in recent_lines:
                try:
                    log_data = json.loads(line.strip())
                    
                    # 統計請求總數
                    if log_data.get('event_type') == 'api_request_completed':
                        stats['total_requests'] += 1
                        
                        status_code = log_data.get('status_code', 0)
                        method = log_data.get('method', 'unknown')
                        duration = log_data.get('duration_ms', 0)
                        
                        # 統計成功和錯誤請求
                        if 200 <= status_code < 400:
                            stats['success_requests'] += 1
                        else:
                            stats['error_requests'] += 1
                            
                        # 統計回應時間
                        if duration > 0:
                            response_times.append(duration)
                        
                        # 統計請求方法
                        stats['request_methods'][method] = stats['request_methods'].get(method, 0) + 1
                        
                        # 統計狀態碼
                        stats['status_codes'][str(status_code)] = stats['status_codes'].get(str(status_code), 0) + 1
                    
                    # 收集錯誤資訊
                    elif log_data.get('levelname') == 'ERROR':
                        stats['recent_errors'].append({
                            'timestamp': log_data.get('asctime', ''),
                            'message': log_data.get('message', ''),
                            'module': log_data.get('module', ''),
                        })
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # 計算平均回應時間
            if response_times:
                stats['avg_response_time'] = round(sum(response_times) / len(response_times), 2)
            
            # 只保留最近的錯誤（最多 10 個）
            stats['recent_errors'] = stats['recent_errors'][-10:]
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats

# 實例化監控儀表板
monitoring_dashboard = MonitoringDashboard()
