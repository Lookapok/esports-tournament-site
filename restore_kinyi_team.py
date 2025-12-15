#!/usr/bin/env python
"""
勤益科技大學隊伍資料恢復腳本
"""

import os
import sys
import django

# 設置 Django 環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Team, Tournament, Standing, Group

def restore_kinyi_team():
    """恢復勤益科技大學隊伍資料"""
    
    print("🔄 開始恢復勤益科技大學隊伍資料...")
    
    # 檢查隊伍是否已存在
    existing_team = Team.objects.filter(name="勤益科技大學-LWX").first()
    if existing_team:
        print(f"✅ 隊伍已存在: {existing_team.name} (ID: {existing_team.id})")
        return existing_team
    
    # 創建隊伍
    try:
        team = Team.objects.create(
            name="勤益科技大學-LWX",
            logo=""
        )
        print(f"✅ 成功創建隊伍: {team.name} (ID: {team.id})")
        
        # 檢查是否需要加入賽事
        tournament = Tournament.objects.get(id=9)  # WTACS S1
        if team not in tournament.participants.all():
            tournament.participants.add(team)
            print(f"✅ 已將隊伍加入賽事: {tournament.name}")
        
        # 檢查是否需要加入B組
        try:
            b_group = Group.objects.get(name="B組", tournament=tournament)
            if team not in b_group.teams.all():
                b_group.teams.add(team)
                print(f"✅ 已將隊伍加入B組")
                
                # 創建積分榜記錄
                standing, created = Standing.objects.get_or_create(
                    tournament=tournament,
                    team=team,
                    group=b_group,
                    defaults={
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'points': 0
                    }
                )
                if created:
                    print(f"✅ 已創建積分榜記錄")
                else:
                    print(f"✅ 積分榜記錄已存在")
                    
        except Group.DoesNotExist:
            print("⚠️  B組不存在，請手動添加到正確的組別")
        
        return team
        
    except Exception as e:
        print(f"❌ 創建隊伍失敗: {e}")
        return None

def main():
    restore_kinyi_team()
    print("\n🎉 恢復完成！")

if __name__ == "__main__":
    main()
