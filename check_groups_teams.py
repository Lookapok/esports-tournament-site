import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Group, Team, Standing

def check_groups_and_teams():
    print("=== 檢查分組與隊伍關聯 ===")
    
    # 查詢所有賽事
    tournaments = Tournament.objects.all()
    for tournament in tournaments:
        print(f"\n賽事: {tournament.name}")
        print(f"格式: {tournament.format}")
        
        # 查詢該賽事的參賽隊伍
        participants = tournament.participants.all()
        print(f"參賽隊伍數量: {participants.count()}")
        
        # 查詢該賽事的分組
        groups = tournament.groups.all()
        print(f"分組數量: {groups.count()}")
        
        for group in groups:
            print(f"\n  分組: {group.name}")
            
            # 查看分組中的隊伍
            group_teams = group.teams.all()
            print(f"  分組隊伍數量: {group_teams.count()}")
            
            for team in group_teams:
                print(f"    - {team.name}")
            
            # 查看該分組的積分榜
            standings = group.standings.all()
            print(f"  積分榜記錄數量: {standings.count()}")
            
            for standing in standings:
                print(f"    積分榜: {standing.team.name} - {standing.points}分")
                
        # 查看該賽事的所有積分榜記錄
        all_standings = tournament.standings.all()
        print(f"\n  總積分榜記錄數量: {all_standings.count()}")

if __name__ == "__main__":
    check_groups_and_teams()
