from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Team, Group


class Command(BaseCommand):
    help = '檢查和修復賽事資料的一致性問題'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自動修復發現的問題',
        )
        parser.add_argument(
            '--tournament-id',
            type=int,
            help='指定要檢查的賽事 ID',
        )

    def handle(self, *args, **options):
        if options['tournament_id']:
            tournaments = Tournament.objects.filter(id=options['tournament_id'])
        else:
            tournaments = Tournament.objects.all()

        total_issues = 0
        
        for tournament in tournaments:
            self.stdout.write(f"\n檢查賽事: {tournament.name}")
            issues_found = []
            
            # 檢查是否有隊伍在多個分組中
            teams_in_groups = {}
            for group in tournament.groups.all():
                for team in group.teams.all():
                    if team.id not in teams_in_groups:
                        teams_in_groups[team.id] = []
                    teams_in_groups[team.id].append(group)
            
            # 找出在多個分組的隊伍
            duplicate_teams = {team_id: groups for team_id, groups in teams_in_groups.items() if len(groups) > 1}
            
            if duplicate_teams:
                for team_id, groups in duplicate_teams.items():
                    team = Team.objects.get(id=team_id)
                    group_names = [g.name for g in groups]
                    issue = f"  ❌ 隊伍 '{team.name}' 同時在分組: {', '.join(group_names)}"
                    issues_found.append(issue)
                    self.stdout.write(self.style.WARNING(issue))
                    
                    if options['fix']:
                        # 自動修復：每個隊伍只保留在第一個分組
                        for group in groups[1:]:
                            group.teams.remove(team)
                        self.stdout.write(
                            self.style.SUCCESS(f"    ✅ 已修復：{team.name} 現在只在分組 '{groups[0].name}' 中")
                        )
                
                total_issues += len(duplicate_teams)
            
            # 檢查空分組
            empty_groups = tournament.groups.filter(teams__isnull=True)
            if empty_groups.exists():
                for group in empty_groups:
                    issue = f"  ⚠️  空分組: '{group.name}' 沒有任何隊伍"
                    issues_found.append(issue)
                    self.stdout.write(self.style.WARNING(issue))
                    
                    if options['fix']:
                        group.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f"    ✅ 已刪除空分組: '{group.name}'")
                        )
                
                total_issues += empty_groups.count()
            
            # 檢查沒有分組的隊伍
            teams_without_groups = tournament.participants.filter(tournament_groups__isnull=True)
            if teams_without_groups.exists():
                for team in teams_without_groups:
                    issue = f"  ⚠️  隊伍 '{team.name}' 沒有分組"
                    issues_found.append(issue)
                    self.stdout.write(self.style.WARNING(issue))
            
            if not issues_found:
                self.stdout.write(self.style.SUCCESS(f"  ✅ 賽事資料正常"))
        
        if total_issues > 0:
            if options['fix']:
                self.stdout.write(
                    self.style.SUCCESS(f"\n總共修復了 {total_issues} 個問題")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"\n發現 {total_issues} 個問題，使用 --fix 參數自動修復")
                )
        else:
            self.stdout.write(self.style.SUCCESS("\n所有賽事資料都正常！"))
