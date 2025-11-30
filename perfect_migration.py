#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整且精確的 Docker → Supabase 資料遷移腳本
根據結構檢查結果進行精確遷移
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

def get_docker_data():
    """從 Docker PostgreSQL 取得完整資料"""
    print("🐳 從 Docker 取得完整資料...")
    
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
        
        # 1. 賽事 (根節點)
        cursor.execute("SELECT * FROM tournaments_tournament ORDER BY id;")
        data['tournaments'] = cursor.fetchall()
        print(f"📋 賽事: {len(data['tournaments'])} 筆")
        
        # 2. 隊伍 (只取 Docker 實際有的欄位)
        cursor.execute("SELECT id, name, logo FROM tournaments_team ORDER BY id;")
        data['teams'] = cursor.fetchall()
        print(f"📋 隊伍: {len(data['teams'])} 筆")
        
        # 3. 選手
        cursor.execute("SELECT id, nickname, avatar, role, team_id FROM tournaments_player ORDER BY id;")
        data['players'] = cursor.fetchall()
        print(f"📋 選手: {len(data['players'])} 筆")
        
        # 4. 小組 (只取 Docker 實際有的欄位)
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
        
        # 8. 統計記錄 (最重要)
        cursor.execute("SELECT * FROM tournaments_playergamestat ORDER BY id;")
        data['stats'] = cursor.fetchall()
        print(f"📊 統計記錄: {len(data['stats'])} 筆")
        
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
    """將資料匯入到 Supabase，按照依賴順序"""
    print("\n☁️ 匯入資料到 Supabase...")
    
    imported_counts = {}
    
    with transaction.atomic():
        try:
            # 1. 賽事 (根節點)
            print("📋 匯入賽事...")
            for row in data['tournaments']:
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
            imported_counts['tournaments'] = len(data['tournaments'])
            print(f"✅ 賽事匯入完成: {imported_counts['tournaments']} 筆")
            
            # 2. 隊伍 (處理額外的 school 欄位)
            print("📋 匯入隊伍...")
            for row in data['teams']:
                Team.objects.create(
                    id=row[0],
                    name=row[1],
                    logo=row[2] if len(row) > 2 and row[2] else '',
                    school=''  # Supabase 的額外欄位，設為空字串
                )
            imported_counts['teams'] = len(data['teams'])
            print(f"✅ 隊伍匯入完成: {imported_counts['teams']} 筆")
            
            # 3. 選手
            print("📋 匯入選手...")
            for row in data['players']:
                Player.objects.create(
                    id=row[0],
                    nickname=row[1],
                    avatar=row[2] if row[2] else '',
                    role=row[3],
                    team_id=row[4]
                )
            imported_counts['players'] = len(data['players'])
            print(f"✅ 選手匯入完成: {imported_counts['players']} 筆")
            
            # 4. 小組 (處理額外的 max_teams 欄位)
            print("📋 匯入小組...")
            for row in data['groups']:
                Group.objects.create(
                    id=row[0],
                    name=row[1],
                    tournament_id=row[2],
                    max_teams=8  # Supabase 的額外欄位，設為預設值
                )
            imported_counts['groups'] = len(data['groups'])
            print(f"✅ 小組匯入完成: {imported_counts['groups']} 筆")
            
            # 5. 比賽
            print("📋 匯入比賽...")
            for row in data['matches']:
                Match.objects.create(
                    id=row[0],
                    round_number=row[1],
                    team1_score=row[2],
                    team2_score=row[3],
                    match_time=row[4],
                    status=row[5],
                    is_lower_bracket=row[6],
                    team1_id=row[7],
                    team2_id=row[8],
                    winner_id=row[9],
                    tournament_id=row[10],
                    map=row[11] if len(row) > 11 else None
                )
            imported_counts['matches'] = len(data['matches'])
            print(f"✅ 比賽匯入完成: {imported_counts['matches']} 筆")
            
            # 6. 遊戲
            print("📋 匯入遊戲...")
            for row in data['games']:
                Game.objects.create(
                    id=row[0],
                    map_number=row[1],
                    map_name=row[2],
                    team1_score=row[3],
                    team2_score=row[4],
                    match_id=row[5],
                    winner_id=row[6]
                )
            imported_counts['games'] = len(data['games'])
            print(f"✅ 遊戲匯入完成: {imported_counts['games']} 筆")
            
            # 7. 排名
            print("📋 匯入排名...")
            for row in data['standings']:
                Standing.objects.create(
                    id=row[0],
                    wins=row[1],
                    losses=row[2],
                    draws=row[3],
                    points=row[4],
                    group_id=row[5],
                    team_id=row[6],
                    tournament_id=row[7]
                )
            imported_counts['standings'] = len(data['standings'])
            print(f"✅ 排名匯入完成: {imported_counts['standings']} 筆")
            
            # 8. 統計記錄 (最重要的部分!)
            print("📊 匯入統計記錄...")
            stats_imported = 0
            for row in data['stats']:
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
                stats_imported += 1
                if stats_imported % 200 == 0:
                    print(f"   📊 已匯入 {stats_imported}/{len(data['stats'])} 筆統計...")
            
            imported_counts['stats'] = stats_imported
            print(f"✅ 統計記錄匯入完成: {imported_counts['stats']} 筆")
            
            # 9. 參賽關聯
            print("📋 匯入參賽關聯...")
            for row in data['participants']:
                # 使用 Django ORM 建立多對多關聯
                tournament = Tournament.objects.get(id=row[1])
                team = Team.objects.get(id=row[2])
                tournament.participants.add(team)
            imported_counts['participants'] = len(data['participants'])
            print(f"✅ 參賽關聯匯入完成: {imported_counts['participants']} 筆")
            
            # 10. 小組隊伍關聯
            print("📋 匯入小組隊伍關聯...")
            for row in data['group_teams']:
                group = Group.objects.get(id=row[1])
                team = Team.objects.get(id=row[2])
                group.teams.add(team)
            imported_counts['group_teams'] = len(data['group_teams'])
            print(f"✅ 小組隊伍關聯匯入完成: {imported_counts['group_teams']} 筆")
            
            return imported_counts
            
        except Exception as e:
            print(f"❌ 匯入失敗: {e}")
            raise

def verify_migration():
    """驗證遷移結果"""
    print("\n🔍 驗證遷移結果...")
    
    results = {}
    
    # 檢查各表數量
    results['tournaments'] = Tournament.objects.count()
    results['teams'] = Team.objects.count()
    results['players'] = Player.objects.count()
    results['groups'] = Group.objects.count()
    results['matches'] = Match.objects.count()
    results['games'] = Game.objects.count()
    results['standings'] = Standing.objects.count()
    results['stats'] = PlayerGameStat.objects.count()
    
    print(f"📊 最終驗證結果:")
    print(f"  🏆 賽事: {results['tournaments']}")
    print(f"  👥 隊伍: {results['teams']}")
    print(f"  👤 選手: {results['players']}")
    print(f"  📋 小組: {results['groups']}")
    print(f"  ⚔️ 比賽: {results['matches']}")
    print(f"  🎮 遊戲: {results['games']}")
    print(f"  📊 排名: {results['standings']}")
    print(f"  📈 統計: {results['stats']}")
    
    # 檢查最重要的統計資料
    if results['stats'] > 0:
        latest_stat = PlayerGameStat.objects.order_by('-id').first()
        top_killer = PlayerGameStat.objects.order_by('-kills').first()
        
        print(f"\n🆕 最新統計記錄 (ID: {latest_stat.id}):")
        print(f"  選手: {latest_stat.player.nickname}")
        print(f"  數據: {latest_stat.kills}K/{latest_stat.deaths}D/{latest_stat.assists}A")
        
        print(f"\n🏅 最高擊殺記錄:")
        print(f"  選手: {top_killer.player.nickname}")
        print(f"  擊殺: {top_killer.kills} (死亡: {top_killer.deaths}, 助攻: {top_killer.assists})")
    
    return results

def main():
    """主遷移流程"""
    print("🚀 開始精確的 Docker → Supabase 資料遷移")
    print("=" * 70)
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 從 Docker 取得資料
        docker_data = get_docker_data()
        if not docker_data:
            print("❌ 無法取得 Docker 資料")
            return
        
        # 2. 匯入到 Supabase
        imported_counts = import_to_supabase(docker_data)
        
        # 3. 驗證結果
        final_results = verify_migration()
        
        # 4. 最終報告
        print("\n" + "=" * 70)
        print("🎉 資料遷移完成!")
        print("=" * 70)
        
        success = True
        expected_counts = {
            'tournaments': 1,
            'teams': 34,
            'players': 231,
            'matches': 144,
            'games': 171,
            'standings': 34,
            'stats': 1644  # 最重要的檢查
        }
        
        for table, expected in expected_counts.items():
            actual = final_results[table]
            if actual == expected:
                print(f"✅ {table}: {actual}/{expected}")
            else:
                print(f"❌ {table}: {actual}/{expected} (差異: {actual - expected:+d})")
                success = False
        
        if success:
            print("\n🎉 完美成功! 所有 1,644 筆統計資料已完整遷移!")
            print("✅ 可以安全地停用 Docker PostgreSQL")
            print("🌐 Supabase 現在包含所有生產資料")
        else:
            print("\n⚠️ 部分資料遷移有問題，需要檢查")
        
        print(f"\n⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ 遷移過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
