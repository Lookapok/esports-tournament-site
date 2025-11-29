# 安全恢復勤益科技大學隊伍的代碼 - 包含錯誤預防機制
# 在Django shell中執行：python manage.py shell < safe_restore_team.py

from tournaments.models import Team, Player, Tournament, Group, Standing, Match
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_restore_kinyi_team():
    """
    安全恢復勤益科技大學隊伍，包含完整的錯誤檢查和預防機制
    """
    print("=== 開始安全恢復勤益科技大學隊伍 ===")
    
    # 設定參數
    TEAM_NAME = "勤益科技大學-LWX"
    TOURNAMENT_ID = 9
    GROUP_NAME = "B組"
    
    # 預防措施：使用資料庫事務，確保原子性操作
    try:
        with transaction.atomic():
            # ===== 第1步：檢查和創建隊伍 =====
            print("\n1. 檢查隊伍狀態...")
            
            # 檢查是否有重複或相似名稱的隊伍
            similar_teams = Team.objects.filter(name__icontains="勤益")
            if similar_teams.exists():
                print("⚠️  發現相似的隊伍：")
                for team in similar_teams:
                    player_count = team.players.count()
                    print(f"   - {team.name} (ID: {team.id}, 選手數: {player_count})")
                
                # 檢查是否完全匹配
                exact_match = similar_teams.filter(name=TEAM_NAME).first()
                if exact_match:
                    team = exact_match
                    print(f"✅ 使用現有隊伍: {team.name} (ID: {team.id})")
                else:
                    # 創建新隊伍前先清理重複項
                    duplicate_count = similar_teams.count()
                    if duplicate_count > 0:
                        print(f"⚠️  發現 {duplicate_count} 個相似隊伍，建議手動檢查")
                    
                    team = Team.objects.create(name=TEAM_NAME)
                    print(f"✅ 創建新隊伍: {team.name} (ID: {team.id})")
            else:
                team = Team.objects.create(name=TEAM_NAME)
                print(f"✅ 創建新隊伍: {team.name} (ID: {team.id})")
            
            # ===== 第2步：檢查賽事和參與狀態 =====
            print("\n2. 檢查賽事狀態...")
            
            try:
                tournament = Tournament.objects.get(id=TOURNAMENT_ID)
                print(f"✅ 找到賽事: {tournament.name} (ID: {tournament.id})")
                
                # 檢查參與狀態
                if tournament.participants.filter(id=team.id).exists():
                    print(f"✅ 隊伍已參與賽事")
                else:
                    tournament.participants.add(team)
                    print(f"✅ 已將隊伍加入賽事")
                    
            except Tournament.DoesNotExist:
                raise Exception(f"❌ 賽事 ID {TOURNAMENT_ID} 不存在")
            
            # ===== 第3步：檢查分組狀態 =====
            print("\n3. 檢查分組狀態...")
            
            try:
                b_group = Group.objects.get(name=GROUP_NAME, tournament=tournament)
                print(f"✅ 找到分組: {b_group.name}")
                
                # 檢查是否已在分組中
                if b_group.teams.filter(id=team.id).exists():
                    print(f"✅ 隊伍已在分組中")
                else:
                    # 檢查隊伍是否在其他分組中
                    other_groups = Group.objects.filter(
                        tournament=tournament, 
                        teams=team
                    ).exclude(id=b_group.id)
                    
                    if other_groups.exists():
                        print("⚠️  隊伍在其他分組中，移除舊分組...")
                        for group in other_groups:
                            group.teams.remove(team)
                            print(f"   - 從 {group.name} 移除")
                    
                    b_group.teams.add(team)
                    print(f"✅ 已將隊伍加入 {GROUP_NAME}")
                    
            except Group.DoesNotExist:
                raise Exception(f"❌ 分組 '{GROUP_NAME}' 不存在")
            
            # ===== 第4步：檢查和創建積分榜記錄 =====
            print("\n4. 檢查積分榜狀態...")
            
            # 檢查是否有重複的積分榜記錄
            existing_standings = Standing.objects.filter(
                tournament=tournament,
                team=team
            )
            
            if existing_standings.count() > 1:
                print("⚠️  發現重複積分榜記錄，清理中...")
                # 保留第一個，刪除其餘的
                keep_standing = existing_standings.first()
                existing_standings.exclude(id=keep_standing.id).delete()
                print(f"✅ 已清理重複記錄，保留 ID: {keep_standing.id}")
            
            # 創建或更新積分榜記錄
            standing, created = Standing.objects.update_or_create(
                tournament=tournament,
                team=team,
                defaults={
                    'group': b_group,
                    'wins': 0,
                    'losses': 0, 
                    'draws': 0,
                    'points': 0
                }
            )
            
            if created:
                print(f"✅ 已創建積分榜記錄")
            else:
                print(f"✅ 已更新積分榜記錄")
            
            # ===== 第5步：數據完整性檢查 =====
            print("\n5. 執行完整性檢查...")
            
            # 檢查選手數據
            players = team.players.all()
            print(f"📊 隊伍選手數: {players.count()}")
            
            if players.exists():
                print("   選手列表:")
                for player in players:
                    print(f"   - {player.nickname} (ID: {player.id})")
            else:
                print("⚠️  隊伍暫無選手資料")
            
            # 檢查比賽記錄
            matches = Match.objects.filter(
                tournament=tournament
            ).filter(
                models.Q(team1=team) | models.Q(team2=team)
            )
            print(f"📊 相關比賽數: {matches.count()}")
            
            # 檢查積分一致性
            calculated_points = standing.wins * 3 + standing.draws * 1
            if standing.points != calculated_points:
                print(f"⚠️  積分不一致: 記錄={standing.points}, 計算={calculated_points}")
                standing.points = calculated_points
                standing.save()
                print(f"✅ 已修正積分為: {calculated_points}")
            
            print("\n=== 恢復完成 ===")
            print(f"隊伍名稱: {team.name}")
            print(f"隊伍ID: {team.id}")
            print(f"賽事: {tournament.name}")
            print(f"分組: {b_group.name}")
            print(f"積分榜: {standing.wins}勝{standing.losses}敗 ({standing.points}分)")
            
            return {
                'success': True,
                'team': team,
                'tournament': tournament,
                'group': b_group,
                'standing': standing,
                'players_count': players.count()
            }
            
    except Exception as e:
        print(f"\n❌ 恢復過程中發生錯誤: {e}")
        print("🔄 所有變更已回滾")
        logger.error(f"Team restoration failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

def check_data_consistency():
    """
    檢查數據一致性的輔助函數
    """
    print("\n=== 執行數據一致性檢查 ===")
    
    from django.db import models
    
    issues = []
    
    # 檢查重複隊伍名稱
    duplicate_teams = Team.objects.values('name').annotate(
        count=models.Count('name')
    ).filter(count__gt=1)
    
    if duplicate_teams:
        issues.append("重複隊伍名稱")
        for dup in duplicate_teams:
            print(f"⚠️  重複隊伍: {dup['name']} ({dup['count']}次)")
    
    # 檢查孤立的選手（隊伍被刪除）
    orphaned_players = Player.objects.filter(team__isnull=True)
    if orphaned_players.exists():
        issues.append(f"孤立選手: {orphaned_players.count()}個")
    
    # 檢查重複積分榜記錄
    duplicate_standings = Standing.objects.values(
        'tournament', 'team'
    ).annotate(
        count=models.Count('id')
    ).filter(count__gt=1)
    
    if duplicate_standings:
        issues.append(f"重複積分榜: {len(duplicate_standings)}組")
    
    if issues:
        print("⚠️  發現的問題:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ 數據一致性檢查通過")
        return True

# 執行恢復
if __name__ == "__main__":
    # 先檢查數據一致性
    check_data_consistency()
    
    # 執行安全恢復
    result = safe_restore_kinyi_team()
    
    if result['success']:
        print(f"\n🎉 恢復成功！")
    else:
        print(f"\n💥 恢復失敗: {result['error']}")
