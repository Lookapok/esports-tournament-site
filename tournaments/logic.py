# tournaments/logic.py (這是新檔案)

from itertools import combinations
from django.db import models
from .models import Match, Standing, Group, Team

def generate_round_robin_matches(tournament):
    """
    為一場「分組循環」賽事自動產生所有比賽。
    """
    # 先刪除這場賽事可能已存在的舊賽程，避免重複產生
    Match.objects.filter(tournament=tournament).delete()

    # 取得賽事的所有分組
    groups = tournament.groups.all()

    matches_created_count = 0
    for group in groups:
        # 取得該分組內的所有隊伍
        teams_in_group = list(group.teams.all())

        # 如果分組內少於兩支隊伍，則無法產生比賽，跳過
        if len(teams_in_group) < 2:
            continue

        # 使用 combinations 函式庫，自動產生所有不重複的隊伍配對
        # 例如 [A, B, C] -> (A, B), (A, C), (B, C)
        for team1, team2 in combinations(teams_in_group, 2):
            Match.objects.create(
                tournament=tournament,
                round_number=1, # 分組賽通常視為第一輪
                team1=team1,
                team2=team2,
                status='scheduled' # 將狀態設為「尚未開始」
            )
            matches_created_count += 1

    return matches_created_count

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


def generate_single_elimination_matches(tournament):
    """
    為「單淘汰」賽事自動產生所有比賽。
    單淘汰制：敗者直接淘汰，勝者晉級下一輪，直到產生最終冠軍。
    """
    import math
    
    # 先刪除這場賽事可能已存在的舊賽程，避免重複產生
    Match.objects.filter(tournament=tournament).delete()
    
    # 取得所有參賽隊伍
    teams = list(tournament.participants.all())
    team_count = len(teams)
    
    if team_count < 2:
        return 0
    
    # 計算需要多少輪比賽（找到大於等於隊伍數量的最小 2 的次方）
    bracket_size = 1
    while bracket_size < team_count:
        bracket_size *= 2
    
    # 計算總輪數
    total_rounds = int(math.log2(bracket_size))
    
    matches_created_count = 0
    
    # 第一輪：處理實際的隊伍配對
    # 如果隊伍數量不是 2 的次方，某些隊伍會直接晉級（bye）
    first_round_matches = team_count // 2  # 第一輪實際比賽場數
    bye_teams = team_count % 2  # 輪空隊伍數量
    
    # 創建第一輪比賽
    for i in range(first_round_matches):
        team1 = teams[i * 2]
        team2 = teams[i * 2 + 1]
        
        Match.objects.create(
            tournament=tournament,
            round_number=1,
            team1=team1,
            team2=team2,
            status='scheduled'
        )
        matches_created_count += 1
    
    # 計算每輪需要的比賽場數並創建佔位符比賽
    current_teams = (team_count + 1) // 2  # 第一輪後剩餘隊伍數量
    
    for round_num in range(2, total_rounds + 1):
        matches_in_round = current_teams // 2
        
        for match_num in range(matches_in_round):
            Match.objects.create(
                tournament=tournament,
                round_number=round_num,
                team1=None,  # 待定，比賽結果出來後填入
                team2=None,  # 待定，比賽結果出來後填入
                status='scheduled'
            )
            matches_created_count += 1
        
        current_teams = matches_in_round  # 下一輪的隊伍數量
    
    return matches_created_count


def generate_double_elimination_matches(tournament):
    """
    為「雙淘汰」賽事自動產生所有比賽。
    雙淘汰制：每支隊伍有兩次失敗的機會，分為勝部和敗部。
    """
    import math
    
    # 先刪除這場賽事可能已存在的舊賽程，避免重複產生
    Match.objects.filter(tournament=tournament).delete()
    
    # 取得所有參賽隊伍
    teams = list(tournament.participants.all())
    team_count = len(teams)
    
    if team_count < 2:
        return 0
    
    # 計算括號大小（找到大於等於隊伍數量的最小 2 的次方）
    bracket_size = 1
    while bracket_size < team_count:
        bracket_size *= 2
    
    matches_created_count = 0
    
    # === 勝部（Upper Bracket）===
    # 勝部第一輪
    first_round_matches = team_count // 2
    
    for i in range(first_round_matches):
        team1 = teams[i * 2] if i * 2 < len(teams) else None
        team2 = teams[i * 2 + 1] if i * 2 + 1 < len(teams) else None
        
        if team1 and team2:
            Match.objects.create(
                tournament=tournament,
                round_number=1,
                team1=team1,
                team2=team2,
                status='scheduled',
                is_lower_bracket=False  # 勝部比賽
            )
            matches_created_count += 1
    
    # 勝部後續輪次
    upper_rounds = int(math.log2(bracket_size))
    current_teams = (team_count + 1) // 2
    
    for round_num in range(2, upper_rounds + 1):
        matches_in_round = current_teams // 2
        
        for match_num in range(matches_in_round):
            Match.objects.create(
                tournament=tournament,
                round_number=round_num,
                team1=None,  # 待定
                team2=None,  # 待定
                status='scheduled',
                is_lower_bracket=False  # 勝部比賽
            )
            matches_created_count += 1
        
        current_teams = matches_in_round
    
    # === 敗部（Lower Bracket）===
    # 敗部的輪次編號從勝部最後一輪 + 1 開始
    lower_bracket_start_round = upper_rounds + 1
    
    # 敗部第一輪：接收勝部第一輪的敗者
    if first_round_matches > 1:
        lower_first_matches = first_round_matches // 2
        
        for match_num in range(lower_first_matches):
            Match.objects.create(
                tournament=tournament,
                round_number=lower_bracket_start_round,
                team1=None,  # 勝部第一輪敗者
                team2=None,  # 勝部第一輪敗者
                status='scheduled',
                is_lower_bracket=True  # 敗部比賽
            )
            matches_created_count += 1
    
    # 敗部後續輪次（複雜的配對邏輯）
    lower_round = lower_bracket_start_round + 1
    lower_teams = first_round_matches // 2
    
    # 敗部輪次數量通常是勝部輪次數量的兩倍左右
    for i in range(upper_rounds - 1):
        # 每兩輪敗部比賽：
        # 1. 敗部倖存者 vs 敗部倖存者
        # 2. 敗部倖存者 vs 勝部新敗者
        
        # 第一小輪：敗部內部對戰
        if lower_teams > 1:
            matches_in_lower = lower_teams // 2
            for match_num in range(matches_in_lower):
                Match.objects.create(
                    tournament=tournament,
                    round_number=lower_round,
                    team1=None,
                    team2=None,
                    status='scheduled',
                    is_lower_bracket=True
                )
                matches_created_count += 1
            
            lower_teams = matches_in_lower
            lower_round += 1
        
        # 第二小輪：敗部倖存者 vs 勝部敗者
        if i < upper_rounds - 2:  # 不是最後一輪
            for match_num in range(lower_teams):
                Match.objects.create(
                    tournament=tournament,
                    round_number=lower_round,
                    team1=None,  # 敗部倖存者
                    team2=None,  # 勝部敗者
                    status='scheduled',
                    is_lower_bracket=True
                )
                matches_created_count += 1
            
            lower_round += 1
    
    # === 總決賽（Grand Finals）===
    # 勝部冠軍 vs 敗部冠軍
    Match.objects.create(
        tournament=tournament,
        round_number=lower_round,
        team1=None,  # 勝部冠軍
        team2=None,  # 敗部冠軍
        status='scheduled',
        is_lower_bracket=False  # 總決賽
    )
    matches_created_count += 1
    
    # 如果敗部冠軍在總決賽獲勝，需要重賽（Reset Grand Finals）
    Match.objects.create(
        tournament=tournament,
        round_number=lower_round + 1,
        team1=None,  # 重賽：勝部冠軍
        team2=None,  # 重賽：敗部冠軍
        status='scheduled',
        is_lower_bracket=False  # 重賽
    )
    matches_created_count += 1
    
    return matches_created_count


def advance_single_elimination_winners(tournament):
    """
    單淘汰賽：將勝者晉級到下一輪比賽
    當比賽結束後調用此函數來自動安排晉級
    """
    from django.db.models import Max
    
    updated_matches = 0
    
    # 按輪次順序處理比賽
    max_round = Match.objects.filter(tournament=tournament).aggregate(
        max_round=Max('round_number')
    )['max_round'] or 0
    
    for round_num in range(1, max_round):
        # 獲取本輪已完成的比賽
        completed_matches = Match.objects.filter(
            tournament=tournament,
            round_number=round_num,
            status='completed',
            winner__isnull=False
        )
        
        # 獲取下一輪的比賽
        next_round_matches = list(Match.objects.filter(
            tournament=tournament,
            round_number=round_num + 1,
            team1__isnull=True,  # 還沒安排隊伍的比賽
            team2__isnull=True
        ).order_by('id'))
        
        # 將勝者安排到下一輪
        winners = [match.winner for match in completed_matches]
        
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners) and i // 2 < len(next_round_matches):
                next_match = next_round_matches[i // 2]
                next_match.team1 = winners[i]
                next_match.team2 = winners[i + 1] if i + 1 < len(winners) else None
                next_match.save()
                updated_matches += 1
    
    return updated_matches


def advance_double_elimination_winners(tournament):
    """
    雙淘汰賽：處理勝者晉級和敗者掉入敗部的邏輯
    這是一個複雜的函數，需要根據比賽結果來安排隊伍到正確的位置
    """
    updated_matches = 0
    
    # 獲取所有已完成的比賽
    completed_matches = Match.objects.filter(
        tournament=tournament,
        status='completed',
        winner__isnull=False
    )
    
    # 分別處理勝部和敗部的比賽
    upper_matches = completed_matches.filter(is_lower_bracket=False)
    lower_matches = completed_matches.filter(is_lower_bracket=True)
    
    # 這裡需要複雜的邏輯來處理各種晉級情況
    # 由於雙淘汰的複雜性，這部分可能需要根據具體需求來實現
    
    return updated_matches