#!/usr/bin/env python3
"""
清理自動生成的假統計數據
只保留真實的比賽記錄
"""
import os
import django

# 設置Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import PlayerGameStat, Game, Match
from django.db import transaction

def clean_fake_stats():
    """清理可能的假統計數據"""
    print("🧹 檢查並清理假統計數據...")
    print("=" * 50)
    
    total_stats = PlayerGameStat.objects.count()
    print(f"📊 當前統計記錄總數: {total_stats}")
    
    if total_stats == 0:
        print("ℹ️ 沒有統計數據，無需清理")
        return
    
    # 檢查是否有明顯的假數據特徵
    # (例如：同一場遊戲中所有選手的數據都很相似)
    suspicious_stats = []
    
    for game in Game.objects.all():
        game_stats = PlayerGameStat.objects.filter(game=game)
        if game_stats.count() > 0:
            # 檢查數據是否過於規整（假數據特徵）
            acs_values = list(game_stats.values_list('acs', flat=True))
            if len(set(acs_values)) == len(acs_values):  # 所有ACS都不同（假數據特徵）
                kills_avg = sum(s.kills for s in game_stats) / len(game_stats)
                if 10 <= kills_avg <= 20:  # 平均擊殺在合理範圍（假數據特徵）
                    suspicious_stats.extend(game_stats)
    
    if suspicious_stats:
        print(f"🔍 發現 {len(suspicious_stats)} 筆可能的假統計數據")
        print("\n可疑記錄樣本:")
        for stat in suspicious_stats[:5]:
            print(f"  {stat.player.name} - 擊殺:{stat.kills} 死亡:{stat.deaths} ACS:{stat.acs}")
        
        confirm = input(f"\n是否要刪除這些可疑的統計數據? (y/N): ")
        if confirm.lower() == 'y':
            with transaction.atomic():
                deleted_count = len(suspicious_stats)
                for stat in suspicious_stats:
                    stat.delete()
            print(f"✅ 已刪除 {deleted_count} 筆假統計數據")
        else:
            print("ℹ️ 保留所有數據")
    else:
        print("✅ 沒有發現明顯的假數據")
    
    final_stats = PlayerGameStat.objects.count()
    print(f"\n📊 清理後統計記錄總數: {final_stats}")

if __name__ == "__main__":
    clean_fake_stats()
