# tournaments/logic.py (這是新檔案)

from itertools import combinations
from .models import Match

def generate_round_robin_matches(tournament):
    """
    為一場「分組循環」賽事自動產生所有比賽。
    """
    # 先刪除可能已存在的舊賽程，避免重複產生
    Match.objects.filter(tournament=tournament).delete()

    # 取得賽事的所有分組
    groups = tournament.groups.all()

    for group in groups:
        # 取得該分組內的所有隊伍
        teams = list(group.teams.all())

        # 如果分組內少於兩支隊伍，則無法產生比賽，跳過
        if len(teams) < 2:
            continue

        # 使用 combinations 產生所有不重複的隊伍配對
        # 例如 [A, B, C] -> (A, B), (A, C), (B, C)
        for team1, team2 in combinations(teams, 2):
            Match.objects.create(
                tournament=tournament,
                round_number=1, # 分組賽通常視為第一輪
                team1=team1,
                team2=team2,
                status='scheduled'
            )

    # 可以回傳產生了多少場比賽
    return Match.objects.filter(tournament=tournament).count()

# tournaments/logic.py

# ... (檔案上半部的程式碼維持不變) ...

def generate_swiss_round_matches(tournament):
    """
    為「瑞士輪」賽事產生下一輪的對戰組合。
    """
    # 找出目前的最高輪次
    last_match = Match.objects.filter(tournament=tournament).order_by('-round_number').first()
    current_round = last_match.round_number if last_match else 0
    next_round = current_round + 1

    # 取得所有隊伍的積分榜，並按照分數高低排序
    standings = list(tournament.standings.all().order_by('-points', '-wins'))

    # 找出已經配對過的隊伍
    paired_teams = set()
    # 找出所有已經打過的對戰組合
    past_matches = set()
    for match in Match.objects.filter(tournament=tournament):
        past_matches.add(tuple(sorted((match.team1.id, match.team2.id))))

    matches_created_count = 0

    # 開始配對
    for i in range(len(standings)):
        team1_standing = standings[i]
        if team1_standing.team.id in paired_teams:
            continue # 如果已經配對過，就跳過

        # 從後面的隊伍中，尋找一個尚未配對、且沒對戰過的對手
        opponent_found = False
        for j in range(i + 1, len(standings)):
            team2_standing = standings[j]
            if team2_standing.team.id in paired_teams:
                continue

            # 檢查這兩隊是否對戰過
            matchup = tuple(sorted((team1_standing.team.id, team2_standing.team.id)))
            if matchup not in past_matches:
                # 找到了！建立比賽
                Match.objects.create(
                    tournament=tournament,
                    round_number=next_round,
                    team1=team1_standing.team,
                    team2=team2_standing.team
                )
                paired_teams.add(team1_standing.team.id)
                paired_teams.add(team2_standing.team.id)
                opponent_found = True
                matches_created_count += 1
                break # 中斷內層迴圈，繼續為下個隊伍配對

        # 如果所有隊伍都打過了，只好輪空 (暫不處理)
        if not opponent_found:
            # TODO: Handle byes for odd number of players or no available opponents
            pass

    return matches_created_count