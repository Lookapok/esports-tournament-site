# tournaments/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match, Standing, Tournament

# tournaments/signals.py

def recalculate_standings(tournament_id):
    """
    重新計算一場完整賽事的所有積分榜數據（更穩健的版本）。
    """
    tournament = Tournament.objects.get(id=tournament_id)

    # 在計算前，先確保所有參賽者都有一個積分榜紀錄
    for team in tournament.participants.all():
        Standing.objects.get_or_create(tournament=tournament, team=team)

    # 1. 將所有該賽事的積分榜數據歸零
    Standing.objects.filter(tournament=tournament).update(
        wins=0, losses=0, draws=0, points=0
    )

    # 2. 找出所有已完成的比賽
    completed_matches = Match.objects.filter(
        tournament=tournament, 
        status='completed'
    )

    # 3. 遍歷每一場比賽，重新累加勝敗與積分
    for match in completed_matches:
        if match.winner and match.team1 and match.team2:
            winner_team = match.winner
            loser_team = match.team1 if match.team2 == winner_team else match.team2

            # 因為我們在開頭確保了紀錄存在，所以這裡可以安心用 .get()
            winner_standing = Standing.objects.get(tournament=tournament, team=winner_team)
            winner_standing.wins += 1
            winner_standing.points += 3 # 勝者得 3 分
            winner_standing.save()

            loser_standing = Standing.objects.get(tournament=tournament, team=loser_team)
            loser_standing.losses += 1
            loser_standing.save()

        # (可選) 處理平局的邏輯
        # elif match.team1_score == match.team2_score:
        #     ...

@receiver(post_save, sender=Match)
def update_standings_on_match_save(sender, instance, **kwargs):
    """
    當一場比賽被儲存後，觸發完整的積分榜重新計算。
    """
    # 只在比賽狀態為「已結束」時才觸發
    if instance.status == 'completed':
        recalculate_standings(instance.tournament.id)