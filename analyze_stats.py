#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# 設定 Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import PlayerGameStat, Player, Team
from django.db.models import Count, Avg

print("🔍 統計資料詳細分析")
print("=" * 50)

# 檢查統計資料樣本
print('🏆 最高 ACS 玩家 (前5名):')
stats = PlayerGameStat.objects.select_related('player', 'team').order_by('-acs')[:5]
for i, stat in enumerate(stats, 1):
    player_name = stat.player.nickname if stat.player else 'Unknown'
    team_name = stat.team.name if stat.team else 'Unknown Team'
    print(f'  {i}. {player_name} ({team_name})')
    print(f'     殺敵: {stat.kills} | 死亡: {stat.deaths} | 助攻: {stat.assists} | ACS: {stat.acs}')

print('\n📊 各隊伍統計資料分布 (前5名):')
team_stats = PlayerGameStat.objects.values('team_id').annotate(
    count=Count('id'),
    avg_acs=Avg('acs'),
    avg_kills=Avg('kills'),
    avg_deaths=Avg('deaths')
).order_by('-count')[:5]

for i, team_stat in enumerate(team_stats, 1):
    team_id = team_stat['team_id']
    try:
        team = Team.objects.get(id=team_id)
        team_name = team.name
    except Team.DoesNotExist:
        team_name = f'隊伍 ID {team_id}'
    
    print(f'  {i}. {team_name}:')
    print(f'     比賽場次: {team_stat["count"]}')
    print(f'     平均 ACS: {team_stat["avg_acs"]:.1f}')
    print(f'     平均殺敵: {team_stat["avg_kills"]:.1f}')
    print(f'     平均死亡: {team_stat["avg_deaths"]:.1f}')

print('\n🎯 整體統計摘要:')
total_stats = PlayerGameStat.objects.count()
total_players = PlayerGameStat.objects.values('player_id').distinct().count()
total_teams = PlayerGameStat.objects.values('team_id').distinct().count()

print(f'  • 總統計記錄: {total_stats} 筆')
print(f'  • 參與球員: {total_players} 位')
print(f'  • 參與隊伍: {total_teams} 支')

# 檢查數據完整性
incomplete_stats = PlayerGameStat.objects.filter(
    acs__isnull=True
).count()

if incomplete_stats > 0:
    print(f'\n⚠️  發現 {incomplete_stats} 筆不完整的統計資料')
else:
    print('\n✅ 所有統計資料完整無缺！')
