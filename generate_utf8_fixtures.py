import os
import django
import json

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.core import serializers
from tournaments.models import Tournament, Team, Player, Match, Group, Standing, Game, PlayerGameStat

print("開始生成 UTF-8 編碼的 fixtures...")

# 取得所有錦標賽相關資料
tournaments_data = serializers.serialize('json', Tournament.objects.all(), indent=2)
teams_data = serializers.serialize('json', Team.objects.all(), indent=2)
players_data = serializers.serialize('json', Player.objects.all(), indent=2)
matches_data = serializers.serialize('json', Match.objects.all(), indent=2)
groups_data = serializers.serialize('json', Group.objects.all(), indent=2)
standings_data = serializers.serialize('json', Standing.objects.all(), indent=2)
games_data = serializers.serialize('json', Game.objects.all(), indent=2)
playergamestats_data = serializers.serialize('json', PlayerGameStat.objects.all(), indent=2)

print("資料序列化完成，開始合併...")

# 合併所有資料
all_data = []
all_data.extend(json.loads(tournaments_data))
all_data.extend(json.loads(teams_data))
all_data.extend(json.loads(players_data))
all_data.extend(json.loads(matches_data))
all_data.extend(json.loads(groups_data))
all_data.extend(json.loads(standings_data))
all_data.extend(json.loads(games_data))
all_data.extend(json.loads(playergamestats_data))

print(f"合併完成，總共 {len(all_data)} 個資料物件")

# 寫入檔案，明確指定 UTF-8 編碼
with open('fixtures/all_tournament_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("✅ UTF-8 fixtures 生成完成！")
print(f"檔案大小: {os.path.getsize('fixtures/all_tournament_data.json')} bytes")
