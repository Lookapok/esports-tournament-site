#!/usr/bin/env python
import os
import sys
import django

# 設置Django環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

# 導入模型
from tournaments.models import Tournament, Player, Match, Standing

def main():
    print("=== 資料庫內容檢查 ===")
    
    # 檢查各模型的資料數量
    tournament_count = Tournament.objects.count()
    player_count = Player.objects.count()
    match_count = Match.objects.count()
    standing_count = Standing.objects.count()
    
    print(f"比賽 (Tournaments): {tournament_count}")
    print(f"選手 (Players): {player_count}")
    print(f"對戰 (Matches): {match_count}")
    print(f"排名 (Standings): {standing_count}")
    
    if tournament_count > 0:
        print("\n=== 比賽列表 ===")
        for tournament in Tournament.objects.all()[:5]:
            print(f"- {tournament.id}: {tournament.name} ({tournament.tournament_type})")
    
    if player_count > 0:
        print("\n=== 選手列表 ===")
        for player in Player.objects.all()[:10]:
            print(f"- {player.id}: {player.name}")
            
    if standing_count > 0:
        print("\n=== 排名資料 ===")
        for standing in Standing.objects.all()[:5]:
            print(f"- {standing.player.name}: {standing.points} 分")

if __name__ == "__main__":
    main()
