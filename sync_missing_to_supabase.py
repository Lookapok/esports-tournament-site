#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增量同步：從 Docker 匯入球員和統計資料到 Supabase
保留現有的錦標賽、隊伍、比賽等基礎資料
"""

import os
import django
import psycopg2
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat

def sync_missing_data():
    """從 Docker 同步缺少的球員和統計資料"""
    
    print("🔄 增量同步：從 Docker 匯入缺少的資料到 Supabase")
    print("=" * 60)
    
    # Docker PostgreSQL 連線設定
    docker_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'esports_dev',
        'user': 'postgres',
        'password': 'esports123'
    }
    
    try:
        # 連接到 Docker PostgreSQL
        print("🐳 連接到 Docker PostgreSQL...")
        docker_conn = psycopg2.connect(**docker_config)
        docker_cursor = docker_conn.cursor()
        print("✅ Docker 連接成功")
        
        with transaction.atomic():
            
            # 1. 同步球員資料
            print("\n👥 同步球員資料...")
            print(f"   Supabase 目前球員數: {Player.objects.count()}")
            
            docker_cursor.execute("SELECT id, nickname, team_id, avatar, role FROM tournaments_player ORDER BY id")
            docker_players = docker_cursor.fetchall()
            print(f"   Docker 球員數: {len(docker_players)}")
            
            created_players = 0
            for player_data in docker_players:
                player_id, nickname, team_id, avatar, role = player_data
                
                # 檢查是否已存在
                if not Player.objects.filter(id=player_id).exists():
                    try:
                        # 找到對應的隊伍
                        team = Team.objects.get(id=team_id) if team_id else None
                        
                        # 創建球員
                        Player.objects.create(
                            id=player_id,
                            nickname=nickname,
                            team=team,
                            avatar=avatar or '',
                            role=role or 'Flex'
                        )
                        created_players += 1
                        
                        if created_players % 50 == 0:
                            print(f"   已創建 {created_players} 個球員...")
                            
                    except Team.DoesNotExist:
                        print(f"   ⚠️ 警告：隊伍 ID {team_id} 不存在，跳過球員 {nickname}")
                    except Exception as e:
                        print(f"   ❌ 創建球員失敗：{nickname} - {e}")
            
            print(f"   ✅ 新增 {created_players} 個球員")
            
            # 2. 同步遊戲資料
            print("\n🎮 同步遊戲資料...")
            print(f"   Supabase 目前遊戲數: {Game.objects.count()}")
            
            docker_cursor.execute("SELECT id, match_id, map_name, team1_rounds, team2_rounds, winner_team_id FROM tournaments_game ORDER BY id")
            docker_games = docker_cursor.fetchall()
            print(f"   Docker 遊戲數: {len(docker_games)}")
            
            created_games = 0
            for game_data in docker_games:
                game_id, match_id, map_name, team1_rounds, team2_rounds, winner_team_id = game_data
                
                if not Game.objects.filter(id=game_id).exists():
                    try:
                        match_obj = Match.objects.get(id=match_id) if match_id else None
                        winner_team = Team.objects.get(id=winner_team_id) if winner_team_id else None
                        
                        Game.objects.create(
                            id=game_id,
                            match=match_obj,
                            map_name=map_name,
                            team1_rounds=team1_rounds or 0,
                            team2_rounds=team2_rounds or 0,
                            winner_team=winner_team
                        )
                        created_games += 1
                        
                    except Match.DoesNotExist:
                        print(f"   ⚠️ 警告：比賽 ID {match_id} 不存在，跳過遊戲 {game_id}")
                    except Exception as e:
                        print(f"   ❌ 創建遊戲失敗：{game_id} - {e}")
            
            print(f"   ✅ 新增 {created_games} 個遊戲")
            
            # 3. 📈 同步統計資料 (重點！)
            print("\n📈 同步球員統計資料...")
            print(f"   Supabase 目前統計數: {PlayerGameStat.objects.count()}")
            
            docker_cursor.execute("""
                SELECT id, game_id, player_id, team_id, kills, deaths, assists, first_kills, acs 
                FROM tournaments_playergamestat 
                ORDER BY id
            """)
            docker_stats = docker_cursor.fetchall()
            print(f"   Docker 統計數: {len(docker_stats)}")
            
            created_stats = 0
            errors = 0
            
            for stat_data in docker_stats:
                stat_id, game_id, player_id, team_id, kills, deaths, assists, first_kills, acs = stat_data
                
                if not PlayerGameStat.objects.filter(id=stat_id).exists():
                    try:
                        game_obj = Game.objects.get(id=game_id) if game_id else None
                        player_obj = Player.objects.get(id=player_id) if player_id else None
                        team_obj = Team.objects.get(id=team_id) if team_id else None
                        
                        if game_obj and player_obj:
                            PlayerGameStat.objects.create(
                                id=stat_id,
                                game=game_obj,
                                player=player_obj,
                                team=team_obj,
                                kills=kills or 0,
                                deaths=deaths or 0,
                                assists=assists or 0,
                                first_kills=first_kills or 0,
                                acs=acs or 0
                            )
                            created_stats += 1
                            
                            if created_stats % 100 == 0:
                                print(f"   已創建 {created_stats} 筆統計...")
                        else:
                            errors += 1
                            
                    except (Game.DoesNotExist, Player.DoesNotExist, Team.DoesNotExist) as e:
                        errors += 1
                        if errors <= 5:  # 只顯示前5個錯誤
                            print(f"   ⚠️ 關聯資料不存在：統計 {stat_id} - {e}")
                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            print(f"   ❌ 創建統計失敗：{stat_id} - {e}")
            
            print(f"   ✅ 新增 {created_stats} 筆統計資料")
            if errors > 0:
                print(f"   ⚠️ 跳過 {errors} 筆有問題的統計")
        
        docker_cursor.close()
        docker_conn.close()
        
        print("\n🎉 增量同步完成！")
        print("=" * 60)
        print("📊 Supabase 最終狀態：")
        print(f"   錦標賽：{Tournament.objects.count()} 筆")
        print(f"   隊伍：{Team.objects.count()} 筆")
        print(f"   球員：{Player.objects.count()} 筆")
        print(f"   比賽：{Match.objects.count()} 筆")
        print(f"   遊戲：{Game.objects.count()} 筆")
        print(f"   分組：{Group.objects.count()} 筆")
        print(f"   排名：{Standing.objects.count()} 筆")
        print(f"   統計：{PlayerGameStat.objects.count()} 筆")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 同步失敗：{e}")
        raise

if __name__ == "__main__":
    sync_missing_data()
