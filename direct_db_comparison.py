#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接比較 Docker PostgreSQL 和 Supabase 資料庫的資料數量
"""

import psycopg2

def check_docker_data():
    """檢查 Docker PostgreSQL 中的資料數量"""
    
    print("🐳 檢查 Docker PostgreSQL 資料")
    print("=" * 50)
    
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
        
        # 檢查統計資料數量
        cursor.execute("SELECT COUNT(*) FROM tournaments_playergamestat;")
        docker_stats = cursor.fetchone()[0]
        print(f"📊 Docker 統計記錄: {docker_stats}")
        
        # 檢查其他資料表
        cursor.execute("SELECT COUNT(*) FROM tournaments_player;")
        docker_players = cursor.fetchone()[0]
        print(f"👤 Docker 選手數量: {docker_players}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_team;")
        docker_teams = cursor.fetchone()[0]
        print(f"👥 Docker 隊伍數量: {docker_teams}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_tournament;")
        docker_tournaments = cursor.fetchone()[0]
        print(f"🏆 Docker 賽事數量: {docker_tournaments}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_game;")
        docker_games = cursor.fetchone()[0]
        print(f"🎮 Docker 遊戲記錄: {docker_games}")
        
        # 檢查最新的幾筆記錄
        print("\n🔍 Docker 最新 3 筆統計記錄:")
        cursor.execute("""
            SELECT p.nickname, pgs.kills, pgs.deaths, pgs.assists, pgs.id
            FROM tournaments_playergamestat pgs
            JOIN tournaments_player p ON pgs.player_id = p.id
            ORDER BY pgs.id DESC
            LIMIT 3;
        """)
        
        latest_records = cursor.fetchall()
        for i, record in enumerate(latest_records, 1):
            print(f"  {i}. {record[0]}: {record[1]}K/{record[2]}D/{record[3]}A (ID: {record[4]})")
        
        cursor.close()
        conn.close()
        
        return {
            'stats': docker_stats,
            'players': docker_players,
            'teams': docker_teams,
            'tournaments': docker_tournaments,
            'games': docker_games
        }
        
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return None

def check_supabase_data():
    """檢查 Supabase 中的資料數量"""
    
    print("\n☁️ 檢查 Supabase 資料")
    print("=" * 50)
    
    try:
        # 連接到 Supabase
        conn = psycopg2.connect(
            host="aws-1-ap-southeast-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.yqmwwyundawdictftepn",
            password="Qazwsxedc0728"
        )
        cursor = conn.cursor()
        
        print("✅ 成功連接到 Supabase")
        
        # 檢查統計資料數量
        cursor.execute("SELECT COUNT(*) FROM tournaments_playergamestat;")
        supabase_stats = cursor.fetchone()[0]
        print(f"📊 Supabase 統計記錄: {supabase_stats}")
        
        # 檢查其他資料表
        cursor.execute("SELECT COUNT(*) FROM tournaments_player;")
        supabase_players = cursor.fetchone()[0]
        print(f"👤 Supabase 選手數量: {supabase_players}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_team;")
        supabase_teams = cursor.fetchone()[0]
        print(f"👥 Supabase 隊伍數量: {supabase_teams}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_tournament;")
        supabase_tournaments = cursor.fetchone()[0]
        print(f"🏆 Supabase 賽事數量: {supabase_tournaments}")
        
        cursor.execute("SELECT COUNT(*) FROM tournaments_game;")
        supabase_games = cursor.fetchone()[0]
        print(f"🎮 Supabase 遊戲記錄: {supabase_games}")
        
        # 檢查最新的幾筆記錄
        print("\n🔍 Supabase 最新 3 筆統計記錄:")
        cursor.execute("""
            SELECT p.nickname, pgs.kills, pgs.deaths, pgs.assists, pgs.id
            FROM tournaments_playergamestat pgs
            JOIN tournaments_player p ON pgs.player_id = p.id
            ORDER BY pgs.id DESC
            LIMIT 3;
        """)
        
        latest_records = cursor.fetchall()
        for i, record in enumerate(latest_records, 1):
            print(f"  {i}. {record[0]}: {record[1]}K/{record[2]}D/{record[3]}A (ID: {record[4]})")
        
        cursor.close()
        conn.close()
        
        return {
            'stats': supabase_stats,
            'players': supabase_players,
            'teams': supabase_teams,
            'tournaments': supabase_tournaments,
            'games': supabase_games
        }
        
    except Exception as e:
        print(f"❌ Supabase 連接失敗: {e}")
        return None

def compare_data():
    """比較兩個資料庫的資料"""
    
    print("🔄 比較 Docker 和 Supabase 資料數量")
    print("=" * 80)
    
    docker_data = check_docker_data()
    supabase_data = check_supabase_data()
    
    if docker_data and supabase_data:
        print("\n📊 資料比較結果:")
        print("=" * 50)
        print(f"{'項目':<15} {'Docker':<10} {'Supabase':<12} {'差異'}")
        print("-" * 50)
        
        categories = {
            '統計記錄': 'stats',
            '選手數量': 'players', 
            '隊伍數量': 'teams',
            '賽事數量': 'tournaments',
            '遊戲記錄': 'games'
        }
        
        total_diff = 0
        for category, key in categories.items():
            docker_count = docker_data[key]
            supabase_count = supabase_data[key]
            diff = docker_count - supabase_count
            total_diff += abs(diff)
            
            status = "✅" if diff == 0 else "⚠️" if diff > 0 else "❌"
            print(f"{category:<15} {docker_count:<10} {supabase_count:<12} {diff:+d} {status}")
        
        print("\n" + "=" * 50)
        if total_diff == 0:
            print("🎉 完美！所有資料都已完整遷移")
        else:
            print(f"⚠️ 發現 {total_diff} 筆資料差異")
            if docker_data['stats'] > supabase_data['stats']:
                print("🔄 建議重新執行完整遷移")
            else:
                print("🔍 需要進一步調查差異原因")

if __name__ == "__main__":
    compare_data()
