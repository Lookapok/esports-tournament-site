import json

try:
    with open('local_backup_fixed_20251005_205426.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    # 找出勤益相關的隊伍
    kinyi_teams = []
    for item in backup_data:
        if item['model'] == 'tournaments.team' and '勤益' in item['fields']['name']:
            kinyi_teams.append(item)
    
    # 找出勤益隊伍的ID
    kinyi_team_ids = [team['pk'] for team in kinyi_teams]
    
    # 找出勤益選手
    kinyi_players = []
    for item in backup_data:
        if item['model'] == 'tournaments.player' and item['fields'].get('team') in kinyi_team_ids:
            kinyi_players.append(item)
    
    print('=== BACKUP DATA ANALYSIS ===')
    print(f'Kinyi teams in backup: {len(kinyi_teams)}')
    for team in kinyi_teams:
        team_name = team['fields']['name']
        team_id = team['pk']
        print(f'  - Team: {team_name} (Original ID: {team_id})')
    
    print(f'\nKinyi players in backup: {len(kinyi_players)}')
    for player in kinyi_players:
        player_name = player['fields'].get('name', 'Unknown')
        player_id = player['pk']
        player_discord = player['fields'].get('discord_name', 'No Discord')
        print(f'  - Player: {player_name} | Discord: {player_discord} (Original ID: {player_id})')
        
    print('\n=== SUMMARY ===')
    print(f'Current database: 1 team, 0 players')
    print(f'Backup contains: {len(kinyi_teams)} teams, {len(kinyi_players)} players')
    
    if len(kinyi_players) > 0:
        print('\n❌ You lost player data! Need to restore from backup.')
    else:
        print('\n✅ No player data in backup either.')

except FileNotFoundError:
    print('❌ Backup file local_backup_fixed_20251005_205426.json not found')
except Exception as e:
    print(f'❌ Error reading backup: {e}')
