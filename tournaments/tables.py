# tournaments/tables.py (這是新檔案)
import django_tables2 as tables
from .models import PlayerMatchStat

class StatsTable(tables.Table):
    # 讓選手和隊伍名稱可以連結到對應的頁面
    player = tables.Column(linkify=lambda record: record.player.get_absolute_url() if hasattr(record.player, 'get_absolute_url') else None)
    team = tables.Column(linkify=lambda record: record.team.get_absolute_url() if hasattr(record.team, 'get_absolute_url') else None)

    class Meta:
        model = PlayerMatchStat
        # 定義表格要顯示的欄位順序
        sequence = ('match', 'player', 'team', 'kills', 'deaths', 'assists', 'first_kills', 'acs')
        # 排除我們不想顯示的欄位
        exclude = ('id',)
        # 為表格加上 Bootstrap 的樣式
        attrs = {"class": "table table-striped table-hover"}
        # 設定預設的空白提示文字
        empty_text = "目前尚無符合條件的數據。"