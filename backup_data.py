#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

# 設定環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

# 設定 UTF-8 編碼
import locale
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# 執行備份
try:
    execute_from_command_line([
        'manage.py', 'dumpdata', 
        '--natural-foreign', '--natural-primary',
        '-e', 'contenttypes', '-e', 'auth.Permission',
        '--output', 'data_backup.json'
    ])
    print("備份成功完成!")
except Exception as e:
    print(f"備份失敗: {e}")
