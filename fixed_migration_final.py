#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新檢查網路連接和執行完整遷移
修正欄位問題並處理網路連接
"""

import os
import sys
import django
import psycopg2
from datetime import datetime

# 手動載入環境變數
import os
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import (
    Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat
)
from django.db import transaction

def test_connections():
    """測試 Docker 和 Supabase 連接"""
    print("🔌 測試資料庫連接...")
    
    # 測試 Docker
    print("\n🐳 測試 Docker PostgreSQL:")
    try:
        docker_conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = docker_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tournaments_playergamestat;")
        docker_count = cursor.fetchone()[0]
        print(f"✅ Docker 連接成功，統計記錄: {docker_count}")
        cursor.close()
        docker_conn.close()
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return False
    
    # 測試 Supabase
    print("\n☁️ 測試 Supabase:")
    try:
        supabase_conn = psycopg2.connect(
            host="aws-1-ap-southeast-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.yqmwwyundawdictftepn",
            password="Qazwsxedc0728"
        )
        cursor = supabase_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tournaments_playergamestat;")
        supabase_count = cursor.fetchone()[0]
        print(f"✅ Supabase 連接成功，統計記錄: {supabase_count}")
        cursor.close()
        supabase_conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Supabase 連接失敗: {e}")
        return False

def check_table_structures():
    """檢查表格結構"""
    print("\n🔍 檢查 Docker 表格結構...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        # 檢查隊伍表結構
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_team' 
            ORDER BY ordinal_position;
        """)
        team_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 隊伍表欄位: {team_columns}")
        
        # 檢查選手表結構
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_player' 
            ORDER BY ordinal_position;
        """)
        player_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 選手表欄位: {player_columns}")
        
        # 檢查統計表結構
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_playergamestat' 
            ORDER BY ordinal_position;
        """)
        stat_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 統計表欄位: {stat_columns}")
        
        cursor.close()
        conn.close()
        
        return {
            'team_columns': team_columns,
            'player_columns': player_columns, 
            'stat_columns': stat_columns
        }
        
    except Exception as e:
        print(f"❌ 檢查結構失敗: {e}")
        return None

def clear_supabase_safely():
    """安全清空 Supabase"""
    print("\n🗑️ 清空 Supabase 資料...")
    
    try:
        with transaction.atomic():
            # 按依賴順序刪除
            counts = {}
            
            counts['stats'] = PlayerGameStat.objects.count()
            PlayerGameStat.objects.all().delete()
            
            counts['standings'] = Standing.objects.count()
            Standing.objects.all().delete()
            
            counts['games'] = Game.objects.count()
            Game.objects.all().delete()
            
            counts['matches'] = Match.objects.count()
            Match.objects.all().delete()
            
            counts['groups'] = Group.objects.count()
            Group.objects.all().delete()
            
            counts['players'] = Player.objects.count()
            Player.objects.all().delete()
            
            counts['teams'] = Team.objects.count()
            Team.objects.all().delete()
            
            counts['tournaments'] = Tournament.objects.count()
            Tournament.objects.all().delete()
            
        for table, count in counts.items():
            print(f"   🗑️ 刪除 {table}: {count} 筆")
            
        print("✅ Supabase 清空完成")
        return True
        
    except Exception as e:
        print(f"❌ 清空失敗: {e}")
        return False

def migrate_with_correct_structure():
    """使用正確的結構進行遷移"""
    print("\n🚀 開始遷移...")
    
    try:
        # 連接 Docker
        docker_conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = docker_conn.cursor()
        
        # 1. 遷移賽事
        print("📋 遷移賽事...")
        cursor.execute("SELECT * FROM tournaments_tournament ORDER BY id;")
        tournaments = cursor.fetchall()
        
        with transaction.atomic():
            for row in tournaments:
                Tournament.objects.create(
                    id=row[0],
                    name=row[1],
                    game=row[2],
                    start_date=row[3],
                    end_date=row[4],
                    rules=row[5],
                    status=row[6],
                    format=row[7]
                )
        print(f"✅ 遷移賽事完成: {len(tournaments)} 筆")
        
        # 2. 遷移隊伍 - 修正欄位
        print("📋 遷移隊伍...")
        cursor.execute("SELECT id, name, logo FROM tournaments_team ORDER BY id;")
        teams = cursor.fetchall()
        
        with transaction.atomic():
            for row in teams:
                Team.objects.create(
                    id=row[0],
                    name=row[1],
                    school='',  # Docker 沒有 school 欄位，設為空字串
                    logo=row[2] if len(row) > 2 and row[2] else None
                )
        print(f"✅ 遷移隊伍完成: {len(teams)} 筆")
        
        # 3. 遷移選手
        print("📋 遷移選手...")
        cursor.execute("SELECT id, nickname, team_id, avatar, role FROM tournaments_player ORDER BY id;")
        players = cursor.fetchall()
        
        with transaction.atomic():
            for row in players:
                Player.objects.create(
                    id=row[0],
                    nickname=row[1],
                    team_id=row[2] if row[2] else None,
                    avatar=row[3] if len(row) > 3 and row[3] else None,
                    role=row[4] if len(row) > 4 and row[4] else None
                )
        print(f"✅ 遷移選手完成: {len(players)} 筆")
        
        # 4. 遷移小組
        print("📋 遷移小組...")
        cursor.execute("SELECT * FROM tournaments_group ORDER BY id;")
        groups = cursor.fetchall()
        
        with transaction.atomic():
            for row in groups:
                Group.objects.create(
                    id=row[0],
                    tournament_id=row[1],
                    name=row[2],
                    max_teams=row[3] if len(row) > 3 else 8
                )
        print(f"✅ 遷移小組完成: {len(groups)} 筆")
        
        # 5. 遷移比賽
        print("📋 遷移比賽...")
        cursor.execute("SELECT * FROM tournaments_match ORDER BY id;")
        matches = cursor.fetchall()
        
        with transaction.atomic():
            for row in matches:
                Match.objects.create(
                    id=row[0],
                    tournament_id=row[1],
                    round_number=row[2] if len(row) > 2 else 1,
                    map=row[3] if len(row) > 3 else '',
                    team1_id=row[4] if len(row) > 4 else None,
                    team2_id=row[5] if len(row) > 5 else None,
                    team1_score=row[6] if len(row) > 6 else 0,
                    team2_score=row[7] if len(row) > 7 else 0,
                    winner_id=row[8] if len(row) > 8 and row[8] else None,
                    match_time=row[9] if len(row) > 9 else None,
                    status=row[10] if len(row) > 10 else 'scheduled',
                    is_lower_bracket=row[11] if len(row) > 11 else False
                )
        print(f"✅ 遷移比賽完成: {len(matches)} 筆")
        
        # 6. 遷移遊戲
        print("📋 遷移遊戲...")
        cursor.execute("SELECT * FROM tournaments_game ORDER BY id;")
        games = cursor.fetchall()
        
        with transaction.atomic():
            for row in games:
                Game.objects.create(
                    id=row[0],
                    match_id=row[1],
                    map_number=row[2] if len(row) > 2 else 1,
                    map_name=row[3] if len(row) > 3 else '',
                    team1_score=row[4] if len(row) > 4 else 0,
                    team2_score=row[5] if len(row) > 5 else 0,
                    winner_id=row[6] if len(row) > 6 and row[6] else None
                )
        print(f"✅ 遷移遊戲完成: {len(games)} 筆")
        
        # 7. 遷移排名
        print("📋 遷移排名...")
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
        standings = cursor.fetchall()
        
        with transaction.atomic():
            for row in standings:
                Standing.objects.create(
                    id=row[0],
                    tournament_id=row[1],
                    team_id=row[2],
                    group_id=row[3] if len(row) > 3 and row[3] else None,
                    position=row[4] if len(row) > 4 else 0,
                    points=row[5] if len(row) > 5 else 0,
                    matches_played=row[6] if len(row) > 6 else 0,
                    matches_won=row[7] if len(row) > 7 else 0,
                    matches_lost=row[8] if len(row) > 8 else 0,
                    games_won=row[9] if len(row) > 9 else 0,
                    games_lost=row[10] if len(row) > 10 else 0
                )
        print(f"✅ 遷移排名完成: {len(standings)} 筆")
        
        # 8. 遷移統計記錄 - 最重要！
        print("📊 遷移統計記錄...")
        cursor.execute("SELECT * FROM tournaments_playergamestat ORDER BY id;")
        stats = cursor.fetchall()
        
        imported_count = 0
        batch_size = 100
        
        with transaction.atomic():
            for i, row in enumerate(stats):
                try:
                    PlayerGameStat.objects.create(
                        id=row[0],
                        game_id=row[1],
                        player_id=row[2],
                        team_id=row[3],
                        kills=row[4],
                        deaths=row[5],
                        assists=row[6],
                        first_kills=row[7] if len(row) > 7 else 0,
                        acs=row[8] if len(row) > 8 else 0.0
                    )
                    imported_count += 1
                    
                    if (i + 1) % batch_size == 0:
                        print(f"   📊 已遷移 {i + 1}/{len(stats)} 筆統計...")
                        
                except Exception as e:
                    print(f"   ⚠️ 統計記錄 {row[0]} 失敗: {e}")
        
        print(f"✅ 遷移統計記錄完成: {imported_count} 筆")
        
        cursor.close()
        docker_conn.close()
        
        return imported_count
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        return 0

def verify_final_result():
    """驗證最終結果"""
    print("\n🔍 驗證遷移結果...")
    
    final_counts = {
        'tournaments': Tournament.objects.count(),
        'teams': Team.objects.count(),
        'players': Player.objects.count(),
        'groups': Group.objects.count(),
        'matches': Match.objects.count(),
        'games': Game.objects.count(),
        'standings': Standing.objects.count(),
        'stats': PlayerGameStat.objects.count()
    }
    
    for table, count in final_counts.items():
        print(f"📊 {table}: {count} 筆")
    
    # 檢查統計記錄
    if final_counts['stats'] > 0:
        latest = PlayerGameStat.objects.order_by('-id').first()
        print(f"\n🆕 最新統計記錄:")
        print(f"   ID: {latest.id}")
        print(f"   選手: {latest.player.nickname}")
        print(f"   數據: {latest.kills}K/{latest.deaths}D/{latest.assists}A")
    
    return final_counts

def main():
    """主執行流程"""
    print("🔄 完整重新遷移 - 修正版")
    print("=" * 60)
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 測試連接
    if not test_connections():
        print("❌ 連接測試失敗，無法繼續")
        return
    
    # 2. 檢查結構
    structures = check_table_structures()
    if not structures:
        print("❌ 結構檢查失敗")
        return
    
    # 3. 清空 Supabase
    if not clear_supabase_safely():
        print("❌ 清空失敗")
        return
    
    # 4. 執行遷移
    imported_stats = migrate_with_correct_structure()
    
    # 5. 驗證結果
    final_counts = verify_final_result()
    
    print("\n" + "=" * 60)
    print("🎉 遷移完成！")
    print(f"📊 統計記錄遷移: {imported_stats}")
    print(f"📊 最終統計記錄: {final_counts['stats']}")
    
    if final_counts['stats'] >= 1644:
        print("✅ 遷移成功！所有統計記錄都已遷移")
    else:
        print(f"⚠️ 部分遷移，預期 1644 筆，實際 {final_counts['stats']} 筆")
    
    print(f"⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
