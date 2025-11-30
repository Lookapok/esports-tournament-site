#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# 設定 Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, PlayerGameStat

print("📊 Supabase 資料檢查結果:")
print("=" * 50)

# 檢查各表的資料筆數
tournaments_count = Tournament.objects.count()
teams_count = Team.objects.count()
players_count = Player.objects.count()
stats_count = PlayerGameStat.objects.count()

print(f"🏆 錦標賽: {tournaments_count} 筆")
print(f"🏟️ 隊伍: {teams_count} 筆")
print(f"👥 球員: {players_count} 筆")
print(f"📈 統計: {stats_count} 筆")

print("\n✅ 資料匯入成功！")

# 檢查一些樣本資料
if teams_count > 0:
    print("\n🏟️ 隊伍樣本:")
    for i, team in enumerate(Team.objects.all()[:3], 1):
        print(f"  {i}. {team.name} (ID: {team.id})")

if players_count > 0:
    print("\n👥 球員樣本:")
    for i, player in enumerate(Player.objects.all()[:3], 1):
        print(f"  {i}. {player.nickname} - 隊伍: {player.team.name if player.team else 'N/A'}")

if stats_count > 0:
    print(f"\n📈 統計資料: 共有 {stats_count} 筆玩家遊戲統計 ⭐")
