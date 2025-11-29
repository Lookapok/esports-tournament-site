import json

# 檢查Docker原始資料
with open('production_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== Docker原始資料統計 ===')
print(f'錦標賽: {len(data.get("tournaments", []))}')
print(f'隊伍: {len(data.get("teams", []))}')
print(f'球員: {len(data.get("players", []))}')
print(f'比賽: {len(data.get("matches", []))}')
print(f'遊戲: {len(data.get("games", []))}')
print(f'分組: {len(data.get("groups", []))}')
print(f'排名: {len(data.get("standings", []))}')

# 檢查資料結構
print('\n=== 資料結構檢查 ===')
if data.get("teams"):
    team = data["teams"][0]
    print(f'第一個隊伍欄位: {list(team.keys())}')

if data.get("players"):
    player = data["players"][0]
    print(f'第一個球員欄位: {list(player.keys())}')

if data.get("groups"):
    group = data["groups"][0]
    print(f'第一個分組欄位: {list(group.keys())}')
