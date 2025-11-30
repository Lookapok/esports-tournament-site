#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整重新遷移：清空 Supabase 並重新匯入所有 Docker 資料
確保 1,644 筆統計記錄完整遷移
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

def clear_supabase_completely():
    """完全清空 Supabase 中的所有資料"""
    print("🗑️ 完全清空 Supabase 資料...")
    
    with transaction.atomic():
        # 按照外鍵依賴順序刪除
        deleted_counts = {}
        
        # 1. 統計資料 (最後層)
        count = PlayerGameStat.objects.count()
        PlayerGameStat.objects.all().delete()
        deleted_counts['PlayerGameStat'] = count
        print(f"   🗑️ 刪除統計記錄: {count}")
        
        # 2. 排名資料
        count = Standing.objects.count()
        Standing.objects.all().delete()
        deleted_counts['Standing'] = count
        print(f"   🗑️ 刪除排名記錄: {count}")
        
        # 3. 遊戲資料
        count = Game.objects.count()
        Game.objects.all().delete()
        deleted_counts['Game'] = count
        print(f"   🗑️ 刪除遊戲記錄: {count}")
        
        # 4. 比賽資料
        count = Match.objects.count()
        Match.objects.all().delete()
        deleted_counts['Match'] = count
        print(f"   🗑️ 刪除比賽記錄: {count}")
        
        # 5. 小組資料
        count = Group.objects.count()
        Group.objects.all().delete()
        deleted_counts['Group'] = count
        print(f"   🗑️ 刪除小組記錄: {count}")
        
        # 6. 選手資料
        count = Player.objects.count()
        Player.objects.all().delete()
        deleted_counts['Player'] = count
        print(f"   🗑️ 刪除選手記錄: {count}")
        
        # 7. 隊伍資料
        count = Team.objects.count()
        Team.objects.all().delete()
        deleted_counts['Team'] = count
        print(f"   🗑️ 刪除隊伍記錄: {count}")
        
        # 8. 賽事資料 (根節點)
        count = Tournament.objects.count()
        Tournament.objects.all().delete()
        deleted_counts['Tournament'] = count
        print(f"   🗑️ 刪除賽事記錄: {count}")
        
    print("✅ Supabase 清空完成")
    return deleted_counts

def get_docker_data():
    """從 Docker PostgreSQL 取得完整資料"""
    print("🐳 從 Docker 取得完整資料...")
    
    try:
        # 連接到 Docker PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        print("✅ 成功連接到 Docker PostgreSQL")
        
        # 取得所有資料
        data = {}
        
        # 1. 賽事
        cursor.execute("SELECT * FROM tournaments_tournament ORDER BY id;")
        data['tournaments'] = cursor.fetchall()
        print(f"📋 取得賽事資料: {len(data['tournaments'])} 筆")
        
        # 2. 隊伍
        cursor.execute("SELECT * FROM tournaments_team ORDER BY id;")
        data['teams'] = cursor.fetchall()
        print(f"📋 取得隊伍資料: {len(data['teams'])} 筆")
        
        # 3. 選手
        cursor.execute("SELECT * FROM tournaments_player ORDER BY id;")
        data['players'] = cursor.fetchall()
        print(f"📋 取得選手資料: {len(data['players'])} 筆")
        
        # 4. 小組
        cursor.execute("SELECT * FROM tournaments_group ORDER BY id;")
        data['groups'] = cursor.fetchall()
        print(f"📋 取得小組資料: {len(data['groups'])} 筆")
        
        # 5. 比賽
        cursor.execute("SELECT * FROM tournaments_match ORDER BY id;")
        data['matches'] = cursor.fetchall()
        print(f"📋 取得比賽資料: {len(data['matches'])} 筆")
        
        # 6. 遊戲
        cursor.execute("SELECT * FROM tournaments_game ORDER BY id;")
        data['games'] = cursor.fetchall()
        print(f"📋 取得遊戲資料: {len(data['games'])} 筆")
        
        # 7. 排名
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
        data['standings'] = cursor.fetchall()
        print(f"📋 取得排名資料: {len(data['standings'])} 筆")
        
        # 8. 統計記錄 - 重要！
        cursor.execute("SELECT * FROM tournaments_playergamestat ORDER BY id;")
        data['playergamestats'] = cursor.fetchall()
        print(f"📊 取得統計記錄: {len(data['playergamestats'])} 筆")
        
        # 取得欄位名稱
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tournaments_playergamestat' ORDER BY ordinal_position;")
        data['stat_columns'] = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return None

def import_to_supabase(docker_data):
    """將 Docker 資料匯入到 Supabase"""
    print("☁️ 匯入資料到 Supabase...")
    
    with transaction.atomic():
        # 1. 匯入賽事
        print("📋 匯入賽事...")
        for row in docker_data['tournaments']:
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
        print(f"✅ 匯入賽事完成: {len(docker_data['tournaments'])} 筆")
        
        # 2. 匯入隊伍
        print("📋 匯入隊伍...")
        for row in docker_data['teams']:
            Team.objects.create(
                id=row[0],
                name=row[1],
                school=row[2] if len(row) > 2 else "",
                logo=row[3] if len(row) > 3 and row[3] else None
            )
        print(f"✅ 匯入隊伍完成: {len(docker_data['teams'])} 筆")
        
        # 3. 匯入選手
        print("📋 匯入選手...")
        for row in docker_data['players']:
            Player.objects.create(
                id=row[0],
                nickname=row[1],
                team_id=row[2] if row[2] else None,
                avatar=row[3] if len(row) > 3 else None,
                role=row[4] if len(row) > 4 else None
            )
        print(f"✅ 匯入選手完成: {len(docker_data['players'])} 筆")
        
        # 4. 匯入小組
        print("📋 匯入小組...")
        for row in docker_data['groups']:
            Group.objects.create(
                id=row[0],
                tournament_id=row[1],
                name=row[2],
                format=row[3] if len(row) > 3 else None
            )
        print(f"✅ 匯入小組完成: {len(docker_data['groups'])} 筆")
        
        # 5. 匯入比賽
        print("📋 匯入比賽...")
        for row in docker_data['matches']:
            Match.objects.create(
                id=row[0],
                tournament_id=row[1],
                team1_id=row[2],
                team2_id=row[3],
                team1_score=row[4],
                team2_score=row[5],
                scheduled_time=row[6],
                status=row[7],
                winner_id=row[8] if row[8] else None,
                group_id=row[9] if len(row) > 9 and row[9] else None
            )
        print(f"✅ 匯入比賽完成: {len(docker_data['matches'])} 筆")
        
        # 6. 匯入遊戲
        print("📋 匯入遊戲...")
        for row in docker_data['games']:
            Game.objects.create(
                id=row[0],
                match_id=row[1],
                map_name=row[2],
                team1_score=row[3],
                team2_score=row[4],
                winner_id=row[5] if row[5] else None,
                duration=row[6] if len(row) > 6 else None
            )
        print(f"✅ 匯入遊戲完成: {len(docker_data['games'])} 筆")
        
        # 7. 匯入排名
        print("📋 匯入排名...")
        for row in docker_data['standings']:
            Standing.objects.create(
                id=row[0],
                tournament_id=row[1],
                team_id=row[2],
                position=row[3],
                points=row[4],
                matches_played=row[5],
                matches_won=row[6],
                matches_lost=row[7],
                games_won=row[8] if len(row) > 8 else 0,
                games_lost=row[9] if len(row) > 9 else 0
            )
        print(f"✅ 匯入排名完成: {len(docker_data['standings'])} 筆")
        
        # 8. 匯入統計記錄 - 最重要的部分！
        print("📊 匯入統計記錄...")
        imported_stats = 0
        for row in docker_data['playergamestats']:
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
                imported_stats += 1
                if imported_stats % 100 == 0:
                    print(f"   📊 已匯入 {imported_stats} 筆統計...")
            except Exception as e:
                print(f"   ⚠️ 統計記錄 {row[0]} 匯入失敗: {e}")
        
        print(f"✅ 匯入統計記錄完成: {imported_stats} 筆")
        
    return imported_stats

def verify_migration():
    """驗證遷移結果"""
    print("\n🔍 驗證遷移結果...")
    
    # 檢查數量
    stat_count = PlayerGameStat.objects.count()
    tournament_count = Tournament.objects.count()
    player_count = Player.objects.count()
    team_count = Team.objects.count()
    game_count = Game.objects.count()
    
    print(f"📊 統計記錄: {stat_count}")
    print(f"🏆 賽事數量: {tournament_count}")
    print(f"👤 選手數量: {player_count}")
    print(f"👥 隊伍數量: {team_count}")
    print(f"🎮 遊戲記錄: {game_count}")
    
    # 檢查最新記錄
    if stat_count > 0:
        latest_stat = PlayerGameStat.objects.order_by('-id').first()
        print(f"🆕 最新統計記錄 ID: {latest_stat.id}")
        print(f"   選手: {latest_stat.player.nickname}")
        print(f"   數據: {latest_stat.kills}K/{latest_stat.deaths}D/{latest_stat.assists}A")
    
    return stat_count

def main():
    """主要遷移流程"""
    print("🔄 開始完整重新遷移")
    print("=" * 60)
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 清空 Supabase
        clear_supabase_completely()
        print()
        
        # 2. 從 Docker 取得資料
        docker_data = get_docker_data()
        if not docker_data:
            print("❌ 無法取得 Docker 資料")
            return
        print()
        
        # 3. 匯入到 Supabase
        imported_stats = import_to_supabase(docker_data)
        print()
        
        # 4. 驗證結果
        final_count = verify_migration()
        
        print("\n" + "=" * 60)
        print("🎉 完整重新遷移完成！")
        print(f"📊 目標統計記錄: {len(docker_data['playergamestats'])}")
        print(f"📊 實際匯入記錄: {imported_stats}")
        print(f"📊 最終驗證記錄: {final_count}")
        
        if final_count == len(docker_data['playergamestats']):
            print("✅ 所有資料完美遷移！")
        else:
            print("⚠️ 仍有資料差異，需要進一步檢查")
        
        print(f"⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 遷移過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
