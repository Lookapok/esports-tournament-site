#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整檢查 Docker 和 Supabase 的所有資料遷移狀況
"""

import os
import psycopg2

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')

# 手動載入 .env 檔案
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    print("⚠️ .env 檔案未找到")

import django
django.setup()

from tournaments.models import *

def check_docker_all_data():
    """檢查 Docker PostgreSQL 中的完整資料"""
    
    print("🐳 檢查 Docker PostgreSQL 完整資料")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        tables_info = {
            'tournaments_tournament': '🏆 賽事',
            'tournaments_team': '👥 隊伍', 
            'tournaments_player': '👤 選手',
            'tournaments_group': '📋 小組',
            'tournaments_match': '⚔️ 比賽',
            'tournaments_game': '🎮 遊戲',
            'tournaments_standing': '📊 排名',
            'tournaments_playergamestat': '📈 統計',
            'tournaments_group_teams': '🔗 小組-隊伍關聯',
            'tournaments_tournament_participants': '🔗 賽事-參賽者關聯'
        }
        
        docker_data = {}
        
        for table, description in tables_info.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                docker_data[table] = count
                print(f"{description:<15} {count:>6} 筆")
                
                # 顯示前幾筆資料
                if count > 0 and count <= 5:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                    samples = cursor.fetchall()
                    for i, sample in enumerate(samples, 1):
                        print(f"  範例{i}: {sample[:3]}...")
                        
            except Exception as e:
                print(f"{description:<15} ❌ 錯誤: {e}")
                docker_data[table] = 0
        
        cursor.close()
        conn.close()
        return docker_data
        
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return None

def check_supabase_all_data():
    """檢查 Supabase 中的完整資料"""
    
    print("\n☁️ 檢查 Supabase 完整資料")
    print("=" * 60)
    
    # 使用 Django ORM 檢查
    models_info = {
        Tournament: '🏆 賽事',
        Team: '👥 隊伍',
        Player: '👤 選手', 
        Group: '📋 小組',
        Match: '⚔️ 比賽',
        Game: '🎮 遊戲',
        Standing: '📊 排名',
        PlayerGameStat: '📈 統計'
    }
    
    supabase_data = {}
    
    for model, description in models_info.items():
        try:
            count = model.objects.count()
            supabase_data[f"tournaments_{model._meta.model_name}"] = count
            print(f"{description:<15} {count:>6} 筆")
            
            # 顯示最新的幾筆資料
            if count > 0:
                latest = model.objects.order_by('-id').first()
                print(f"  最新記錄: ID={latest.id}")
                
        except Exception as e:
            print(f"{description:<15} ❌ 錯誤: {e}")
            supabase_data[f"tournaments_{model._meta.model_name}"] = 0
    
    # 檢查關聯表
    try:
        # Group-Team 關聯
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tournaments_group_teams;")
            group_teams_count = cursor.fetchone()[0]
            supabase_data['tournaments_group_teams'] = group_teams_count
            print(f"{'🔗 小組-隊伍關聯':<15} {group_teams_count:>6} 筆")
            
            # Tournament-Participants 關聯
            cursor.execute("SELECT COUNT(*) FROM tournaments_tournament_participants;")
            participants_count = cursor.fetchone()[0]
            supabase_data['tournaments_tournament_participants'] = participants_count
            print(f"{'🔗 賽事-參賽者關聯':<15} {participants_count:>6} 筆")
            
    except Exception as e:
        print(f"🔗 關聯表檢查失敗: {e}")
    
    return supabase_data

def compare_all_data():
    """比較所有資料"""
    
    print("\n🔄 完整資料遷移比較")
    print("=" * 80)
    
    docker_data = check_docker_all_data()
    supabase_data = check_supabase_all_data()
    
    if docker_data and supabase_data:
        print(f"\n📊 詳細比較結果:")
        print("=" * 80)
        print(f"{'資料表':<25} {'Docker':<10} {'Supabase':<10} {'差異':<10} {'狀態'}")
        print("-" * 80)
        
        all_tables = set(docker_data.keys()) | set(supabase_data.keys())
        total_missing = 0
        perfect_matches = 0
        
        for table in sorted(all_tables):
            docker_count = docker_data.get(table, 0)
            supabase_count = supabase_data.get(table, 0)
            diff = docker_count - supabase_count
            total_missing += abs(diff)
            
            if diff == 0:
                status = "✅ 完美"
                perfect_matches += 1
            elif diff > 0:
                status = "⚠️ 缺少"
            else:
                status = "❓ 多餘"
                
            # 簡化表名顯示
            display_name = table.replace('tournaments_', '')
            print(f"{display_name:<25} {docker_count:<10} {supabase_count:<10} {diff:>+4d}      {status}")
        
        print("\n" + "=" * 80)
        print(f"📈 總結報告:")
        print(f"  🎯 完美匹配表格: {perfect_matches}/{len(all_tables)}")
        print(f"  📊 總差異記錄數: {total_missing}")
        
        if total_missing == 0:
            print("  🎉 完美！所有資料都已完整遷移")
        else:
            print(f"  ⚠️ 仍有 {total_missing} 筆資料差異")
            
        # 檢查最重要的統計資料
        stats_docker = docker_data.get('tournaments_playergamestat', 0)
        stats_supabase = supabase_data.get('tournaments_playergamestat', 0)
        if stats_docker > 0:
            completion_rate = (stats_supabase / stats_docker) * 100
            print(f"  📊 統計資料完成度: {completion_rate:.1f}% ({stats_supabase}/{stats_docker})")

def check_data_integrity():
    """檢查資料完整性和關聯"""
    
    print(f"\n🔍 資料完整性檢查")
    print("=" * 50)
    
    try:
        # 檢查外鍵關聯
        print("🔗 檢查外鍵關聯:")
        
        # 1. 選手-隊伍關聯
        players_with_teams = Player.objects.filter(team__isnull=False).count()
        total_players = Player.objects.count()
        print(f"  👤 選手有隊伍: {players_with_teams}/{total_players}")
        
        # 2. 統計-選手關聯
        stats_with_players = PlayerGameStat.objects.count()
        unique_players_in_stats = PlayerGameStat.objects.values('player').distinct().count()
        print(f"  📈 統計記錄: {stats_with_players} 筆，涉及 {unique_players_in_stats} 名選手")
        
        # 3. 比賽-隊伍關聯
        matches_with_teams = Match.objects.filter(team1__isnull=False, team2__isnull=False).count()
        total_matches = Match.objects.count()
        print(f"  ⚔️ 比賽有隊伍: {matches_with_teams}/{total_matches}")
        
        # 4. 遊戲-比賽關聯
        games_with_matches = Game.objects.count()
        unique_matches_in_games = Game.objects.values('match').distinct().count()
        print(f"  🎮 遊戲記錄: {games_with_matches} 筆，涉及 {unique_matches_in_games} 場比賽")
        
        print("\n📊 資料品質檢查:")
        
        # 檢查頂尖選手
        if PlayerGameStat.objects.exists():
            top_killers = PlayerGameStat.objects.order_by('-kills')[:3]
            print("  🏆 擊殺王前3名:")
            for i, stat in enumerate(top_killers, 1):
                print(f"    {i}. {stat.player.nickname}: {stat.kills} 擊殺")
                
        # 檢查比賽結果
        completed_matches = Match.objects.filter(status='completed').count()
        print(f"  ✅ 已完成比賽: {completed_matches}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整性檢查失敗: {e}")
        return False

def main():
    """主函數"""
    print("🎯 完整資料遷移檢查報告")
    print("=" * 100)
    
    # 1. 比較所有資料
    compare_all_data()
    
    # 2. 檢查資料完整性
    check_data_integrity()
    
    print(f"\n🎉 檢查完成！")

if __name__ == "__main__":
    main()
