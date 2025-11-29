from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Team, Player, Match, Standing
from django.conf import settings

class Command(BaseCommand):
    help = '檢查 Supabase 資料庫中的資料狀態'

    def handle(self, *args, **options):
        self.stdout.write("🔍 檢查 Supabase 資料庫資料...")
        
        # 顯示資料庫連接資訊
        db_settings = settings.DATABASES['default']
        self.stdout.write(f"📊 資料庫引擎: {db_settings.get('ENGINE')}")
        self.stdout.write(f"🌐 資料庫主機: {db_settings.get('HOST')}")
        
        try:
            # 檢查各項資料數量
            tournament_count = Tournament.objects.count()
            team_count = Team.objects.count()
            player_count = Player.objects.count()
            match_count = Match.objects.count()
            standing_count = Standing.objects.count()
            
            self.stdout.write("\n📈 資料統計:")
            self.stdout.write(f"🏆 錦標賽: {tournament_count} 筆")
            self.stdout.write(f"👥 隊伍: {team_count} 筆")
            self.stdout.write(f"🎮 選手: {player_count} 筆")
            self.stdout.write(f"⚔️ 比賽: {match_count} 筆")
            self.stdout.write(f"📊 積分表: {standing_count} 筆")
            
            if tournament_count > 0:
                # 顯示錦標賽詳情
                tournaments = Tournament.objects.all()[:5]
                self.stdout.write("\n🏆 錦標賽清單:")
                for t in tournaments:
                    self.stdout.write(f"  - {t.name} ({t.game}) - {t.status}")
            
            if team_count > 0:
                # 顯示隊伍詳情
                teams = Team.objects.all()[:5]
                self.stdout.write("\n👥 隊伍清單:")
                for team in teams:
                    self.stdout.write(f"  - {team.name}")
            
            # 檢查是否有B組資料
            b_group_standings = Standing.objects.filter(group__name__icontains='B').count()
            self.stdout.write(f"\n🅱️ B組積分記錄: {b_group_standings} 筆")
            
            if tournament_count == 0:
                self.stdout.write(self.style.WARNING("\n⚠️  資料庫是空的！需要執行資料匯入。"))
                self.stdout.write("💡 執行: python manage.py load_tournament_data")
            else:
                self.stdout.write(self.style.SUCCESS(f"\n✅ 資料庫連接正常，共有 {tournament_count + team_count + player_count + match_count} 筆記錄"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ 資料庫連接錯誤: {str(e)}"))
            self.stdout.write("💡 請檢查 DATABASE_URL 設定和 Supabase 連接")
