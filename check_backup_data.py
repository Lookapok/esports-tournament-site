#!/usr/bin/env python
import json

def check_backup_data():
    """檢查備份檔案中的完整資料"""
    
    backup_files = [
        'backup_utf8.json',
        'local_backup_20251005_204901.json', 
        'local_backup_fixed_20251005_205426.json',
        'tournaments_data.json'
    ]
    
    for backup_file in backup_files:
        try:
            print(f"\n=== 檢查 {backup_file} ===")
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 統計各種資料
            stats = {}
            team_names = set()
            tournament_names = set()
            
            for item in data:
                model = item['model']
                if model not in stats:
                    stats[model] = 0
                stats[model] += 1
                
                # 收集隊伍名稱
                if model == 'tournaments.team':
                    team_names.add(item['fields']['name'])
                
                # 收集賽事名稱
                if model == 'tournaments.tournament':
                    tournament_names.add(item['fields']['name'])
            
            print(f"📊 總項目數: {len(data)}")
            for model, count in sorted(stats.items()):
                emoji = "🏆" if "tournament" in model else "👥" if "team" in model else "🎮" if "player" in model else "📋"
                print(f"  {emoji} {model}: {count}")
            
            if team_names:
                print(f"\n👥 隊伍總數: {len(team_names)}")
                print("隊伍名稱:")
                for i, name in enumerate(sorted(team_names), 1):
                    print(f"  {i:2d}. {name}")
            
            if tournament_names:
                print(f"\n🏆 賽事名稱:")
                for name in tournament_names:
                    print(f"  - {name}")
                    
        except FileNotFoundError:
            print(f"❌ 檔案 {backup_file} 不存在")
        except Exception as e:
            print(f"❌ 讀取 {backup_file} 時發生錯誤: {e}")

if __name__ == "__main__":
    check_backup_data()
