# 恢復勤益科技大學隊伍的代碼 - 增強版
# 在Django shell中執行：python manage.py shell < restore_team_code_enhanced.py

from tournaments.models import Team, Player, Tournament, Group, Standing
from django.db import transaction
from django.db import models

print("=== 開始恢復勤益科技大學隊伍 (增強版) ===")

# 預防機制：檢查數據重複
def check_for_duplicates():
    """檢查潛在的重複數據"""
    print("\n🔍 執行重複數據檢查...")
    
    # 檢查同名隊伍
    kinyi_teams = Team.objects.filter(name__icontains="勤益")
    if kinyi_teams.count() > 1:
        print(f"⚠️  發現 {kinyi_teams.count()} 個相似隊伍:")
        for team in kinyi_teams:
            print(f"   - {team.name} (ID: {team.id})")
        return True
    
    return False

# 執行預檢查
has_duplicates = check_for_duplicates()

# 創建勤益科技大學-LWX隊伍 (使用事務保護)
try:
    with transaction.atomic():  # 確保原子性操作
        # 檢查是否已存在
        existing_team = Team.objects.filter(name__icontains="勤益科技大學-LWX").first()
        if existing_team:
            print(f"✅ 隊伍已存在: {existing_team.name} (ID: {existing_team.id})")
            team = existing_team
        else:
            # 檢查是否有相似名稱的隊伍
            similar_teams = Team.objects.filter(name__icontains="勤益科技大學")
            if similar_teams.exists():
                print("⚠️  發現相似隊伍，請確認是否需要合併:")
                for similar_team in similar_teams:
                    print(f"   - {similar_team.name} (ID: {similar_team.id})")
            
            # 創建新隊伍
            team = Team.objects.create(name="勤益科技大學-LWX")
            print(f"✅ 成功創建隊伍: {team.name} (ID: {team.id})")
        
        # 檢查賽事並加入參賽
        try:
            tournament = Tournament.objects.get(id=9)
            print(f"✅ 找到賽事: {tournament.name}")
        except Tournament.DoesNotExist:
            raise Exception("❌ 賽事 ID 9 不存在，請檢查賽事ID")
        
        if not tournament.participants.filter(id=team.id).exists():
            tournament.participants.add(team)
            print(f"✅ 已將隊伍加入賽事: {tournament.name}")
        else:
            print(f"✅ 隊伍已在賽事中: {tournament.name}")
        
        # 檢查分組並加入
        try:
            b_group = Group.objects.get(name="B組", tournament=tournament)
            print(f"✅ 找到分組: {b_group.name}")
            
            # 檢查是否已在其他分組中
            other_groups = Group.objects.filter(
                tournament=tournament, 
                teams=team
            ).exclude(id=b_group.id)
            
            if other_groups.exists():
                print("⚠️  隊伍在其他分組中，正在移除:")
                for group in other_groups:
                    group.teams.remove(team)
                    print(f"   - 已從 {group.name} 移除")
            
            if not b_group.teams.filter(id=team.id).exists():
                b_group.teams.add(team)
                print(f"✅ 已將隊伍加入分組: {b_group.name}")
            else:
                print(f"✅ 隊伍已在分組中: {b_group.name}")
            
            # 檢查重複積分榜記錄
            existing_standings = Standing.objects.filter(
                tournament=tournament,
                team=team
            )
            
            if existing_standings.count() > 1:
                print("⚠️  發現重複積分榜記錄，正在清理...")
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
                print(f"✅ 已更新積分榜記錄 (分組: {standing.group.name if standing.group else '無'})")
                
        except Group.DoesNotExist:
            print("❌ 找不到B組，請先確認分組設置")
            raise Exception("分組 'B組' 不存在")
        
        # 最終驗證
        print("\n📊 恢復結果驗證:")
        players_count = team.players.count()
        print(f"   選手數量: {players_count}")
        
        if players_count == 0:
            print("⚠️  隊伍暫無選手，可能需要額外恢復選手資料")
        
        # 檢查積分計算
        calculated_points = standing.wins * 3 + standing.draws * 1
        if standing.points != calculated_points:
            print(f"⚠️  積分不一致，正在修正: {standing.points} → {calculated_points}")
            standing.points = calculated_points
            standing.save()
        
        print("\n=== 恢復完成 ===")
        print(f"隊伍名稱: {team.name}")
        print(f"隊伍ID: {team.id}")
        print(f"賽事: {tournament.name}")
        print(f"分組: {b_group.name}")
        print(f"積分榜: {standing.wins}勝{standing.losses}敗 ({standing.points}分)")
        print("✅ 所有操作成功完成，數據完整性良好")

except Exception as e:
    print(f"\n❌ 恢復過程中發生錯誤: {e}")
    print("🔄 所有變更已自動回滾，數據庫狀態未改變")
    print("💡 建議先執行數據清理腳本，再重新嘗試恢復")
    
    # 提供額外診斷信息
    print(f"\n🔍 錯誤診斷信息:")
    print(f"   錯誤類型: {type(e).__name__}")
    if "Tournament" in str(e):
        print("   建議：檢查賽事ID是否正確")
    elif "Group" in str(e):
        print("   建議：檢查分組是否存在")
    elif "duplicate" in str(e).lower():
        print("   建議：先執行數據清理腳本")
    
    raise e  # 重新拋出錯誤以便調試
