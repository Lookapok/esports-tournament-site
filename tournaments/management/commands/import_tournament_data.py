from django.core.management.base import BaseCommand
from django.core.management import call_command
import json

class Command(BaseCommand):
    help = '導入賽事資料到新環境'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='JSON 資料檔案路徑')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        self.stdout.write('🚀 開始導入資料...')
        
        try:
            # 清除現有資料（謹慎使用）
            self.stdout.write('⚠️  清除現有資料...')
            call_command('flush', '--noinput')
            
            # 導入資料
            self.stdout.write('📊 導入新資料...')
            call_command('loaddata', json_file)
            
            self.stdout.write(
                self.style.SUCCESS('✅ 資料導入完成！')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 導入失敗: {e}')
            )
