#!/usr/bin/env python
import os
import sys
import django
import json

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.core.management import call_command

def restore_complete_data():
    """恢復完整的 37 支隊伍資料"""
    
    print("🏁 開始恢復完整資料（37支隊伍）...")
    
    # 檢查完整備份檔案
    backup_file = 'local_backup_fixed_20251005_205426.json'
    
    if not os.path.exists(backup_file):
        print(f"❌ 找不到完整備份檔案：{backup_file}")
        return
    
    try:
        # 讀取並篩選 tournaments 相關資料
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 篩選只要 tournaments 應用的資料
        tournaments_data = [
            item for item in data 
            if item['model'].startswith('tournaments.')
        ]
        
        print(f"📊 找到 {len(tournaments_data)} 筆 tournaments 相關資料")
        
        # 創建臨時檔案
        temp_file = 'temp_complete_tournaments.json'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(tournaments_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 建立暫時檔案: {temp_file}")
        
        # 先清空現有的 tournaments 資料
        print("🗑️  清空現有 tournaments 資料...")
        
        from tournaments.models import Tournament, Team, Player, Group, Match, Standing
        
        # 依照外鍵關係順序刪除
        Standing.objects.all().delete()
        Match.objects.all().delete()
        Group.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        Tournament.objects.all().delete()
        
        # 載入完整資料
        print("⏳ 載入完整資料中...")
        call_command('loaddata', temp_file, verbosity=1)
        
        print("✅ 資料載入成功！")
        
        # 驗證恢復結果
        from tournaments.models import Tournament, Team, Player, Group, Match
        
        tournament_count = Tournament.objects.count()
        team_count = Team.objects.count()
        player_count = Player.objects.count()
        group_count = Group.objects.count()
        match_count = Match.objects.count()
        
        print(f"\n📊 恢復後的完整資料統計:")
        print(f"  🏆 賽事: {tournament_count}")
        print(f"  👥 隊伍: {team_count}")
        print(f"  🎮 選手: {player_count}")
        print(f"  📋 分組: {group_count}")
        print(f"  ⚔️  比賽: {match_count}")
        
        total_records = tournament_count + team_count + player_count + group_count + match_count
        print(f"🎉 總共恢復 {total_records} 筆資料！")
        
        # 清理暫時檔案
        os.remove(temp_file)
        print(f"🗑️  清理暫時檔案: {temp_file}")
        
        print("🎊 完整資料恢復完成！現在有 37 支隊伍了！")
        
    except Exception as e:
        print(f"❌ 恢復資料時發生錯誤: {e}")

if __name__ == "__main__":
    restore_complete_data()
