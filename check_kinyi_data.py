from tournaments.models import Team, Player, Tournament, Group, Standing, Match
from django.db import models
import os
os.environ['DJANGO_COLORS'] = 'nocolor'

print('=== 檢查勤益科技大學資料狀況 ===')

# 檢查隊伍資料
print('\n1. 檢查隊伍資料：')
kinyi_teams = Team.objects.filter(name__icontains='勤益')
print(f'   找到 {kinyi_teams.count()} 支隊伍')
for team in kinyi_teams:
    print(f'  - {team.name} (ID: {team.id})')

# 檢查選手資料
print('\n2. 檢查選手資料：')
kinyi_players = Player.objects.filter(team__name__icontains='勤益')
print(f'   找到 {kinyi_players.count()} 位選手')
for player in kinyi_players:
    print(f'  - {player.name} ({player.team.name if player.team else "無隊伍"})')

# 檢查比賽資料
print('\n3. 檢查比賽資料：')
kinyi_matches = Match.objects.filter(models.Q(team1__name__icontains='勤益') | models.Q(team2__name__icontains='勤益'))
print(f'   找到 {kinyi_matches.count()} 場比賽')
for match in kinyi_matches[:10]:  # 顯示前10場
    winner_info = f', 勝者: {match.winner.name}' if match.winner else ', 未決定勝負'
    print(f'  - Match {match.id}: {match.team1.name} vs {match.team2.name} ({match.status}{winner_info})')

# 檢查積分榜
print('\n4. 檢查積分榜：')
kinyi_standings = Standing.objects.filter(team__name__icontains='勤益')
print(f'   找到 {kinyi_standings.count()} 筆積分榜記錄')
for standing in kinyi_standings:
    print(f'  - {standing.team.name}: {standing.wins}勝{standing.losses}敗 ({standing.points}分)')

# 檢查備份檔案中的資料
print('\n5. 檢查備份檔案：')
import json
try:
    with open('local_backup_fixed_20251005_205426.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
        
    kinyi_teams_in_backup = []
    kinyi_players_in_backup = []
    
    for item in backup_data:
        if item['model'] == 'tournaments.team' and '勤益' in item['fields']['name']:
            kinyi_teams_in_backup.append(item)
        elif item['model'] == 'tournaments.player' and item['fields'].get('team'):
            # 需要檢查這個team是否是勤益的
            for team_item in backup_data:
                if (team_item['model'] == 'tournaments.team' and 
                    team_item['pk'] == item['fields']['team'] and 
                    '勤益' in team_item['fields']['name']):
                    kinyi_players_in_backup.append(item)
                    break
    
    print(f'   備份中找到 {len(kinyi_teams_in_backup)} 支勤益隊伍')
    print(f'   備份中找到 {len(kinyi_players_in_backup)} 位勤益選手')
    
    if kinyi_teams_in_backup:
        print('   備份中的隊伍：')
        for team in kinyi_teams_in_backup:
            print(f'   - {team["fields"]["name"]} (原ID: {team["pk"]})')
            
except FileNotFoundError:
    print('   找不到備份檔案 local_backup_fixed_20251005_205426.json')
except Exception as e:
    print(f'   讀取備份檔案時發生錯誤: {e}')

print('\n=== 檢查完成 ===')
