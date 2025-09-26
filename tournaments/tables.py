# tournaments/tables.py
import django_tables2 as tables
from .models import PlayerGameStat

class StatsTable(tables.Table):
    # --- [修改] 比賽欄位 ---
    # 使用 lambda 函數自訂連結文字，讓它變短
    match = tables.LinkColumn(
        "tournament_detail",
        # 只顯示「賽事名稱 - R輪次」
        text=lambda record: f"{record.game.match.tournament.name} - R{record.game.match.round_number}",
        args=[tables.A("game.match.pk")],
        verbose_name="比賽"
    )
    
    # --- [修改] 選手欄位 ---
    # 使用 accessor 直接抓取 player 物件中的 nickname 屬性
    player = tables.Column(
        accessor="player.nickname", 
        verbose_name="選手"
    )

    # --- [修改] 代表隊伍欄位 ---
    # 同樣只抓取 team 的 name 屬性
    team = tables.Column(
        accessor="team.name",
        verbose_name="代表隊伍"
    )

    # --- [修改] 地圖欄位 ---
    # 使用 accessor 直接抓取關聯的 game 物件中的 map_name 欄位
    game = tables.Column(
        accessor="game.map_name", 
        verbose_name="地圖"
    )

    class Meta:
        model = PlayerGameStat
        template_name = "django_tables2/bootstrap5.html"
        
        # 欄位順序與要顯示的欄位
        fields = (
            "match", 
            "player", 
            "team", 
            "game",  # <-- 注意這裡的名字要和上面我們定義的變數名一致
            "kills", 
            "deaths", 
            "assists", 
            "first_kills", 
            "acs"
        )
        sequence = fields