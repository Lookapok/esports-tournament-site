#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

# 載入並分析 Docker 資料
with open('production_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('📊 Docker 資料結構分析:')
for key in data.keys():
    items = data[key] if isinstance(data[key], list) else [data[key]]
    print(f'{key}: {len(items)} 筆')

print('\n🔍 球員資料樣本:')
players = data.get('players', [])[:3]
for i, player in enumerate(players, 1):
    nickname = player.get("nickname", "N/A")
    player_id = player.get("id", "N/A")
    team_id = player.get("team_id", "N/A")
    role = player.get("role", "N/A")
    print(f'{i}. ID:{player_id} | 暱稱:{nickname} | 隊伍:{team_id} | 角色:{role}')

print('\n🎮 檢查是否有統計資料:')
if 'player_stats' in data:
    print(f'player_stats: {len(data["player_stats"])} 筆')
elif 'stats' in data:
    print(f'stats: {len(data["stats"])} 筆')
elif 'game_stats' in data:
    print(f'game_stats: {len(data["game_stats"])} 筆')
else:
    print('❌ 沒有發現任何統計資料！')
    print('可用的鍵值:', list(data.keys()))
