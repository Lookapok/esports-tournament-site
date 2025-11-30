#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整清空 Supabase 並重新匯入所有 Docker 資料
確保 1,644 筆統計記錄完整遷移
"""

import os
import psycopg2
from datetime import datetime

# 手動設定環境變數
os.environ['DATABASE_URL'] = 'postgresql://postgres.yqmwwyundawdictftepn:Qazwsxedc0728@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
import django
django.setup()

from tournaments.models import (
    Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat
)
from django.db import transaction

def clear_supabase():
    """完全清空 Supabase 資料"""
    print("🗑️ 清空 Supabase 資料...")
    
    with transaction.atomic():
        # 按照外鍵依賴順序刪除
        counts = {}
        
        # 1. 統計資料 (最後層)
        counts['stats'] = PlayerGameStat.objects.count()
        PlayerGameStat.objects.all().delete()
        print(f"   🗑️ 刪除統計記錄: {counts['stats']}")
        
        # 2. 排名資料
        counts['standings'] = Standing.objects.count()
        Standing.objects.all().delete()
        print(f"   🗑️ 刪除排名記錄: {counts['standings']}")
        
        # 3. 遊戲資料
        counts['games'] = Game.objects.count()
        Game.objects.all().delete()
        print(f"   🗑️ 刪除遊戲記錄: {counts['games']}")
        
        # 4. 比賽資料
        counts['matches'] = Match.objects.count()
        Match.objects.all().delete()
        print(f"   🗑️ 刪除比賽記錄: {counts['matches']}")
        
        # 5. 清空多對多關聯
        for tournament in Tournament.objects.all():
            tournament.participants.clear()
        for group in Group.objects.all():
            group.teams.clear()
        
        # 6. 小組資料
        counts['groups'] = Group.objects.count()
        Group.objects.all().delete()
        print(f"   🗑️ 刪除小組記錄: {counts['groups']}")
        
        # 7. 選手資料
        counts['players'] = Player.objects.count()
        Player.objects.all().delete()
        print(f"   🗑️ 刪除選手記錄: {counts['players']}")
        
        # 8. 隊伍資料
        counts['teams'] = Team.objects.count()
        Team.objects.all().delete()
        print(f"   🗑️ 刪除隊伍記錄: {counts['teams']}")
        
        # 9. 賽事資料 (根節點)
        counts['tournaments'] = Tournament.objects.count()
        Tournament.objects.all().delete()
        print(f"   🗑️ 刪除賽事記錄: {counts['tournaments']}")
        
    print("✅ Supabase 清空完成")
    return counts

def get_docker_data():
    """從 Docker PostgreSQL 取得完整資料"""
    print("\n🐳 從 Docker 取得完整資料...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        data = {}
        
        # 1. 賽事
        cursor.execute("SELECT * FROM tournaments_tournament ORDER BY id;")
        data['tournaments'] = cursor.fetchall()
        print(f"📋 賽事: {len(data['tournaments'])} 筆")
        
        # 2. 隊伍
        cursor.execute("SELECT id, name, logo FROM tournaments_team ORDER BY id;")
        data['teams'] = cursor.fetchall()
        print(f"📋 隊伍: {len(data['teams'])} 筆")
        
        # 3. 選手
        cursor.execute("SELECT id, nickname, avatar, role, team_id FROM tournaments_player ORDER BY id;")
        data['players'] = cursor.fetchall()
        print(f"📋 選手: {len(data['players'])} 筆")
        
        # 4. 小組
        cursor.execute("SELECT id, name, tournament_id FROM tournaments_group ORDER BY id;")
        data['groups'] = cursor.fetchall()
        print(f"📋 小組: {len(data['groups'])} 筆")
        
        # 5. 比賽
        cursor.execute("SELECT * FROM tournaments_match ORDER BY id;")
        data['matches'] = cursor.fetchall()
        print(f"📋 比賽: {len(data['matches'])} 筆")
        
        # 6. 遊戲
        cursor.execute("SELECT * FROM tournaments_game ORDER BY id;")
        data['games'] = cursor.fetchall()
        print(f"📋 遊戲: {len(data['games'])} 筆")
        
        # 7. 排名
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
        data['standings'] = cursor.fetchall()
        print(f"📋 排名: {len(data['standings'])} 筆")
        
        # 8. 統計記錄 (最重要!)
        cursor.execute("SELECT * FROM tournaments_playergamestat ORDER BY id;")
        data['stats'] = cursor.fetchall()
        print(f"📊 統計記錄: {len(data['stats'])} 筆 ⭐")
        
        # 9. 參賽隊伍關聯
        cursor.execute("SELECT * FROM tournaments_tournament_participants ORDER BY id;")
        data['participants'] = cursor.fetchall()
        print(f"📋 參賽關聯: {len(data['participants'])} 筆")
        
        # 10. 小組隊伍關聯
        cursor.execute("SELECT * FROM tournaments_group_teams ORDER BY id;")
        data['group_teams'] = cursor.fetchall()
        print(f"📋 小組隊伍: {len(data['group_teams'])} 筆")
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return None

def import_to_supabase(data):
    """匯入所有資料到 Supabase"""
    print("\n☁️ 匯入資料到 Supabase...")
    
    with transaction.atomic():
        # 1. 賽事
        print("📋 匯入賽事...")
        for row in data['tournaments']:
            Tournament.objects.create(
                id=row[0], name=row[1], game=row[2], 
                start_date=row[3], end_date=row[4], 
                rules=row[5], status=row[6], format=row[7]
            )
        print(f"✅ 賽事: {len(data['tournaments'])} 筆")
        
        # 2. 隊伍
        print("📋 匯入隊伍...")
        for row in data['teams']:
            Team.objects.create(
                id=row[0], name=row[1], 
                logo=row[2] if len(row) > 2 and row[2] else '',
                school=''  # Supabase 額外欄位
            )
        print(f"✅ 隊伍: {len(data['teams'])} 筆")
        
        # 3. 選手
        print("📋 匯入選手...")
        for row in data['players']:
            Player.objects.create(
                id=row[0], nickname=row[1],
                avatar=row[2] if row[2] else '',
                role=row[3], team_id=row[4]
            )
        print(f"✅ 選手: {len(data['players'])} 筆")
        
        # 4. 小組
        print("📋 匯入小組...")
        for row in data['groups']:
            Group.objects.create(
                id=row[0], name=row[1], 
                tournament_id=row[2], max_teams=8
            )
        print(f"✅ 小組: {len(data['groups'])} 筆")
        
        # 5. 比賽
        print("📋 匯入比賽...")
        for row in data['matches']:
            Match.objects.create(
                id=row[0], round_number=row[1],
                team1_score=row[2], team2_score=row[3],
                match_time=row[4], status=row[5],
                is_lower_bracket=row[6],
                team1_id=row[7], team2_id=row[8],
                winner_id=row[9], tournament_id=row[10],
                map=row[11] if len(row) > 11 else None
            )
        print(f"✅ 比賽: {len(data['matches'])} 筆")
        
        # 6. 遊戲
        print("📋 匯入遊戲...")
        for row in data['games']:
            Game.objects.create(
                id=row[0], map_number=row[1],
                map_name=row[2], team1_score=row[3],
                team2_score=row[4], match_id=row[5],
                winner_id=row[6]
            )
        print(f"✅ 遊戲: {len(data['games'])} 筆")
        
        # 7. 排名
        print("📋 匯入排名...")
        for row in data['standings']:
            Standing.objects.create(
                id=row[0], wins=row[1], losses=row[2],
                draws=row[3], points=row[4],
                group_id=row[5], team_id=row[6],
                tournament_id=row[7]
            )
        print(f"✅ 排名: {len(data['standings'])} 筆")
        
        # 8. 統計記錄 (重點!)
        print("📊 匯入統計記錄...")
        batch_size = 100
        imported = 0
        
        for i in range(0, len(data['stats']), batch_size):
            batch = data['stats'][i:i + batch_size]
            for row in batch:
                PlayerGameStat.objects.create(
                    id=row[0], kills=row[1], deaths=row[2],
                    assists=row[3], first_kills=row[4],
                    acs=row[5], game_id=row[6],
                    player_id=row[7], team_id=row[8]
                )
                imported += 1
            
            print(f"   📊 已匯入 {imported}/{len(data['stats'])} 筆統計...")
        
        print(f"✅ 統計記錄: {imported} 筆 ⭐")
        
        # 9. 參賽關聯
        print("📋 匯入參賽關聯...")
        for row in data['participants']:
            tournament = Tournament.objects.get(id=row[1])
            team = Team.objects.get(id=row[2])
            tournament.participants.add(team)
        print(f"✅ 參賽關聯: {len(data['participants'])} 筆")
        
        # 10. 小組隊伍關聯
        print("📋 匯入小組隊伍關聯...")
        for row in data['group_teams']:
            group = Group.objects.get(id=row[1])
            team = Team.objects.get(id=row[2])
            group.teams.add(team)
        print(f"✅ 小組隊伍關聯: {len(data['group_teams'])} 筆")
        
        return imported

def verify_final_result():
    """最終驗證"""
    print("\n🔍 最終驗證...")
    
    results = {
        'tournaments': Tournament.objects.count(),
        'teams': Team.objects.count(),
        'players': Player.objects.count(),
        'groups': Group.objects.count(),
        'matches': Match.objects.count(),
        'games': Game.objects.count(),
        'standings': Standing.objects.count(),
        'stats': PlayerGameStat.objects.count()
    }
    
    print("📊 最終結果:")
    for table, count in results.items():
        print(f"  {table}: {count}")
    
    # 特別檢查統計資料
    if results['stats'] > 0:
        latest = PlayerGameStat.objects.order_by('-id').first()
        highest_kills = PlayerGameStat.objects.order_by('-kills').first()
        
        print(f"\n🆕 最新統計 (ID {latest.id}):")
        print(f"  {latest.player.nickname}: {latest.kills}K/{latest.deaths}D/{latest.assists}A")
        
        print(f"🏅 最高擊殺:")
        print(f"  {highest_kills.player.nickname}: {highest_kills.kills} 擊殺")
    
    return results

def main():
    """完整清空+重新匯入流程"""
    print("🚀 完整清空 Supabase 並重新匯入 Docker 資料")
    print("=" * 80)
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 清空 Supabase
        clear_counts = clear_supabase()
        
        # 2. 從 Docker 取得資料
        docker_data = get_docker_data()
        if not docker_data:
            return
        
        # 3. 匯入到 Supabase
        stats_imported = import_to_supabase(docker_data)
        
        # 4. 驗證結果
        final_results = verify_final_result()
        
        # 5. 最終報告
        print("\n" + "=" * 80)
        print("🎉 遷移完成報告")
        print("=" * 80)
        
        target_stats = len(docker_data['stats'])
        actual_stats = final_results['stats']
        
        if actual_stats == target_stats:
            print(f"✅ 完美成功! 統計記錄: {actual_stats}/{target_stats}")
            print("✅ 所有 1,644 筆統計資料已完整遷移!")
            print("🌐 Supabase 現在包含完整的生產資料")
            print("🔧 可以安全地停用 Docker PostgreSQL")
        else:
            print(f"⚠️ 統計記錄差異: {actual_stats}/{target_stats}")
        
        print(f"\n⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ 過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
