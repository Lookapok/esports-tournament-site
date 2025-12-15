#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
從 Docker PostgreSQL 匯出完整資料並導入到 Supabase
包含球員統計資料 (PlayerGameStat)
"""

import json
import subprocess
import psycopg2
from datetime import datetime

def export_docker_data():
    """從 Docker PostgreSQL 匯出完整資料"""
    
    print("🐳 連接到 Docker PostgreSQL...")
    
    # Docker PostgreSQL 連線設定
    docker_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'esports_dev',
        'user': 'postgres',
        'password': 'esports123'  # 正確的密碼
    }
    
    try:
        # 連接到 Docker PostgreSQL
        conn = psycopg2.connect(**docker_config)
        cursor = conn.cursor()
        
        print("✅ 成功連接到 Docker PostgreSQL")
        
        # 匯出資料結構
        export_data = {}
        
        # 1. 匯出錦標賽資料
        print("📊 匯出錦標賽資料...")
        cursor.execute("SELECT id, name, game, start_date, end_date, rules, status, format FROM tournaments_tournament")
        tournaments = []
        for row in cursor.fetchall():
            tournaments.append({
                'id': row[0],
                'name': row[1],
                'game': row[2],
                'start_date': row[3].isoformat() if row[3] else None,
                'end_date': row[4].isoformat() if row[4] else None,
                'rules': row[5],
                'status': row[6],
                'format': row[7]
            })
        export_data['tournaments'] = tournaments
        print(f"  ✅ 匯出 {len(tournaments)} 筆錦標賽資料")
        
        # 2. 匯出隊伍資料
        print("🏆 匯出隊伍資料...")
        cursor.execute("SELECT id, name, logo FROM tournaments_team")
        teams = []
        for row in cursor.fetchall():
            teams.append({
                'id': row[0],
                'name': row[1],
                'logo': row[2] or ''
            })
        export_data['teams'] = teams
        print(f"  ✅ 匯出 {len(teams)} 筆隊伍資料")
        
        # 3. 匯出球員資料
        print("👥 匯出球員資料...")
        cursor.execute("SELECT id, nickname, team_id, avatar, role FROM tournaments_player")
        players = []
        for row in cursor.fetchall():
            players.append({
                'id': row[0],
                'nickname': row[1],
                'team_id': row[2],
                'avatar': row[3] or '',
                'role': row[4] or 'Flex'
            })
        export_data['players'] = players
        print(f"  ✅ 匯出 {len(players)} 筆球員資料")
        
        # 4. 匯出比賽資料
        print("⚔️ 匯出比賽資料...")
        cursor.execute("SELECT id, tournament_id, team1_id, team2_id, team1_score, team2_score, match_time, status FROM tournaments_match")
        matches = []
        for row in cursor.fetchall():
            matches.append({
                'id': row[0],
                'tournament_id': row[1],
                'team1_id': row[2],
                'team2_id': row[3],
                'team1_score': row[4],
                'team2_score': row[5],
                'match_date': row[6].isoformat() if row[6] else None,
                'status': row[7]
            })
        export_data['matches'] = matches
        print(f"  ✅ 匯出 {len(matches)} 筆比賽資料")
        
        # 5. 匯出遊戲資料
        print("🎮 匯出遊戲資料...")
        cursor.execute("SELECT id, match_id, map_name, team1_rounds, team2_rounds, winner_team_id FROM tournaments_game")
        games = []
        for row in cursor.fetchall():
            games.append({
                'id': row[0],
                'match_id': row[1],
                'map_name': row[2],
                'team1_rounds': row[3],
                'team2_rounds': row[4],
                'winner_team_id': row[5]
            })
        export_data['games'] = games
        print(f"  ✅ 匯出 {len(games)} 筆遊戲資料")
        
        # 6. 匯出分組資料
        print("📂 匯出分組資料...")
        cursor.execute("SELECT id, name, tournament_id FROM tournaments_group")
        groups = []
        for row in cursor.fetchall():
            groups.append({
                'id': row[0],
                'name': row[1],
                'tournament_id': row[2]
            })
        export_data['groups'] = groups
        print(f"  ✅ 匯出 {len(groups)} 筆分組資料")
        
        # 7. 匯出排名資料
        print("🏅 匯出排名資料...")
        cursor.execute("SELECT id, tournament_id, team_id, group_id, wins, losses, draws, points FROM tournaments_standing")
        standings = []
        for row in cursor.fetchall():
            standings.append({
                'id': row[0],
                'tournament_id': row[1],
                'team_id': row[2],
                'group_id': row[3],
                'wins': row[4],
                'losses': row[5],
                'draws': row[6],
                'points': row[7]
            })
        export_data['standings'] = standings
        print(f"  ✅ 匯出 {len(standings)} 筆排名資料")
        
        # 8. 📈 匯出球員統計資料 (重點！)
        print("📈 匯出球員統計資料...")
        cursor.execute("""
            SELECT id, game_id, player_id, team_id, kills, deaths, assists, first_kills, acs 
            FROM tournaments_playergamestat
        """)
        player_stats = []
        for row in cursor.fetchall():
            player_stats.append({
                'id': row[0],
                'game_id': row[1],
                'player_id': row[2],
                'team_id': row[3],
                'kills': row[4],
                'deaths': row[5],
                'assists': row[6],
                'first_kills': row[7],
                'acs': row[8]
            })
        export_data['player_stats'] = player_stats
        print(f"  ✅ 匯出 {len(player_stats)} 筆統計資料 (這就是關鍵資料！)")
        
        cursor.close()
        conn.close()
        
        # 儲存完整資料到檔案
        filename = f'complete_docker_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 資料匯出成功！")
        print(f"📁 檔案：{filename}")
        print(f"📊 統計：")
        print(f"  - 錦標賽：{len(tournaments)} 筆")
        print(f"  - 隊伍：{len(teams)} 筆")
        print(f"  - 球員：{len(players)} 筆")
        print(f"  - 比賽：{len(matches)} 筆")
        print(f"  - 遊戲：{len(games)} 筆")
        print(f"  - 分組：{len(groups)} 筆")
        print(f"  - 排名：{len(standings)} 筆")
        print(f"  - 統計：{len(player_stats)} 筆 📈")
        
        return filename, export_data
        
    except Exception as e:
        print(f"❌ 匯出失敗：{e}")
        return None, None

if __name__ == "__main__":
    export_docker_data()
