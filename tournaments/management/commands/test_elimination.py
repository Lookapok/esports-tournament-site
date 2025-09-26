from django.core.management.base import BaseCommand
from django.db import models
from tournaments.models import Tournament, Team
from tournaments.logic import generate_single_elimination_matches, generate_double_elimination_matches


class Command(BaseCommand):
    help = '測試淘汰賽演算法'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tournament-id',
            type=int,
            required=True,
            help='要測試的賽事 ID',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['single', 'double'],
            required=True,
            help='淘汰賽格式：single 或 double',
        )

    def handle(self, *args, **options):
        try:
            tournament = Tournament.objects.get(id=options['tournament_id'])
        except Tournament.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"找不到 ID 為 {options['tournament_id']} 的賽事"))
            return

        self.stdout.write(f"測試賽事: {tournament.name}")
        self.stdout.write(f"參賽隊伍數量: {tournament.participants.count()}")

        if options['format'] == 'single':
            self.stdout.write("正在生成單淘汰賽程...")
            count = generate_single_elimination_matches(tournament)
            self.stdout.write(
                self.style.SUCCESS(f"成功生成 {count} 場單淘汰比賽")
            )
        elif options['format'] == 'double':
            self.stdout.write("正在生成雙淘汰賽程...")
            count = generate_double_elimination_matches(tournament)
            self.stdout.write(
                self.style.SUCCESS(f"成功生成 {count} 場雙淘汰比賽")
            )

        # 顯示生成的比賽詳情
        matches = tournament.matches.all().order_by('round_number', 'is_lower_bracket', 'id')
        
        current_round = None
        current_bracket = None
        
        for match in matches:
            round_changed = current_round != match.round_number
            bracket_changed = current_bracket != match.is_lower_bracket
            
            if round_changed or bracket_changed:
                bracket_name = "敗部" if match.is_lower_bracket else "勝部"
                if options['format'] == 'single':
                    if match.round_number == matches.aggregate(max_round=models.Max('round_number'))['max_round']:
                        bracket_name = "決賽"
                    else:
                        bracket_name = f"第 {match.round_number} 輪"
                else:
                    bracket_name += f" 第 {match.round_number} 輪"
                
                self.stdout.write(f"\n=== {bracket_name} ===")
                current_round = match.round_number
                current_bracket = match.is_lower_bracket

            team1_name = match.team1.name if match.team1 else "待定"
            team2_name = match.team2.name if match.team2 else "待定"
            
            self.stdout.write(f"  {team1_name} vs {team2_name}")
