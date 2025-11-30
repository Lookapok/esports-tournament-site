from django.core.management.base import BaseCommand
from tournaments.models import PlayerGameStat, Team, Game
from django.db import transaction

class Command(BaseCommand):
    help = '清理自動生成的假統計數據'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只顯示會被刪除的數據，不實際刪除',
        )
        parser.add_argument(
            '--team',
            type=str,
            help='只檢查特定隊伍的數據',
        )

    def handle(self, *args, **options):
        self.stdout.write("🧹 檢查假統計數據...")
        
        dry_run = options['dry_run']
        target_team = options['team']
        
        total_stats = PlayerGameStat.objects.count()
        self.stdout.write(f"📊 總統計記錄數: {total_stats}")
        
        if total_stats == 0:
            self.stdout.write("ℹ️ 沒有統計數據")
            return
        
        # 顯示各隊數據分布
        self.stdout.write("\n📈 各隊統計數據:")
        teams = Team.objects.all()
        if target_team:
            teams = teams.filter(name__icontains=target_team)
        
        suspicious_stats = []
        
        for team in teams:
            team_stats = PlayerGameStat.objects.filter(team=team)
            stats_count = team_stats.count()
            player_count = team.player_set.count()
            
            self.stdout.write(f"  {team.name}: {stats_count} 筆統計 / {player_count} 位選手")
            
            if stats_count > 0:
                # 檢查平均值
                avg_kills = sum(s.kills for s in team_stats) / stats_count
                avg_deaths = sum(s.deaths for s in team_stats) / stats_count
                avg_acs = sum(float(s.acs) for s in team_stats) / stats_count
                
                self.stdout.write(f"    平均: K{avg_kills:.1f} D{avg_deaths:.1f} ACS{avg_acs:.1f}")
                
                # 假數據特徵檢測
                if (8 <= avg_kills <= 22 and 
                    4 <= avg_deaths <= 18 and 
                    120 <= avg_acs <= 280 and
                    stats_count >= 3):
                    
                    # 檢查數據分布是否過於平均
                    kills_var = sum((s.kills - avg_kills) ** 2 for s in team_stats) / stats_count
                    if kills_var < 20:  # 變異度太小
                        suspicious_stats.extend(list(team_stats))
                        self.stdout.write(f"    ⚠️ 可疑：數據過於平均")
        
        if suspicious_stats:
            self.stdout.write(f"\n🔍 發現 {len(suspicious_stats)} 筆可疑數據:")
            
            # 按遊戲分組顯示
            games_with_suspicious = {}
            for stat in suspicious_stats:
                if stat.game not in games_with_suspicious:
                    games_with_suspicious[stat.game] = []
                games_with_suspicious[stat.game].append(stat)
            
            for game, stats in list(games_with_suspicious.items())[:5]:  # 只顯示前5場
                self.stdout.write(f"\n  遊戲: {game.match.team1.name} vs {game.match.team2.name}")
                for stat in stats[:3]:  # 每場遊戲顯示3位選手
                    self.stdout.write(f"    {stat.player.name}: K{stat.kills} D{stat.deaths} A{stat.assists} ACS{stat.acs}")
            
            if len(games_with_suspicious) > 5:
                self.stdout.write(f"    ... 還有 {len(games_with_suspicious) - 5} 場類似遊戲")
            
            if dry_run:
                self.stdout.write(f"\n🔍 乾跑模式：會刪除 {len(suspicious_stats)} 筆記錄")
            else:
                confirm = input(f"\n確定要刪除這 {len(suspicious_stats)} 筆可疑數據嗎? (yes/no): ")
                if confirm.lower() == 'yes':
                    with transaction.atomic():
                        deleted_count = 0
                        for stat in suspicious_stats:
                            stat.delete()
                            deleted_count += 1
                    
                    self.stdout.write(f"✅ 已刪除 {deleted_count} 筆假數據")
                else:
                    self.stdout.write("ℹ️ 已取消刪除")
        else:
            self.stdout.write("✅ 沒有發現可疑的假數據")
        
        final_count = PlayerGameStat.objects.count()
        self.stdout.write(f"\n📊 最終統計記錄數: {final_count}")
