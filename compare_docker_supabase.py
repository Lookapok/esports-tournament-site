"""
比較 Docker 資料 (production_data.json) 和 Supabase 雲端資料
"""
import json
import os
import sys
from django.core.management.base import BaseCommand
import django
from django.conf import settings

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing

def load_docker_data():
    """載入 Docker 原始資料"""
    with open('production_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_supabase_data():
    """取得 Supabase 雲端資料"""
    # 確保使用 Supabase 資料庫
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ 沒有設定 DATABASE_URL，無法連接 Supabase")
        return None
    
    data = {
        'tournaments': list(Tournament.objects.values()),
        'teams': list(Team.objects.values()),
        'players': list(Player.objects.values()),
        'matches': list(Match.objects.values()),
        'games': list(Game.objects.values()),
        'groups': list(Group.objects.values()),
        'standings': list(Standing.objects.values()),
    }
    return data

def compare_data(docker_data, supabase_data):
    """比較兩個資料集"""
    print("=" * 60)
    print("📊 Docker vs Supabase 資料比較")
    print("=" * 60)
    
    comparisons = [
        ('tournaments', '錦標賽'),
        ('teams', '隊伍'),
        ('players', '球員'),
        ('matches', '比賽'),
        ('games', '遊戲'),
        ('groups', '分組'),
        ('standings', '排名'),
    ]
    
    for key, name in comparisons:
        docker_count = len(docker_data.get(key, []))
        supabase_count = len(supabase_data.get(key, []))
        
        status = "✅" if docker_count == supabase_count else "❌"
        print(f"{status} {name}: Docker={docker_count}, Supabase={supabase_count}")
        
        if docker_count != supabase_count:
            print(f"   ⚠️  差異: {supabase_count - docker_count}")
    
    print("\n" + "=" * 60)
    
    # 詳細比較
    print("\n🔍 詳細資料比較:")
    
    # 比較錦標賽
    print(f"\n📋 錦標賽詳細:")
    if docker_data.get('tournaments') and supabase_data.get('tournaments'):
        docker_tournament = docker_data['tournaments'][0]
        supabase_tournament = supabase_data['tournaments'][0] if supabase_data['tournaments'] else None
        
        if supabase_tournament:
            print(f"  Docker Tournament ID: {docker_tournament.get('id')}, Name: {docker_tournament.get('name')}")
            print(f"  Supabase Tournament ID: {supabase_tournament.get('id')}, Name: {supabase_tournament.get('name')}")
        else:
            print("  ❌ Supabase 沒有錦標賽資料")
    
    # 比較隊伍
    print(f"\n🏆 隊伍詳細:")
    if docker_data.get('teams') and supabase_data.get('teams'):
        docker_team_names = [team['name'] for team in docker_data['teams'][:5]]
        supabase_team_names = [team['name'] for team in supabase_data['teams'][:5]] if supabase_data['teams'] else []
        
        print(f"  Docker 前5隊: {docker_team_names}")
        print(f"  Supabase 前5隊: {supabase_team_names}")
        
        # 檢查是否有遺失的隊伍
        docker_all_names = {team['name'] for team in docker_data['teams']}
        supabase_all_names = {team['name'] for team in supabase_data['teams']} if supabase_data['teams'] else set()
        
        missing_in_supabase = docker_all_names - supabase_all_names
        extra_in_supabase = supabase_all_names - docker_all_names
        
        if missing_in_supabase:
            print(f"  ❌ Supabase 缺少的隊伍: {list(missing_in_supabase)[:3]}...")
        if extra_in_supabase:
            print(f"  ⚠️  Supabase 多出的隊伍: {list(extra_in_supabase)[:3]}...")
    
    # 比較分組
    print(f"\n🎯 分組詳細:")
    if docker_data.get('groups') and supabase_data.get('groups'):
        docker_groups = [group['name'] for group in docker_data['groups']]
        supabase_groups = [group['name'] for group in supabase_data['groups']] if supabase_data['groups'] else []
        
        print(f"  Docker 分組: {docker_groups}")
        print(f"  Supabase 分組: {supabase_groups}")

def main():
    print("🔄 開始比較 Docker 和 Supabase 資料...")
    
    # 載入 Docker 資料
    try:
        docker_data = load_docker_data()
        print("✅ 成功載入 Docker 資料")
    except Exception as e:
        print(f"❌ 載入 Docker 資料失敗: {e}")
        return
    
    # 檢查是否有 Supabase 連線
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("\n❌ 無法比較 Supabase 資料 - 沒有設定 DATABASE_URL 環境變數")
        print("📝 要設定環境變數，請執行:")
        print("   $env:DATABASE_URL = 'your_supabase_url'")
        return
    
    # 取得 Supabase 資料
    try:
        supabase_data = get_supabase_data()
        print("✅ 成功連接 Supabase 並取得資料")
    except Exception as e:
        print(f"❌ 取得 Supabase 資料失敗: {e}")
        return
    
    # 比較資料
    compare_data(docker_data, supabase_data)

if __name__ == '__main__':
    main()
