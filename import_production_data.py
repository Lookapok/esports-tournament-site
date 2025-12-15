#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
資料匯入腳本 - 從 JSON 檔案匯入到線上資料庫
"""

import os
import sys
import django
import json
from datetime import datetime
from django.utils.dateparse import parse_date, parse_datetime

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing
from django.db import transaction

def import_tournament_data():
    """匯入錦標賽資料"""
    try:
        print("🔄 開始匯入錦標賽資料...")
        
        # 讀取資料檔案
        with open('production_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with transaction.atomic():
            print("📊 匯入錦標賽...")
            for item in data.get('tournaments', []):
                tournament, created = Tournament.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'name': item['name'],
                        'game': item['game'],
                        'start_date': parse_date(item['start_date']) if item['start_date'] else None,
                        'end_date': parse_date(item['end_date']) if item['end_date'] else None,
                        'rules': item.get('rules', ''),
                        'status': item.get('status', 'upcoming'),
                        'format': item.get('format', 'single_elimination')
                    }
                )
                if created:
                    print(f"  ✅ 建立錦標賽: {tournament.name}")
            
            print("👥 匯入隊伍...")
            for item in data.get('teams', []):
                team, created = Team.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'name': item['name'],
                        'logo': item.get('logo', '')
                    }
                )
                if created:
                    print(f"  ✅ 建立隊伍: {team.name}")
            
            print("🎮 匯入選手...")
            for item in data.get('players', []):
                try:
                    team = Team.objects.get(id=item['team_id']) if item['team_id'] else None
                except Team.DoesNotExist:
                    team = None
                
                player, created = Player.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'nickname': item['nickname'],
                        'team': team,
                        'avatar': item.get('avatar', ''),
                        'role': item.get('role', '')
                    }
                )
                if created:
                    print(f"  ✅ 建立選手: {player.nickname}")
            
            print("📊 匯入小組...")
            for item in data.get('groups', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                except Tournament.DoesNotExist:
                    continue
                
                group, created = Group.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'tournament': tournament,
                        'name': item['name']
                    }
                )
                if created:
                    print(f"  ✅ 建立小組: {group.name}")
            
            print("⚔️  匯入比賽...")
            for item in data.get('matches', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team1 = Team.objects.get(id=item['team1_id']) if item['team1_id'] else None
                    team2 = Team.objects.get(id=item['team2_id']) if item['team2_id'] else None
                    winner = Team.objects.get(id=item['winner_id']) if item['winner_id'] else None
                except (Tournament.DoesNotExist, Team.DoesNotExist):
                    continue
                
                match, created = Match.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'tournament': tournament,
                        'round_number': item.get('round_number', 1),
                        'map': item.get('map', ''),
                        'team1': team1,
                        'team2': team2,
                        'team1_score': item.get('team1_score', 0),
                        'team2_score': item.get('team2_score', 0),
                        'winner': winner,
                        'match_time': parse_datetime(item['match_time']) if item.get('match_time') else None,
                        'status': item.get('status', 'scheduled'),
                        'is_lower_bracket': item.get('is_lower_bracket', False)
                    }
                )
                if created:
                    print(f"  ✅ 建立比賽: {match}")
            
            print("🎯 匯入遊戲...")
            for item in data.get('games', []):
                try:
                    match = Match.objects.get(id=item['match_id'])
                    winner = Team.objects.get(id=item['winner_id']) if item['winner_id'] else None
                except (Match.DoesNotExist, Team.DoesNotExist):
                    continue
                
                game, created = Game.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'match': match,
                        'map_number': item.get('map_number', 1),
                        'map_name': item.get('map_name', ''),
                        'team1_score': item.get('team1_score', 0),
                        'team2_score': item.get('team2_score', 0),
                        'winner': winner
                    }
                )
                if created:
                    print(f"  ✅ 建立遊戲: {game}")
            
            print("📈 匯入積分榜...")
            for item in data.get('standings', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team = Team.objects.get(id=item['team_id'])
                    group = Group.objects.get(id=item['group_id']) if item['group_id'] else None
                except (Tournament.DoesNotExist, Team.DoesNotExist, Group.DoesNotExist):
                    continue
                
                standing, created = Standing.objects.get_or_create(
                    id=item['id'],
                    defaults={
                        'tournament': tournament,
                        'team': team,
                        'group': group,
                        'wins': item.get('wins', 0),
                        'losses': item.get('losses', 0),
                        'draws': item.get('draws', 0),
                        'points': item.get('points', 0)
                    }
                )
                if created:
                    print(f"  ✅ 建立積分: {standing}")
        
        print("🎉 資料匯入完成！")
        print("📝 請檢查管理員頁面確認資料正確性。")
        return True
        
    except Exception as e:
        print(f"❌ 匯入失敗: {str(e)}")
        return False

if __name__ == "__main__":
    import_tournament_data()
