#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
導出玩家名單到 players.json
用於 Discord Bot 的模糊比對功能
"""

import os
import django
import json
from pathlib import Path

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from tournaments.models import Player

def export_players_to_json():
    """從資料庫導出所有玩家暱稱到 players.json"""
    
    print("🔍 正在從資料庫提取玩家資料...")
    
    # 從資料庫撈出所有選手的暱稱
    all_nicknames = list(Player.objects.values_list('nickname', flat=True).order_by('nickname'))
    
    if not all_nicknames:
        print("⚠️ 資料庫中沒有找到任何玩家資料")
        return False
    
    # 移除空值和重複項
    all_nicknames = list(filter(None, set(all_nicknames)))
    all_nicknames.sort()
    
    # 寫入到 players.json 檔案
    output_file = Path('players.json')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_nicknames, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 成功！已匯出 {len(all_nicknames)} 位選手資料到 {output_file}")
        print("📋 玩家名單預覽:")
        
        # 顯示前 10 個玩家名稱作為預覽
        for i, nickname in enumerate(all_nicknames[:10], 1):
            print(f"  {i:2d}. {nickname}")
        
        if len(all_nicknames) > 10:
            print(f"  ... 還有 {len(all_nicknames) - 10} 位玩家")
        
        print(f"\n📁 檔案位置: {output_file.absolute()}")
        print("🤖 現在可以啟動 Discord Bot 了！")
        
        return True
        
    except Exception as e:
        print(f"❌ 寫入檔案失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 WTACS 玩家名單導出工具")
    print("=" * 40)
    
    success = export_players_to_json()
    
    if success:
        print("\n✨ 導出完成！Discord Bot 現在可以使用模糊比對功能了。")
    else:
        print("\n❌ 導出失敗！請檢查資料庫連接和玩家資料。")
