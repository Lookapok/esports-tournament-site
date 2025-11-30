#!/usr/bin/env python3
"""
檢查數據庫中的統計數據
"""
import os
import django

# 設置Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Player, Team, Tournament, PlayerGameStat, Match, Game

def check_stats_data():
    """檢查統計相關的數據"""
    print("🔍 檢查數據庫統計數據...")
    print("=" * 50)
    
    # 基礎數據
    print(f"📊 選手總數: {Player.objects.count()}")
    print(f"📊 隊伍總數: {Team.objects.count()}")
    print(f"📊 賽事總數: {Tournament.objects.count()}")
    print(f"📊 比賽總數: {Match.objects.count()}")
    print(f"📊 遊戲場次總數: {Game.objects.count()}")
    
    # 重要：檢查PlayerGameStat
    stats_count = PlayerGameStat.objects.count()
    print(f"📊 選手遊戲統計總數: {stats_count}")
    
    if stats_count == 0:
        print("❌ 沒有PlayerGameStat數據 - 這就是為什麼統計頁面是空的！")
        print("\n🔍 檢查是否有遊戲數據：")
        
        games = Game.objects.all()[:5]
        if games.exists():
            print("✅ 有遊戲數據，但沒有統計數據")
            for game in games:
                print(f"   遊戲: {game.id} - {game.match}")
        else:
            print("❌ 也沒有遊戲數據")
            
        print("\n💡 需要生成PlayerGameStat數據才能顯示統計")
    else:
        print("✅ 有PlayerGameStat數據")
        # 顯示一些樣本
        sample_stats = PlayerGameStat.objects.select_related('player', 'team')[:5]
        print("\n前5筆統計數據:")
        for stat in sample_stats:
            print(f"   {stat.player.name} ({stat.team.name}) - 擊殺:{stat.kills} 死亡:{stat.deaths} ACS:{stat.acs}")

if __name__ == "__main__":
    check_stats_data()
