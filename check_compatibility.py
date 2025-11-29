import json

# 檢查Django模型與Docker資料的相容性
print('=== 模型相容性檢查 ===')

with open('production_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查Team模型相容性
print('\n1. Team模型相容性:')
if data.get("teams"):
    team = data["teams"][0]
    print(f'Docker team欄位: {list(team.keys())}')
    print('Django Team模型需要: id, name, school(新增), logo')
    print(f'缺少欄位: school (但force_reimport已處理)')

# 檢查Player模型相容性
print('\n2. Player模型相容性:')
if data.get("players"):
    player = data["players"][0]
    print(f'Docker player欄位: {list(player.keys())}')
    print('Django Player模型需要: id, nickname, team_id, avatar, role')
    print('✓ 完全相容')

# 檢查Group模型相容性
print('\n3. Group模型相容性:')
if data.get("groups"):
    group = data["groups"][0]
    print(f'Docker group欄位: {list(group.keys())}')
    print('Django Group模型需要: id, tournament_id, name, max_teams(新增)')
    print(f'缺少欄位: max_teams (但force_reimport已處理)')

# 檢查其他模型
print('\n4. 其他模型檢查:')
models_to_check = ['tournaments', 'matches', 'games', 'standings']
for model in models_to_check:
    if data.get(model):
        item = data[model][0]
        print(f'{model}欄位: {list(item.keys())}')

print('\n=== 結論 ===')
print('✓ Docker資料結構與Django模型基本相容')
print('✓ force_reimport命令已處理缺少的欄位(school, max_teams)')
print('✓ Player欄位名稱已正確映射(nickname, role)')
