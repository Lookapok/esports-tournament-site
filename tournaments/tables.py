# tournaments/tables.py
import django_tables2 as tables
from .models import PlayerGameStat

def get_opponent_info(record):
    """
    根據選手所屬隊伍，返回對手信息
    """
    match = record.game.match
    player_team = record.team
    
    # 確定對手隊伍
    if match.team1 == player_team:
        opponent = match.team2
    elif match.team2 == player_team:
        opponent = match.team1
    else:
        # 如果選手隊伍不是比賽中的任一隊伍，顯示完整對戰信息
        if match.team1 and match.team2:
            return f"R{match.round_number}: {match.team1.name} vs {match.team2.name}"
        else:
            return f"R{match.round_number}: TBD"
    
    # 顯示對手名稱 - 簡潔版本
    if opponent:
        return f"R{match.round_number} vs {opponent.name}"
    else:
        return f"R{match.round_number} vs TBD"

class StatsTable(tables.Table):
    # --- [修改] 比賽欄位 - 顯示對手信息 ---
    # 使用 lambda 函數顯示對手信息
    match = tables.LinkColumn(
        "tournament_detail",
        text=lambda record: get_opponent_info(record),
        args=[tables.A("game.match.tournament.pk")],
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