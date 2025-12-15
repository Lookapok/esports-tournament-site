#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速檢查 Docker vs Supabase 資料內容是否真的一致
專注檢查具體的球員資料和統計數據
"""

import json
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Player, PlayerGameStat, Team

def check_specific_data():
    print("🔍 檢查具體資料內容...")
    
    # 1. 載入 Docker 原始資料
    print("\n📦 載入 Docker 原始資料...")
    try:
        with open('production_data.json', 'r', encoding='utf-8') as f:
            docker_data = json.load(f)
    except FileNotFoundError:
        print("❌ production_data.json 找不到！")
        return
    
    # 2. 檢查 Docker 資料中的具體球員
    docker_players = docker_data.get('players', [])
    docker_stats = docker_data.get('player_stats', [])
    
    print(f"📊 Docker 資料:")
    print(f"  球員數量: {len(docker_players)}")
    print(f"  統計數量: {len(docker_stats)}")
    
    # 顯示前幾個球員的詳細資料
    print(f"\n👥 Docker 前 5 個球員:")
    for i, player in enumerate(docker_players[:5]):
        print(f"  {i+1}. {player.get('username', 'N/A')}#{player.get('tag', 'N/A')} (隊伍ID: {player.get('team_id', 'N/A')})")
        print(f"     ID: {player.get('id')} | 真實姓名: {player.get('real_name', 'N/A')}")
    
    # 檢查統計資料樣本
    print(f"\n📈 Docker 前 5 個統計記錄:")
    for i, stat in enumerate(docker_stats[:5]):
        print(f"  {i+1}. 球員ID:{stat.get('player_id')} | 擊殺:{stat.get('kills', 0)} | 死亡:{stat.get('deaths', 0)} | 助攻:{stat.get('assists', 0)}")
    
    # 3. 檢查 Supabase 目前的資料
    print(f"\n🌐 Supabase 目前資料:")
    supabase_players = Player.objects.all()[:5]
    supabase_stats = PlayerGameStat.objects.all()[:5]
    
    print(f"  球員數量: {Player.objects.count()}")
    print(f"  統計數量: {PlayerGameStat.objects.count()}")
    
    print(f"\n👥 Supabase 前 5 個球員:")
    for i, player in enumerate(supabase_players):
        print(f"  {i+1}. {player.username}#{player.tag} (隊伍ID: {player.team_id if player.team else 'N/A'})")
        print(f"     ID: {player.id} | 真實姓名: {player.real_name}")
    
    print(f"\n📈 Supabase 前 5 個統計記錄:")
    for i, stat in enumerate(supabase_stats):
        print(f"  {i+1}. 球員ID:{stat.player_id} | 擊殺:{stat.kills} | 死亡:{stat.deaths} | 助攻:{stat.assists}")
    
    # 4. 比對特定球員
    print(f"\n🔍 詳細比對檢查:")
    
    if docker_players and supabase_players:
        # 檢查第一個球員
        docker_player_1 = docker_players[0]
        supabase_player_1 = supabase_players[0]
        
        print(f"📋 第一個球員比對:")
        print(f"  Docker:   {docker_player_1.get('username', 'N/A')}#{docker_player_1.get('tag', 'N/A')}")
        print(f"  Supabase: {supabase_player_1.username}#{supabase_player_1.tag}")
        
        if docker_player_1.get('username') == supabase_player_1.username and docker_player_1.get('tag') == supabase_player_1.tag:
            print("  ✅ 第一個球員資料一致")
        else:
            print("  ⚠️ 第一個球員資料不一致 - 可能有假資料問題！")
    
    # 5. 檢查統計資料是否為空或假資料
    if PlayerGameStat.objects.count() == 0:
        print("\n❌ 嚴重問題：Supabase 中沒有任何統計資料！")
        print("   這確認了資料可能沒有正確從 Docker 同步")
    else:
        # 檢查統計資料是否都是 0 或假資料
        zero_stats = PlayerGameStat.objects.filter(kills=0, deaths=0, assists=0).count()
        total_stats = PlayerGameStat.objects.count()
        print(f"\n📊 統計資料分析:")
        print(f"  全部為 0 的統計: {zero_stats}/{total_stats}")
        if zero_stats > total_stats * 0.8:  # 如果 80% 以上都是 0
            print("  ⚠️ 大部分統計資料都是 0，可能是假資料！")

if __name__ == "__main__":
    check_specific_data()
