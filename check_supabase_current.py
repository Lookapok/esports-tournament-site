#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查目前 Supabase 中的資料狀況
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat

def check_supabase_data():
    print("🌐 檢查 Supabase 目前資料狀況...")
    print("=" * 50)
    
    # 檢查各個模型的資料數量
    models_info = [
        ('錦標賽', Tournament),
        ('隊伍', Team),
        ('球員', Player),
        ('比賽', Match),
        ('遊戲', Game),
        ('分組', Group),
        ('排名', Standing),
        ('統計資料', PlayerGameStat),
    ]
    
    for name, model in models_info:
        count = model.objects.count()
        print(f"{name:8}: {count:4} 筆")
    
    print("\n" + "=" * 50)
    
    # 如果有資料，顯示一些樣本
    if Tournament.objects.exists():
        print("\n🏆 錦標賽樣本：")
        for t in Tournament.objects.all()[:3]:
            print(f"  - ID:{t.id} | {t.name} | {t.game} | 狀態:{t.status}")
    
    if Team.objects.exists():
        print("\n👥 隊伍樣本：")
        for team in Team.objects.all()[:5]:
            print(f"  - ID:{team.id} | {team.name}")
    
    if Player.objects.exists():
        print("\n🎮 球員樣本：")
        for player in Player.objects.all()[:5]:
            team_name = player.team.name if player.team else "無隊伍"
            print(f"  - ID:{player.id} | {player.nickname} | 隊伍:{team_name}")
    
    if PlayerGameStat.objects.exists():
        print("\n📈 統計資料樣本：")
        for stat in PlayerGameStat.objects.all()[:5]:
            player_name = stat.player.nickname if stat.player else "未知球員"
            print(f"  - 球員:{player_name} | K:{stat.kills} D:{stat.deaths} A:{stat.assists} | ACS:{stat.acs}")
    else:
        print("\n❌ Supabase 中沒有任何統計資料！")
    
    # 檢查資料的新舊程度
    print("\n🕒 資料時間檢查：")
    if PlayerGameStat.objects.exists():
        latest_stat = PlayerGameStat.objects.order_by('-id').first()
        print(f"最新統計記錄 ID: {latest_stat.id}")
    
    if Player.objects.exists():
        latest_player = Player.objects.order_by('-id').first()
        print(f"最新球員記錄 ID: {latest_player.id}")
    
    print("\n💭 建議：")
    total_stats = PlayerGameStat.objects.count()
    total_players = Player.objects.count()
    
    if total_stats == 0 and total_players == 0:
        print("✅ Supabase 是空的，可以直接匯入 Docker 資料")
    elif total_stats == 0 and total_players > 0:
        print("⚠️ 有球員但沒統計資料，可能是假資料或不完整")
    elif total_stats > 0 and total_players > 0:
        print(f"📊 有完整資料 ({total_players}球員, {total_stats}統計)")
        print("   需要比對 Docker 和 Supabase 的資料差異")
    
if __name__ == "__main__":
    check_supabase_data()
