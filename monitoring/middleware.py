"""
監控中介軟體
追蹤 API 請求、回應時間和錯誤
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

# 取得監控專用的日誌記錄器
monitor_logger = logging.getLogger('monitoring')

class APIMonitoringMiddleware(MiddlewareMixin):
    """API 監控中介軟體"""
    
    def process_request(self, request):
        """記錄請求開始時間"""
        request._monitoring_start_time = time.time()
        
        # 記錄請求基本資訊
        if request.path.startswith('/api/'):
            monitor_logger.info('API Request Started', extra={
                'event_type': 'api_request_start',
                'method': request.method,
                'path': request.path,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self.get_client_ip(request),
                'timestamp': time.time()
            })
    
    def process_response(self, request, response):
        """記錄回應資訊和處理時間"""
        if hasattr(request, '_monitoring_start_time'):
            duration = time.time() - request._monitoring_start_time
            
            # 只監控 API 請求
            if request.path.startswith('/api/'):
                log_data = {
                    'event_type': 'api_request_completed',
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'ip_address': self.get_client_ip(request),
                    'timestamp': time.time()
                }
                
                # 根據狀態碼決定日誌級別
                if response.status_code >= 500:
                    monitor_logger.error('API Request Failed', extra=log_data)
                elif response.status_code >= 400:
                    monitor_logger.warning('API Request Error', extra=log_data)
                else:
                    monitor_logger.info('API Request Success', extra=log_data)
        
        return response
    
    def process_exception(self, request, exception):
        """記錄例外錯誤"""
        if hasattr(request, '_monitoring_start_time'):
            duration = time.time() - request._monitoring_start_time
            
            monitor_logger.error('API Request Exception', extra={
                'event_type': 'api_exception',
                'method': request.method,
                'path': request.path,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'duration_ms': round(duration * 1000, 2),
                'ip_address': self.get_client_ip(request),
                'timestamp': time.time()
            })
        
        return None
    
    def get_client_ip(self, request):
        """取得客戶端 IP 位址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BusinessLogicMiddleware(MiddlewareMixin):
    """業務邏輯監控中介軟體"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """監控特定的業務邏輯視圖"""
        # 識別重要的業務操作
        business_views = [
            'generate_matches_action',
            'GameReportAPIView',
            'tournament_detail',
        ]
        
        if view_func.__name__ in business_views:
            business_logger = logging.getLogger('tournaments.business')
            business_logger.info('Business Operation Started', extra={
                'event_type': 'business_operation',
                'view_name': view_func.__name__,
                'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
                'path': request.path,
                'timestamp': time.time()
            })
        
        return None
