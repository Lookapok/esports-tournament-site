#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Docker SQLite 到 Supabase PostgreSQL 遷移腳本
處理資料庫間的兼容性問題
"""

import os
import sys
import django
import json
from datetime import datetime
from django.utils import timezone

# 設定編碼
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing
from django.db import transaction
from django.core.exceptions import ValidationError

def clean_data_for_postgresql(data):
    """清理資料以適應 PostgreSQL"""
    print("🔧 正在清理資料以適應 PostgreSQL...")
    
    # 清理錦標賽資料
    for item in data.get('tournaments', []):
        # 確保日期格式正確
        if item.get('start_date'):
            try:
                # 嘗試解析不同的日期格式
                if isinstance(item['start_date'], str):
                    # 移除時區資訊以避免衝突
                    date_str = item['start_date'].replace('+00:00', '').replace('Z', '')
                    if 'T' in date_str:
                        item['start_date'] = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                    else:
                        item['start_date'] = date_str
            except:
                item['start_date'] = None
                
        if item.get('end_date'):
            try:
                if isinstance(item['end_date'], str):
                    date_str = item['end_date'].replace('+00:00', '').replace('Z', '')
                    if 'T' in date_str:
                        item['end_date'] = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                    else:
                        item['end_date'] = date_str
            except:
                item['end_date'] = None
    
    # 清理比賽資料
    for item in data.get('matches', []):
        if item.get('match_time'):
            try:
                if isinstance(item['match_time'], str):
                    date_str = item['match_time'].replace('+00:00', '').replace('Z', '')
                    if 'T' in date_str:
                        item['match_time'] = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                    else:
                        item['match_time'] = date_str
            except:
                item['match_time'] = None
    
    # 清理外鍵為 null 的情況
    for item in data.get('standings', []):
        if item.get('group_id') == '':
            item['group_id'] = None
    
    for item in data.get('matches', []):
        if item.get('winner_id') == '':
            item['winner_id'] = None
            
    print("✅ 資料清理完成")
    return data

def reset_postgresql_sequences():
    """重置 PostgreSQL 序列，避免主鍵衝突"""
    print("🔄 重置 PostgreSQL 序列...")
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # 獲取所有表的序列
        tables = [
            ('tournaments_tournament', 'id'),
            ('tournaments_team', 'id'),
            ('tournaments_player', 'id'),
            ('tournaments_match', 'id'),
            ('tournaments_game', 'id'),
            ('tournaments_group', 'id'),
            ('tournaments_standing', 'id'),
        ]
        
        for table, pk_field in tables:
            try:
                # 獲取當前最大 ID
                cursor.execute(f"SELECT MAX({pk_field}) FROM {table}")
                max_id = cursor.fetchone()[0]
                
                if max_id:
                    # 設定序列的下一個值
                    cursor.execute(f"SELECT setval('{table}_{pk_field}_seq', {max_id})")
                    print(f"  ✅ {table}: 序列設定為 {max_id + 1}")
            except Exception as e:
                print(f"  ⚠️ {table}: 序列重置失敗 - {e}")
    
    print("✅ 序列重置完成")

def migrate_data_to_supabase():
    """遷移資料到 Supabase"""
    try:
        print("🚀 開始 Docker -> Supabase 資料遷移...")
        
        # 檢查 production_data.json 是否存在
        if not os.path.exists('production_data.json'):
            print("❌ production_data.json 不存在！請先從 Docker 環境匯出資料")
            return False
        
        # 載入資料
        print("📖 讀取資料檔案...")
        with open('production_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 顯示原始資料統計
        print(f"📊 原始資料統計:")
        print(f"  - 錦標賽: {len(data.get('tournaments', []))}")
        print(f"  - 隊伍: {len(data.get('teams', []))}")
        print(f"  - 選手: {len(data.get('players', []))}")
        print(f"  - 比賽: {len(data.get('matches', []))}")
        print(f"  - 遊戲: {len(data.get('games', []))}")
        print(f"  - 分組: {len(data.get('groups', []))}")
        print(f"  - 積分榜: {len(data.get('standings', []))}")
        
        # 清理資料
        data = clean_data_for_postgresql(data)
        
        # 檢查目前資料庫狀態
        print("🔍 檢查目前資料庫狀態...")
        print(f"  - 現有錦標賽: {Tournament.objects.count()}")
        print(f"  - 現有隊伍: {Team.objects.count()}")
        print(f"  - 現有選手: {Player.objects.count()}")
        
        # 詢問是否清空現有資料
        print("\n⚠️ 注意：此操作將清空現有資料並重新匯入")
        
        # 在事務中執行遷移
        with transaction.atomic():
            print("🗑️ 清空現有資料...")
            Standing.objects.all().delete()
            Game.objects.all().delete()
            Match.objects.all().delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            Group.objects.all().delete()
            Tournament.objects.all().delete()
            
            # 依序匯入資料（注意外鍵依賴順序）
            print("📥 開始匯入資料...")
            
            # 1. 匯入錦標賽（無外鍵依賴）
            tournaments_imported = 0
            for item in data.get('tournaments', []):
                try:
                    Tournament.objects.create(
                        id=item['id'],
                        name=item['name'],
                        game=item.get('game', ''),
                        start_date=item.get('start_date'),
                        end_date=item.get('end_date'),
                        rules=item.get('rules', ''),
                        status=item.get('status', 'upcoming'),
                        format=item.get('format', 'single_elimination')
                    )
                    tournaments_imported += 1
                except Exception as e:
                    print(f"  ❌ 錦標賽匯入失敗: {item.get('name')} - {e}")
            print(f"  ✅ 錦標賽匯入完成: {tournaments_imported} 筆")
            
            # 2. 匯入隊伍（無外鍵依賴）
            teams_imported = 0
            for item in data.get('teams', []):
                try:
                    Team.objects.create(
                        id=item['id'],
                        name=item['name'],
                        school=item.get('school', ''),
                        logo=item.get('logo', '')
                    )
                    teams_imported += 1
                except Exception as e:
                    print(f"  ❌ 隊伍匯入失敗: {item.get('name')} - {e}")
            print(f"  ✅ 隊伍匯入完成: {teams_imported} 筆")
            
            # 3. 匯入分組（依賴錦標賽）
            groups_imported = 0
            for item in data.get('groups', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    Group.objects.create(
                        id=item['id'],
                        tournament=tournament,
                        name=item['name'],
                        max_teams=item.get('max_teams', 8)
                    )
                    groups_imported += 1
                except Exception as e:
                    print(f"  ❌ 分組匯入失敗: {item.get('name')} - {e}")
            print(f"  ✅ 分組匯入完成: {groups_imported} 筆")
            
            # 4. 匯入選手（依賴隊伍）
            players_imported = 0
            for item in data.get('players', []):
                try:
                    team = Team.objects.get(id=item['team_id'])
                    Player.objects.create(
                        id=item['id'],
                        name=item['name'],
                        team=team,
                        position=item.get('position', ''),
                        avatar=item.get('avatar', '')
                    )
                    players_imported += 1
                except Exception as e:
                    print(f"  ❌ 選手匯入失敗: {item.get('name')} - {e}")
            print(f"  ✅ 選手匯入完成: {players_imported} 筆")
            
            # 5. 匯入比賽（依賴錦標賽和隊伍）
            matches_imported = 0
            for item in data.get('matches', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team1 = Team.objects.get(id=item['team1_id'])
                    team2 = Team.objects.get(id=item['team2_id'])
                    winner = None
                    if item.get('winner_id'):
                        winner = Team.objects.get(id=item['winner_id'])
                    
                    Match.objects.create(
                        id=item['id'],
                        tournament=tournament,
                        round_number=item.get('round_number', 1),
                        map=item.get('map', ''),
                        team1=team1,
                        team2=team2,
                        team1_score=item.get('team1_score', 0),
                        team2_score=item.get('team2_score', 0),
                        winner=winner,
                        match_time=item.get('match_time'),
                        status=item.get('status', 'scheduled'),
                        is_lower_bracket=item.get('is_lower_bracket', False)
                    )
                    matches_imported += 1
                except Exception as e:
                    print(f"  ❌ 比賽匯入失敗: Match {item.get('id')} - {e}")
            print(f"  ✅ 比賽匯入完成: {matches_imported} 筆")
            
            # 6. 匯入遊戲（依賴比賽）
            games_imported = 0
            for item in data.get('games', []):
                try:
                    match = Match.objects.get(id=item['match_id'])
                    winner = None
                    if item.get('winner_id'):
                        winner = Team.objects.get(id=item['winner_id'])
                    
                    Game.objects.create(
                        id=item['id'],
                        match=match,
                        map_number=item.get('map_number', 1),
                        map_name=item.get('map_name', ''),
                        team1_score=item.get('team1_score', 0),
                        team2_score=item.get('team2_score', 0),
                        winner=winner
                    )
                    games_imported += 1
                except Exception as e:
                    print(f"  ❌ 遊戲匯入失敗: Game {item.get('id')} - {e}")
            print(f"  ✅ 遊戲匯入完成: {games_imported} 筆")
            
            # 7. 匯入積分榜（依賴錦標賽、隊伍、分組）
            standings_imported = 0
            for item in data.get('standings', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team = Team.objects.get(id=item['team_id'])
                    group = None
                    if item.get('group_id'):
                        group = Group.objects.get(id=item['group_id'])
                    
                    # 使用 unique_together 約束
                    standing, created = Standing.objects.get_or_create(
                        tournament=tournament,
                        team=team,
                        defaults={
                            'group': group,
                            'wins': item.get('wins', 0),
                            'losses': item.get('losses', 0),
                            'draws': item.get('draws', 0),
                            'points': item.get('points', 0)
                        }
                    )
                    if created:
                        standings_imported += 1
                except Exception as e:
                    print(f"  ❌ 積分榜匯入失敗: {e}")
            print(f"  ✅ 積分榜匯入完成: {standings_imported} 筆")
        
        # 重置序列
        reset_postgresql_sequences()
        
        # 最終驗證
        print("\n🔍 遷移完成驗證:")
        print(f"  - 錦標賽: {Tournament.objects.count()}")
        print(f"  - 隊伍: {Team.objects.count()}")
        print(f"  - 選手: {Player.objects.count()}")
        print(f"  - 比賽: {Match.objects.count()}")
        print(f"  - 遊戲: {Game.objects.count()}")
        print(f"  - 分組: {Group.objects.count()}")
        print(f"  - 積分榜: {Standing.objects.count()}")
        
        print("\n🎉 Docker 到 Supabase 遷移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_data_to_supabase()
