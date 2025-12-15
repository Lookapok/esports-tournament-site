# 測試對手顯示功能
# 在Django shell中執行：python manage.py shell < test_opponent_display.py

from tournaments.models import PlayerGameStat, Match, Team
from tournaments.tables import get_opponent_info

print("=== 測試對手顯示功能 ===")

# 獲取一些測試數據
stats = PlayerGameStat.objects.select_related(
    'game__match__team1', 
    'game__match__team2', 
    'game__match__tournament',
    'player',
    'team'
).all()[:10]

print(f"\n找到 {stats.count()} 筆統計記錄進行測試")

for i, stat in enumerate(stats, 1):
    try:
        match_info = get_opponent_info(stat)
        print(f"{i}. {stat.player.nickname} ({stat.team.name})")
        print(f"   顯示: {match_info}")
        
        # 顯示實際對戰隊伍
        match = stat.game.match
        actual_teams = f"{match.team1.name if match.team1 else 'TBD'} vs {match.team2.name if match.team2 else 'TBD'}"
        print(f"   實際: {actual_teams}")
        print()
        
    except Exception as e:
        print(f"❌ 記錄 {i} 發生錯誤: {e}")

print("\n=== 測試完成 ===")

# 額外測試：檢查勤益科技大學的數據
print("\n=== 檢查勤益科技大學數據 ===")
kinyi_stats = PlayerGameStat.objects.filter(
    team__name__icontains="勤益"
).select_related(
    'game__match__team1', 
    'game__match__team2', 
    'game__match__tournament',
    'player',
    'team'
)

if kinyi_stats.exists():
    print(f"找到 {kinyi_stats.count()} 筆勤益科技大學的記錄")
    for stat in kinyi_stats[:5]:  # 只顯示前5筆
        match_info = get_opponent_info(stat)
        print(f"- {stat.player.nickname}: {match_info}")
else:
    print("❌ 沒有找到勤益科技大學的數據記錄")
    print("   可能是因為選手資料還沒有恢復")

print("\n✅ 對手顯示功能測試完成")
