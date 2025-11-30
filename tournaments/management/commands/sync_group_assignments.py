"""
同步 Standing 的 group 設定到 Group 的 teams ManyToManyField
"""
from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Group, Standing


class Command(BaseCommand):
    help = 'Sync group assignments between Standing and Group models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tournament-id',
            type=int,
            help='Tournament ID to sync (default: all tournaments)',
        )

    def handle(self, *args, **options):
        tournament_id = options.get('tournament_id')
        
        if tournament_id:
            tournaments = Tournament.objects.filter(id=tournament_id)
        else:
            tournaments = Tournament.objects.all()
            
        for tournament in tournaments:
            self.stdout.write(f'Processing tournament: {tournament.name}')
            
            # 清除所有 Group.teams 關係
            for group in tournament.groups.all():
                group.teams.clear()
                
            # 根據 Standing.group 重新建立 Group.teams 關係
            standings_with_group = Standing.objects.filter(
                tournament=tournament,
                group__isnull=False
            )
            
            synced_count = 0
            for standing in standings_with_group:
                standing.group.teams.add(standing.team)
                synced_count += 1
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Synced {synced_count} team-group relationships for {tournament.name}'
                )
            )
            
        self.stdout.write(self.style.SUCCESS('Sync completed!'))
