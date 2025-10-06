"""
Django 管理命令：優化資料庫索引以提升查詢性能
執行方式: python manage.py optimize_database_indexes
"""

from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '為電競賽事系統添加資料庫索引以提升查詢性能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只顯示要執行的 SQL 語句，不實際執行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 針對最常用的查詢添加索引
        indexes = [
            # Tournament 索引
            {
                'name': 'idx_tournament_status_start_date',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_tournament_status_start_date 
                    ON tournaments_tournament(status, start_date DESC);
                ''',
                'description': '賽事狀態和開始日期的複合索引'
            },
            {
                'name': 'idx_tournament_format',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_tournament_format 
                    ON tournaments_tournament(format);
                ''',
                'description': '賽事格式索引'
            },
            
            # Match 索引
            {
                'name': 'idx_match_tournament_status',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_match_tournament_status 
                    ON tournaments_match(tournament_id, status);
                ''',
                'description': '比賽的賽事ID和狀態複合索引'
            },
            {
                'name': 'idx_match_tournament_round',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_match_tournament_round 
                    ON tournaments_match(tournament_id, round_number);
                ''',
                'description': '比賽的賽事ID和輪次複合索引'
            },
            {
                'name': 'idx_match_teams',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_match_team1_team2 
                    ON tournaments_match(team1_id, team2_id);
                ''',
                'description': '比賽隊伍索引'
            },
            {
                'name': 'idx_match_time_status',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_match_time_status 
                    ON tournaments_match(match_time, status) 
                    WHERE status = 'scheduled';
                ''',
                'description': '預定比賽時間索引（僅針對已排程的比賽）'
            },
            
            # Team 索引
            {
                'name': 'idx_team_name',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_team_name 
                    ON tournaments_team(name);
                ''',
                'description': '隊伍名稱索引'
            },
            
            # Standing 索引
            {
                'name': 'idx_standing_tournament_points',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_standing_tournament_points 
                    ON tournaments_standing(tournament_id, points DESC, wins DESC);
                ''',
                'description': '積分榜排序索引（按積分和勝場降序）'
            },
            
            # Group 索引
            {
                'name': 'idx_group_tournament',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_group_tournament 
                    ON tournaments_group(tournament_id);
                ''',
                'description': '分組的賽事ID索引'
            },
        ]

        self.stdout.write(
            self.style.SUCCESS('開始資料庫索引優化...')
        )

        with connection.cursor() as cursor:
            for index in indexes:
                try:
                    if dry_run:
                        self.stdout.write(f'\n{index["description"]}:')
                        self.stdout.write(f'SQL: {index["sql"].strip()}')
                    else:
                        cursor.execute(index['sql'])
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ 已創建索引: {index["description"]}')
                        )
                        
                except Exception as e:
                    if 'already exists' in str(e):
                        self.stdout.write(
                            self.style.WARNING(f'- 索引已存在: {index["description"]}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'✗ 創建索引失敗: {index["description"]} - {e}')
                        )
                        logger.error(f'Index creation failed: {index["name"]} - {e}')

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('這是預覽模式，沒有實際執行任何 SQL 語句'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('資料庫索引優化完成！'))
            
            # 執行 ANALYZE 來更新統計信息（僅 PostgreSQL）
            try:
                cursor.execute('ANALYZE;')
                self.stdout.write(self.style.SUCCESS('✓ 已更新資料庫統計信息'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'更新統計信息失敗（這對 SQLite 是正常的）: {e}'))
