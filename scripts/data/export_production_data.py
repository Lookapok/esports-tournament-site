#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
資料匯出腳本 - 專門處理中文字元編碼問題
"""

import os
import sys
import django
import json
from datetime import datetime

# 設定編碼
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing, PlayerGameStat
from django.core import serializers

def export_tournament_data():
    """匯出錦標賽資料"""
    try:
        print("🔄 開始匯出錦標賽資料...")
        
        data = {}
        
        # 匯出各類資料
        data['tournaments'] = list(Tournament.objects.all().values())
        data['teams'] = list(Team.objects.all().values())
        data['players'] = list(Player.objects.all().values())
        data['matches'] = list(Match.objects.all().values())
        data['games'] = list(Game.objects.all().values())
        data['groups'] = list(Group.objects.all().values())
        data['standings'] = list(Standing.objects.all().values())
        data['player_stats'] = list(PlayerGameStat.objects.all().values())
        
        # 處理日期格式
        for item in data['tournaments']:
            if item.get('start_date'):
                item['start_date'] = str(item['start_date'])
            if item.get('end_date'):
                item['end_date'] = str(item['end_date'])
        
        for item in data['matches']:
            if item.get('date'):
                item['date'] = str(item['date'])
        
        for item in data['games']:
            if item.get('timestamp'):
                item['timestamp'] = str(item['timestamp'])
        
        # 寫入檔案
        with open('production_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ 資料匯出成功！")
        print(f"📊 錦標賽: {len(data['tournaments'])}")
        print(f"👥 隊伍: {len(data['teams'])}")
        print(f"🎮 選手: {len(data['players'])}")
        print(f"⚔️  比賽: {len(data['matches'])}")
        print(f"🎯 遊戲: {len(data['games'])}")
        print(f"📈 積分榜: {len(data['standings'])}")
        print(f"📋 選手統計: {len(data['player_stats'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 匯出失敗: {str(e)}")
        return False

if __name__ == "__main__":
    export_tournament_data()
