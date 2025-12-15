#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正小組問題後的完整遷移
"""

import os
import django
import psycopg2
from datetime import datetime

# 設定環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres.yqmwwyundawdictftepn:Qazwsxedc0728@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

django.setup()

from tournaments.models import *
from django.db import transaction
from django.db.models import signals
from tournaments.signals import update_standings_on_match_save

def main():
    print("🔄 繼續完成遷移...")
    
    # 停用 signals
    signals.post_save.disconnect(update_standings_on_match_save, sender=Match)
    
    try:
        # 取得 Docker 資料
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        with transaction.atomic():
            # 檢查當前狀態
            print(f"當前狀態: {Tournament.objects.count()} 賽事, {Team.objects.count()} 隊伍, {Player.objects.count()} 選手")
            
            # 小組
            cursor.execute("SELECT * FROM tournaments_group ORDER BY id;")
            groups_data = cursor.fetchall()
            print(f"準備匯入 {len(groups_data)} 個小組...")
            
            for row in groups_data:
                print(f"  匯入小組: ID={row[0]}, Name={row[1]}, Tournament={row[2]}")
                Group.objects.create(
                    id=row[0],
                    name=row[1],
                    tournament_id=row[2],
                    max_teams=8
                )
            print(f"✅ 小組匯入完成: {Group.objects.count()} 筆")
            
            # 排名 - 先匯入避免 signals 問題（但有重複資料問題，暫時跳過）
            print("⚠️ 跳過排名匯入（Docker資料有重複問題）")
            # cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
            # standings_data = cursor.fetchall()
            # print(f"準備匯入 {len(standings_data)} 個排名...")
            
            # for row in standings_data:
            #     # Standing 模型欄位: tournament, team, group, wins, losses, draws, points
            #     # Docker 資料: id, tournament_id, team_id, position, points, matches_played, matches_won, matches_lost, games_won, games_lost
            #     Standing.objects.create(
            #         id=row[0],
            #         tournament_id=row[1],
            #         team_id=row[2],
            #         # position -> 不對應，跳過
            #         points=row[4],
            #         # matches_played -> 不直接對應
            #         wins=row[6],  # matches_won
            #         losses=row[7],  # matches_lost
            #         draws=0,  # 預設值
            #         # games_won, games_lost -> 不對應
            #     )
            # print(f"✅ 排名匯入完成: {Standing.objects.count()} 筆")
            
            # 比賽
            cursor.execute("SELECT * FROM tournaments_match ORDER BY id;")
            matches_data = cursor.fetchall()
            print(f"準備匯入 {len(matches_data)} 場比賽...")
            
            for row in matches_data:
                Match.objects.create(
                    id=row[0],                    # id
                    tournament_id=row[10],        # tournament_id
                    round_number=row[1],          # round_number  
                    team1_id=row[7],              # team1_id
                    team2_id=row[8],              # team2_id
                    team1_score=row[2],           # team1_score
                    team2_score=row[3],           # team2_score
                    winner_id=row[9] if row[9] else None,  # winner_id
                    match_time=row[4],            # match_time
                    status=row[5],                # status
                    is_lower_bracket=row[6],      # is_lower_bracket
                    map=row[11] if len(row) > 11 else None  # map
                )
            print(f"✅ 比賽匯入完成: {Match.objects.count()} 筆")
            
            # 遊戲
            cursor.execute("SELECT * FROM tournaments_game ORDER BY id;")
            games_data = cursor.fetchall()
            print(f"準備匯入 {len(games_data)} 個遊戲...")
            
            for row in games_data:
                Game.objects.create(
                    id=row[0],                    # id
                    match_id=row[5],              # match_id
                    map_number=row[1],            # map_number
                    map_name=row[2],              # map_name
                    team1_score=row[3],           # team1_score
                    team2_score=row[4],           # team2_score
                    winner_id=row[6] if row[6] else None  # winner_id
                )
            print(f"✅ 遊戲匯入完成: {Game.objects.count()} 筆")
            
            # 統計記錄
            cursor.execute("SELECT * FROM tournaments_playergamestat ORDER BY id;")
            stats_data = cursor.fetchall()
            print(f"準備匯入 {len(stats_data)} 筆統計記錄...")
            
            imported = 0
            for row in stats_data:
                try:
                    PlayerGameStat.objects.create(
                        id=row[0],
                        kills=row[1],
                        deaths=row[2],
                        assists=row[3],
                        first_kills=row[4],
                        acs=row[5],
                        game_id=row[6],
                        player_id=row[7],
                        team_id=row[8]
                    )
                    imported += 1
                    if imported % 200 == 0:
                        print(f"   📊 已匯入 {imported} 筆統計...")
                except Exception as e:
                    print(f"   ⚠️ 統計記錄 {row[0]} 失敗: {e}")
            
            print(f"✅ 統計匯入完成: {imported} 筆")
            
        cursor.close()
        conn.close()
        
        print("\n🎉 完整遷移完成！")
        print(f"📊 最終統計記錄: {PlayerGameStat.objects.count()}")
        
        if PlayerGameStat.objects.count() == 1644:
            print("✅ 完美！所有 1,644 筆統計記錄都已遷移")
        else:
            print(f"⚠️ 預期 1,644 筆，實際 {PlayerGameStat.objects.count()} 筆")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 重新啟用 signals
        signals.post_save.connect(update_standings_on_match_save, sender=Match)

if __name__ == "__main__":
    main()
