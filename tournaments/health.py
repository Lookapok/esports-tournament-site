from django.http import JsonResponse
from django.conf import settings
from django.db import connection
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat

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
        
        # 檢查所有資料表
        status['tournament_count'] = Tournament.objects.count()
        status['team_count'] = Team.objects.count()
        status['player_count'] = Player.objects.count()
        status['match_count'] = Match.objects.count()
        status['game_count'] = Game.objects.count()
        status['group_count'] = Group.objects.count()
        status['standing_count'] = Standing.objects.count()
        status['playergamestat_count'] = PlayerGameStat.objects.count()
        
        # 檢查資料完整性
        total_data = (status['tournament_count'] + status['team_count'] + 
                     status['player_count'] + status['match_count'] + 
                     status['group_count'] + status['standing_count'])
        
        if total_data == 0:
            status['issues'].append('所有資料表都是空的')
        elif status['tournament_count'] > 0 and status['team_count'] == 0:
            status['issues'].append('有錦標賽但沒有隊伍資料')
        elif status['tournament_count'] > 0 and status['group_count'] == 0:
            status['issues'].append('有錦標賽但沒有分組資料')
        elif status['tournament_count'] > 0 and status['standing_count'] == 0:
            status['issues'].append('有錦標賽但沒有積分榜資料')
        elif status['game_count'] > 0 and status['playergamestat_count'] == 0:
            status['issues'].append('有比賽局數但沒有選手統計數據')
        
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
