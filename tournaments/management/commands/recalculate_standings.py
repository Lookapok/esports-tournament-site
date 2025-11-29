# tournaments/management/commands/recalculate_standings.py

from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Match, Standing, Group

class Command(BaseCommand):
    help = '重新計算指定賽事的積分榜'

    def add_arguments(self, parser):
        parser.add_argument('tournament_id', type=int, help='賽事ID')

    def handle(self, *args, **options):
        tournament_id = options['tournament_id']
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            self.stdout.write(f'開始重新計算賽事: {tournament.name}')
            
            # 檢查是否為分組賽制
            if tournament.format == 'round_robin':
                self.recalculate_group_standings(tournament)
            else:
                self.recalculate_tournament_standings(tournament)
                
        except Tournament.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'找不到ID為{tournament_id}的賽事')
            )

    def recalculate_group_standings(self, tournament):
        """重新計算分組賽積分榜"""
        self.stdout.write('處理分組賽積分計算...')
        
        # 獲取所有分組
        groups = tournament.groups.all()
        
        for group in groups:
            self.stdout.write(f'  處理 {group.name}...')
            
            # 確保每個分組內的隊伍都有Standing記錄
            for team in group.teams.all():
                standing, created = Standing.objects.get_or_create(
                    tournament=tournament, 
                    team=team, 
                    group=group,
                    defaults={
                        'wins': 0,
                        'losses': 0, 
                        'draws': 0,
                        'points': 0
                    }
                )
                if created:
                    self.stdout.write(f'    創建 {team.name} 的積分記錄')
                else:
                    # 重置積分
                    standing.wins = 0
                    standing.losses = 0
                    standing.draws = 0
                    standing.points = 0
                    standing.save()
                    self.stdout.write(f'    重置 {team.name} 的積分')
            
            # 計算分組內已完成的比賽
            group_teams = list(group.teams.all())
            completed_matches = Match.objects.filter(
                tournament=tournament,
                status='completed',
                team1__in=group_teams,
                team2__in=group_teams
            )
            
            self.stdout.write(f'    找到 {completed_matches.count()} 場已完成的比賽')
            
            for match in completed_matches:
                self.stdout.write(f'      處理比賽: {match.team1.name} vs {match.team2.name} ({match.team1_score}-{match.team2_score})')
                
                if match.winner and match.team1 and match.team2:
                    # 更新勝者積分
                    try:
                        winner_standing = Standing.objects.get(
                            tournament=tournament, 
                            team=match.winner,
                            group=group
                        )
                        winner_standing.wins += 1
                        winner_standing.points += 3  # 勝者得3分
                        winner_standing.save()
                        
                        # 更新敗者積分
                        loser_team = match.team1 if match.team2 == match.winner else match.team2
                        loser_standing = Standing.objects.get(
                            tournament=tournament, 
                            team=loser_team,
                            group=group
                        )
                        loser_standing.losses += 1
                        loser_standing.save()
                        
                        self.stdout.write(f'        勝者: {match.winner.name} (+3分, 總計{winner_standing.points}分)')
                        self.stdout.write(f'        敗者: {loser_team.name} (+1敗, 總計{loser_standing.losses}敗)')
                    except Standing.DoesNotExist:
                        self.stdout.write(f'        錯誤: 找不到積分記錄 - 勝者: {match.winner.name}')
                elif match.team1_score == match.team2_score:
                    # 平局處理
                    for team in [match.team1, match.team2]:
                        standing = Standing.objects.get(
                            tournament=tournament, 
                            team=team,
                            group=group
                        )
                        standing.draws += 1
                        standing.points += 1  # 平局得1分
                        standing.save()
                    self.stdout.write(f'        平局，雙方各得1分')
        
        self.stdout.write(self.style.SUCCESS(f'積分重新計算完成！'))

    def recalculate_tournament_standings(self, tournament):
        """重新計算一般賽事積分榜"""
        self.stdout.write('處理一般賽事積分計算...')
        
        # 重置所有積分
        Standing.objects.filter(tournament=tournament).update(
            wins=0, losses=0, draws=0, points=0
        )
        
        # 重新計算
        completed_matches = Match.objects.filter(
            tournament=tournament, 
            status='completed'
        )
        
        for match in completed_matches:
            if match.winner and match.team1 and match.team2:
                winner_standing, _ = Standing.objects.get_or_create(
                    tournament=tournament, 
                    team=match.winner
                )
                winner_standing.wins += 1
                winner_standing.points += 3
                winner_standing.save()
                
                loser_team = match.team1 if match.team2 == match.winner else match.team2
                loser_standing, _ = Standing.objects.get_or_create(
                    tournament=tournament, 
                    team=loser_team
                )
                loser_standing.losses += 1
                loser_standing.save()
        
        self.stdout.write(self.style.SUCCESS(f'積分重新計算完成！'))
