#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完全清空 Supabase 資料庫並重新匯入 Docker 的正確資料
"""

import os
import sys
import django
import psycopg2
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import (
    Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat
)
from django.db import transaction

def clear_supabase_data():
    """完全清空 Supabase 中的所有資料"""
    print("🗑️ 清空 Supabase 資料...")
    
    with transaction.atomic():
        # 按照外鍵依賴順序刪除
        deleted_counts = {}
        
        # 1. 統計資料 (最後層)
        count = PlayerGameStat.objects.count()
        PlayerGameStat.objects.all().delete()
        deleted_counts['PlayerGameStat'] = count
        
        # 2. 排名資料
        count = Standing.objects.count()
        Standing.objects.all().delete()
        deleted_counts['Standing'] = count
        
        # 3. 球員資料
        count = Player.objects.count()
        Player.objects.all().delete()
        deleted_counts['Player'] = count
        
        # 4. 遊戲資料
        count = Game.objects.count()
        Game.objects.all().delete()
        deleted_counts['Game'] = count
        
        # 5. 比賽資料
        count = Match.objects.count()
        Match.objects.all().delete()
        deleted_counts['Match'] = count
        
        # 6. 分組資料
        count = Group.objects.count()
        Group.objects.all().delete()
        deleted_counts['Group'] = count
        
        # 7. 隊伍資料
        count = Team.objects.count()
        Team.objects.all().delete()
        deleted_counts['Team'] = count
        
        # 8. 錦標賽資料
        count = Tournament.objects.count()
        Tournament.objects.all().delete()
        deleted_counts['Tournament'] = count
        
    print("✅ Supabase 資料清空完成：")
    for model, count in deleted_counts.items():
        print(f"  - {model}: 刪除 {count} 筆")
    
    return deleted_counts

def get_docker_data():
    """從 Docker PostgreSQL 獲取完整資料"""
    print("🐳 從 Docker PostgreSQL 獲取資料...")
    
    docker_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'esports_dev',
        'user': 'postgres',
        'password': 'esports123'
    }
    
    try:
        conn = psycopg2.connect(**docker_config)
        cursor = conn.cursor()
        
        data = {}
        
        # 1. 錦標賽
        cursor.execute("SELECT id, name, game, start_date, end_date, rules, status, format FROM tournaments_tournament ORDER BY id")
        data['tournaments'] = []
        for row in cursor.fetchall():
            data['tournaments'].append({
                'id': row[0], 'name': row[1], 'game': row[2],
                'start_date': row[3], 'end_date': row[4],
                'rules': row[5], 'status': row[6], 'format': row[7]
            })
        
        # 2. 隊伍
        cursor.execute("SELECT id, name, logo FROM tournaments_team ORDER BY id")
        data['teams'] = []
        for row in cursor.fetchall():
            data['teams'].append({
                'id': row[0], 'name': row[1], 'logo': row[2] or '', 'school': ''  # 加入空的 school 欄位
            })
        
        # 3. 分組
        cursor.execute("SELECT id, name, tournament_id FROM tournaments_group ORDER BY id")
        data['groups'] = []
        for row in cursor.fetchall():
            data['groups'].append({
                'id': row[0], 'name': row[1], 'tournament_id': row[2]
            })
        
        # 4. 球員
        cursor.execute("SELECT id, nickname, team_id, avatar, role FROM tournaments_player ORDER BY id")
        data['players'] = []
        for row in cursor.fetchall():
            data['players'].append({
                'id': row[0], 'nickname': row[1], 'team_id': row[2],
                'avatar': row[3] or '', 'role': row[4] or 'Flex'
            })
        
        # 5. 比賽
        cursor.execute("SELECT id, tournament_id, round_number, map, team1_id, team2_id, team1_score, team2_score, winner_id, match_time, status, is_lower_bracket FROM tournaments_match ORDER BY id")
        data['matches'] = []
        for row in cursor.fetchall():
            data['matches'].append({
                'id': row[0], 'tournament_id': row[1], 'round_number': row[2], 'map': row[3],
                'team1_id': row[4], 'team2_id': row[5],
                'team1_score': row[6], 'team2_score': row[7], 'winner_id': row[8],
                'match_time': row[9], 'status': row[10], 'is_lower_bracket': row[11]
            })
        
        # 6. 遊戲 - 按照 Docker 欄位順序匯入
        cursor.execute("SELECT id, match_id, map_number, map_name, team1_score, team2_score, winner_id FROM tournaments_game ORDER BY id")
        data['games'] = []
        for row in cursor.fetchall():
            data['games'].append({
                'id': row[0], 'match_id': row[1], 'map_number': row[2],
                'map_name': row[3], 'team1_score': row[4], 'team2_score': row[5],
                'winner_id': row[6]
            })
        
        # 7. 排名
        cursor.execute("SELECT id, tournament_id, team_id, group_id, wins, losses, draws, points FROM tournaments_standing ORDER BY id")
        data['standings'] = []
        for row in cursor.fetchall():
            data['standings'].append({
                'id': row[0], 'tournament_id': row[1], 'team_id': row[2],
                'group_id': row[3], 'wins': row[4], 'losses': row[5],
                'draws': row[6], 'points': row[7]
            })
        
        # 8. 統計資料 (關鍵！)
        cursor.execute("SELECT id, game_id, player_id, team_id, kills, deaths, assists, first_kills, acs FROM tournaments_playergamestat ORDER BY id")
        data['player_stats'] = []
        for row in cursor.fetchall():
            data['player_stats'].append({
                'id': row[0], 'game_id': row[1], 'player_id': row[2],
                'team_id': row[3], 'kills': row[4], 'deaths': row[5],
                'assists': row[6], 'first_kills': row[7], 'acs': row[8]
            })
        
        cursor.close()
        conn.close()
        
        print("✅ Docker 資料獲取完成：")
        print(f"  - 錦標賽: {len(data['tournaments'])} 筆")
        print(f"  - 隊伍: {len(data['teams'])} 筆")
        print(f"  - 分組: {len(data['groups'])} 筆")
        print(f"  - 球員: {len(data['players'])} 筆")
        print(f"  - 比賽: {len(data['matches'])} 筆")
        print(f"  - 遊戲: {len(data['games'])} 筆")
        print(f"  - 排名: {len(data['standings'])} 筆")
        print(f"  - 統計: {len(data['player_stats'])} 筆 ⭐")
        
        return data
        
    except Exception as e:
        print(f"❌ 獲取 Docker 資料失敗: {e}")
        return None

def import_to_supabase(data):
    """將資料匯入到 Supabase"""
    print("📤 匯入資料到 Supabase...")
    
    imported_counts = {}
    
    with transaction.atomic():
        
        # 1. 匯入錦標賽
        print("🏆 匯入錦標賽...")
        tournaments_created = []
        for t_data in data['tournaments']:
            tournament = Tournament.objects.create(
                id=t_data['id'],
                name=t_data['name'],
                game=t_data['game'],
                start_date=t_data['start_date'],
                end_date=t_data['end_date'],
                rules=t_data['rules'],
                status=t_data['status'],
                format=t_data['format']
            )
            tournaments_created.append(tournament)
        imported_counts['Tournament'] = len(tournaments_created)
        
        # 2. 匯入隊伍
        print("🏟️ 匯入隊伍...")
        teams_created = []
        for team_data in data['teams']:
            team = Team.objects.create(
                id=team_data['id'],
                name=team_data['name'],
                school=team_data['school'],  # 設定空的 school
                logo=team_data['logo']
            )
            teams_created.append(team)
        imported_counts['Team'] = len(teams_created)
        
        # 3. 匯入分組
        print("📂 匯入分組...")
        groups_created = []
        for group_data in data['groups']:
            group = Group.objects.create(
                id=group_data['id'],
                name=group_data['name'],
                tournament_id=group_data['tournament_id']
            )
            groups_created.append(group)
        imported_counts['Group'] = len(groups_created)
        
        # 4. 匯入球員
        print("👥 匯入球員...")
        players_created = []
        for player_data in data['players']:
            player = Player.objects.create(
                id=player_data['id'],
                nickname=player_data['nickname'],
                team_id=player_data['team_id'],
                avatar=player_data['avatar'],
                role=player_data['role']
            )
            players_created.append(player)
        imported_counts['Player'] = len(players_created)
        
        # 5. 匯入排名 (在比賽之前，避免信號處理器錯誤)
        print("🏅 匯入排名...")
        standings_created = []
        for standing_data in data['standings']:
            standing = Standing.objects.create(
                id=standing_data['id'],
                tournament_id=standing_data['tournament_id'],
                team_id=standing_data['team_id'],
                group_id=standing_data['group_id'],
                wins=standing_data['wins'],
                losses=standing_data['losses'],
                draws=standing_data['draws'],
                points=standing_data['points']
            )
            standings_created.append(standing)
        imported_counts['Standing'] = len(standings_created)
        
        # 6. 匯入比賽
        print("⚔️ 匯入比賽...")
        matches_created = []
        for match_data in data['matches']:
            match = Match.objects.create(
                id=match_data['id'],
                tournament_id=match_data['tournament_id'],
                round_number=match_data['round_number'] if match_data['round_number'] is not None else 1,
                map=match_data['map'],
                team1_id=match_data['team1_id'],
                team2_id=match_data['team2_id'],
                team1_score=match_data['team1_score'],
                team2_score=match_data['team2_score'],
                winner_id=match_data['winner_id'],
                match_time=match_data['match_time'],
                status=match_data['status'],
                is_lower_bracket=match_data['is_lower_bracket']
            )
            matches_created.append(match)
        imported_counts['Match'] = len(matches_created)
        
        # 7. 匯入遊戲
        print("🎮 匯入遊戲...")
        games_created = []
        for game_data in data['games']:
            game = Game.objects.create(
                id=game_data['id'],
                match_id=game_data['match_id'],
                map_number=game_data['map_number'],
                map_name=game_data['map_name'],
                team1_score=game_data['team1_score'],
                team2_score=game_data['team2_score'],
                winner_id=game_data['winner_id']
            )
            games_created.append(game)
        imported_counts['Game'] = len(games_created)
        
        # 8. 匯入統計資料 (關鍵！)
        print("📈 匯入統計資料...")
        stats_created = []
        for stat_data in data['player_stats']:
            stat = PlayerGameStat.objects.create(
                id=stat_data['id'],
                game_id=stat_data['game_id'],
                player_id=stat_data['player_id'],
                team_id=stat_data['team_id'],
                kills=stat_data['kills'],
                deaths=stat_data['deaths'],
                assists=stat_data['assists'],
                first_kills=stat_data['first_kills'],
                acs=stat_data['acs']
            )
            stats_created.append(stat)
        imported_counts['PlayerGameStat'] = len(stats_created)
    
    print("✅ Supabase 資料匯入完成：")
    for model, count in imported_counts.items():
        print(f"  - {model}: 新增 {count} 筆")
    
    return imported_counts

def main():
    """主程式：完整清空並重新匯入"""
    print("🔄 開始完整資料重新匯入流程")
    print("=" * 50)
    
    try:
        # 步驟 1: 清空 Supabase
        deleted_counts = clear_supabase_data()
        print()
        
        # 步驟 2: 從 Docker 獲取資料
        docker_data = get_docker_data()
        if not docker_data:
            print("❌ 無法獲取 Docker 資料，停止執行")
            return
        print()
        
        # 步驟 3: 匯入到 Supabase
        imported_counts = import_to_supabase(docker_data)
        print()
        
        # 步驟 4: 驗證結果
        print("🔍 驗證匯入結果...")
        current_counts = {
            'Tournament': Tournament.objects.count(),
            'Team': Team.objects.count(),
            'Group': Group.objects.count(),
            'Player': Player.objects.count(),
            'Match': Match.objects.count(),
            'Game': Game.objects.count(),
            'Standing': Standing.objects.count(),
            'PlayerGameStat': PlayerGameStat.objects.count(),
        }
        
        print("✅ 當前 Supabase 資料量：")
        for model, count in current_counts.items():
            print(f"  - {model}: {count} 筆")
        
        # 檢查統計資料樣本
        print()
        print("📊 統計資料樣本檢查...")
        sample_stats = PlayerGameStat.objects.select_related('player').all()[:3]
        for stat in sample_stats:
            print(f"  - {stat.player.nickname}: {stat.kills}殺/{stat.deaths}死/{stat.assists}助 (ACS: {stat.acs})")
        
        print()
        print("🎉 資料重新匯入完成！")
        print(f"📈 統計資料總數：{current_counts['PlayerGameStat']} 筆")
        
    except Exception as e:
        print(f"❌ 執行失敗：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
