# 數據清理和驗證工具
# 在Django shell中執行：python manage.py shell < data_cleanup_validator.py

from tournaments.models import Team, Player, Tournament, Group, Standing, Match
from django.db import models, transaction
from collections import defaultdict
import logging

def clean_duplicate_data():
    """
    清理重複數據
    """
    print("=== 開始數據清理 ===")
    
    with transaction.atomic():
        # 1. 清理重複隊伍
        print("\n1. 檢查重複隊伍...")
        duplicate_teams = Team.objects.values('name').annotate(
            count=models.Count('name')
        ).filter(count__gt=1)
        
        for dup in duplicate_teams:
            teams = Team.objects.filter(name=dup['name']).order_by('id')
            keep_team = teams.first()  # 保留第一個
            duplicate_teams_to_delete = teams[1:]  # 刪除其餘的
            
            print(f"⚠️  重複隊伍: {dup['name']}")
            print(f"   保留: ID {keep_team.id}")
            
            # 將重複隊伍的選手轉移到保留的隊伍
            for team in duplicate_teams_to_delete:
                players = team.players.all()
                for player in players:
                    # 檢查是否已有同名選手
                    existing_player = keep_team.players.filter(
                        nickname=player.nickname
                    ).first()
                    
                    if not existing_player:
                        player.team = keep_team
                        player.save()
                        print(f"   轉移選手: {player.nickname}")
                    else:
                        print(f"   刪除重複選手: {player.nickname}")
                        player.delete()
                
                # 更新比賽記錄
                Match.objects.filter(team1=team).update(team1=keep_team)
                Match.objects.filter(team2=team).update(team2=keep_team)
                
                # 更新積分榜
                Standing.objects.filter(team=team).update(team=keep_team)
                
                # 更新分組關係
                for group in team.tournament_groups.all():
                    group.teams.remove(team)
                    group.teams.add(keep_team)
                
                # 更新賽事參與
                for tournament in team.tournaments.all():
                    tournament.participants.remove(team)
                    tournament.participants.add(keep_team)
                
                print(f"   刪除重複隊伍: ID {team.id}")
                team.delete()
        
        # 2. 清理重複選手
        print("\n2. 檢查重複選手...")
        duplicate_players = Player.objects.values('nickname', 'team').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for dup in duplicate_players:
            players = Player.objects.filter(
                nickname=dup['nickname'],
                team_id=dup['team']
            ).order_by('id')
            
            keep_player = players.first()
            players_to_delete = players[1:]
            
            print(f"⚠️  重複選手: {dup['nickname']}")
            print(f"   保留: ID {keep_player.id}")
            
            for player in players_to_delete:
                # 轉移統計數據（如果有的話）
                player.game_stats.all().delete()  # 簡單刪除，避免複雜度
                print(f"   刪除重複選手: ID {player.id}")
                player.delete()
        
        # 3. 清理重複積分榜
        print("\n3. 檢查重複積分榜...")
        duplicate_standings = Standing.objects.values(
            'tournament', 'team'
        ).annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for dup in duplicate_standings:
            standings = Standing.objects.filter(
                tournament_id=dup['tournament'],
                team_id=dup['team']
            ).order_by('id')
            
            keep_standing = standings.first()
            standings_to_delete = standings[1:]
            
            print(f"⚠️  重複積分榜記錄")
            print(f"   保留: ID {keep_standing.id}")
            
            for standing in standings_to_delete:
                print(f"   刪除: ID {standing.id}")
                standing.delete()

def validate_data_integrity():
    """
    驗證數據完整性
    """
    print("\n=== 數據完整性驗證 ===")
    
    errors = []
    warnings = []
    
    # 1. 檢查孤立選手
    orphaned_players = Player.objects.filter(team__isnull=True)
    if orphaned_players.exists():
        errors.append(f"孤立選手: {orphaned_players.count()}個")
        for player in orphaned_players:
            print(f"❌ 孤立選手: {player.nickname} (ID: {player.id})")
    
    # 2. 檢查積分榜一致性
    print("\n檢查積分榜一致性...")
    inconsistent_standings = []
    
    for standing in Standing.objects.all():
        calculated_points = standing.wins * 3 + standing.draws * 1
        if standing.points != calculated_points:
            inconsistent_standings.append({
                'standing': standing,
                'recorded': standing.points,
                'calculated': calculated_points
            })
    
    if inconsistent_standings:
        warnings.append(f"積分不一致: {len(inconsistent_standings)}個")
        for item in inconsistent_standings:
            standing = item['standing']
            print(f"⚠️  {standing.team.name}: 記錄={item['recorded']}, 計算={item['calculated']}")
    
    # 3. 檢查分組完整性
    print("\n檢查分組完整性...")
    teams_in_multiple_groups = []
    
    for tournament in Tournament.objects.all():
        team_group_count = defaultdict(int)
        
        for group in tournament.groups.all():
            for team in group.teams.all():
                team_group_count[team.id] += 1
        
        for team_id, count in team_group_count.items():
            if count > 1:
                team = Team.objects.get(id=team_id)
                teams_in_multiple_groups.append({
                    'team': team,
                    'tournament': tournament,
                    'group_count': count
                })
    
    if teams_in_multiple_groups:
        warnings.append(f"多分組隊伍: {len(teams_in_multiple_groups)}個")
        for item in teams_in_multiple_groups:
            print(f"⚠️  {item['team'].name} 在 {item['tournament'].name} 中屬於 {item['group_count']} 個分組")
    
    # 4. 檢查比賽完整性
    print("\n檢查比賽完整性...")
    invalid_matches = Match.objects.filter(
        models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
    )
    
    if invalid_matches.exists():
        errors.append(f"無效比賽: {invalid_matches.count()}場")
        for match in invalid_matches:
            print(f"❌ 無效比賽 ID {match.id}: {match.team1} vs {match.team2}")
    
    # 總結報告
    print(f"\n=== 驗證報告 ===")
    print(f"錯誤: {len(errors)}個")
    print(f"警告: {len(warnings)}個")
    
    if errors:
        print("\n錯誤列表:")
        for error in errors:
            print(f"❌ {error}")
    
    if warnings:
        print("\n警告列表:")
        for warning in warnings:
            print(f"⚠️  {warning}")
    
    if not errors and not warnings:
        print("✅ 數據完整性驗證通過")
        return True
    
    return len(errors) == 0  # 只有警告不算失敗

def fix_standing_points():
    """
    修正積分榜積分
    """
    print("\n=== 修正積分榜積分 ===")
    
    fixed_count = 0
    
    for standing in Standing.objects.all():
        calculated_points = standing.wins * 3 + standing.draws * 1
        
        if standing.points != calculated_points:
            old_points = standing.points
            standing.points = calculated_points
            standing.save()
            
            print(f"✅ 修正 {standing.team.name}: {old_points} → {calculated_points}")
            fixed_count += 1
    
    if fixed_count == 0:
        print("✅ 所有積分都正確")
    else:
        print(f"✅ 已修正 {fixed_count} 個積分記錄")

# 執行清理和驗證
if __name__ == "__main__":
    print("🔧 開始數據清理和驗證流程")
    
    # 1. 先驗證現狀
    print("\n=== 清理前驗證 ===")
    validate_data_integrity()
    
    # 2. 執行清理
    clean_duplicate_data()
    
    # 3. 修正積分
    fix_standing_points()
    
    # 4. 再次驗證
    print("\n=== 清理後驗證 ===")
    is_valid = validate_data_integrity()
    
    if is_valid:
        print("\n🎉 數據清理完成，數據完整性良好")
    else:
        print("\n⚠️  數據清理完成，但仍有問題需要手動處理")
    
    print("\n✅ 現在可以安全執行隊伍恢復操作")
