from django.http import JsonResponse
from django.conf import settings
from django.db import connection
from tournaments.models import Tournament

def health_check(request):
    """健康檢查端點 - 診斷系統狀態"""
    status = {
        'status': 'OK',
        'debug': settings.DEBUG,
        'database': 'Unknown',
        'database_url_set': bool(getattr(settings, 'DATABASE_URL', None)),
        'issues': []
    }
    
    try:
        # 檢查資料庫連接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'Connected'
        
        # 檢查資料表
        tournament_count = Tournament.objects.count()
        status['tournament_count'] = tournament_count
        
    except Exception as e:
        status['status'] = 'ERROR'
        status['database'] = 'Connection Failed'
        status['database_error'] = str(e)
        status['issues'].append(f'資料庫錯誤: {str(e)}')
    
    # 檢查關鍵設定
    db_engine = settings.DATABASES.get('default', {}).get('ENGINE')
    status['database_engine'] = db_engine
    
    if not getattr(settings, 'DATABASE_URL', None):
        status['issues'].append('DATABASE_URL 環境變數未設定')
    
    return JsonResponse(status, status=500 if status['status'] == 'ERROR' else 200)
