from django.core.management.base import BaseCommand
from django.core.management import call_command
from tournaments.models import Tournament, Team, Player

class Command(BaseCommand):
    help = 'Load initial tournament data if database is empty'
    
    def handle(self, *args, **options):
        tournament_count = Tournament.objects.count()
        team_count = Team.objects.count()
        player_count = Player.objects.count()
        
        if tournament_count == 0 and team_count == 0:
            self.stdout.write(self.style.WARNING('資料庫為空，開始載入初始資料...'))
            
            try:
                call_command('loaddata', 'fixtures/all_tournament_data.json')
                
                # 驗證載入結果
                new_tournament_count = Tournament.objects.count()
                new_team_count = Team.objects.count() 
                new_player_count = Player.objects.count()
                
                self.stdout.write(self.style.SUCCESS(
                    f'資料載入完成！\n'
                    f'錦標賽: {new_tournament_count}\n'
                    f'隊伍: {new_team_count}\n'
                    f'選手: {new_player_count}'
                ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'載入失敗: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'資料已存在，跳過載入。目前有 {tournament_count} 個錦標賽，{team_count} 支隊伍，{player_count} 名選手。'
            ))
