# tournaments/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from rest_framework import status
from .models import Tournament, Team, Match, Game, PlayerGameStat, Player
from .serializers import TournamentSerializer, TeamSerializer, MatchSerializer, PlayerGameStatSerializer
from django.db import transaction
import logging

# 取得 API 專用的日誌記錄器
api_logger = logging.getLogger('tournaments.api')

class TournamentListAPI(APIView):
    def get(self, request):
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TournamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamListAPI(APIView):
    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatchDetailAPI(APIView):
    def patch(self, request, pk):
        try:
            match = Match.objects.get(pk=pk)
        except Match.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MatchSerializer(match, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GameReportAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        # 記錄遊戲結果報告開始
        api_logger.info('Game Report Started', extra={
            'event_type': 'game_report_start',
            'match_id': pk,
            'data_size': len(str(request.data)) if request.data else 0,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        })
        
        try:
            match = Match.objects.get(pk=pk)
        except Match.DoesNotExist:
            api_logger.error('Match Not Found', extra={
                'event_type': 'match_not_found',
                'match_id': pk,
            })
            return Response({"error": f"Match with id {pk} not found."}, status=404)

        data = request.data
        if not isinstance(data, dict) or "player_stats" not in data:
            return Response({"error": "Invalid data format."}, status=400)

        player_stats_list = data.get("player_stats", [])
                # --- [新增這三行來檢查數據] ---
        print("--- Received Player Stats List from Bot ---")
        print(player_stats_list)
        print("-----------------------------------------")
        # ------------------------------------
        map_num = data.get("map_number", 1)
        map_name = data.get("map_name")
        final_score_str = data.get("final_score", "0-0")
        winning_team_name = data.get("winning_team_name")

        created_stats, errors = [], []

        try:
            final_score = final_score_str.replace(':', '-').split('-') if final_score_str else ["0", "0"]
            team1_score = int(final_score[0]) if len(final_score) > 0 else 0
            team2_score = int(final_score[1]) if len(final_score) > 1 else 0

            with transaction.atomic():
                game, created = Game.objects.get_or_create(match=match, map_number=map_num)
                game.map_name = map_name
                game.team1_score = team1_score
                game.team2_score = team2_score

            # --- [關鍵修改] 新增防禦性檢查 ---
                game.winner = None 
            # 只有在 match.team1 和 match.team2 都存在時，才進行名稱比對
                if winning_team_name and match.team1 and match.team2:
                    if winning_team_name.strip().lower() == match.team1.name.strip().lower():
                        game.winner = match.team1
                    elif winning_team_name.strip().lower() == match.team2.name.strip().lower():
                        game.winner = match.team2
            # ------------------------------------

                game.save()

                for player_data in player_stats_list:
                    nickname = player_data.get('nickname')
                    if not nickname: continue
                    try:
                    # [關鍵修改] 查詢選手時，也檢查隊伍是否存在
                        if not match.team1 or not match.team2:
                        # 如果比賽隊伍未定，我們就放寬選手的查詢範圍
                            player = Player.objects.get(nickname__iexact=nickname)
                        else:
                            player = Player.objects.get(nickname__iexact=nickname, team__in=[match.team1, match.team2])

                        stat_obj, created = PlayerGameStat.objects.update_or_create(
                            game=game, player=player,
                            defaults={
                                'team': player.team,
                                'kills': player_data.get('kills', 0),
                                'deaths': player_data.get('deaths', 0),
                                'assists': player_data.get('assists', 0),
                                'first_kills': player_data.get('first_kills', 0),
                                'acs': player_data.get('acs', 0.0),
                        }
                    )
                        created_stats.append({"player_nickname": player.nickname})
                    except Player.DoesNotExist:
                        errors.append({"nickname": nickname, "error": "Player not found for this match."})

            if errors:
                api_logger.warning('Game Report Completed with Errors', extra={
                    'event_type': 'game_report_partial_success',
                    'match_id': pk,
                    'success_count': len(created_stats),
                    'error_count': len(errors),
                    'errors': errors,
                })
                return Response({"status": "Completed with errors", "success_data": created_stats, "errors": errors}, status=207)

            api_logger.info('Game Report Completed Successfully', extra={
                'event_type': 'game_report_success',
                'match_id': pk,
                'stats_created': len(created_stats),
                'map_name': map_name,
                'final_score': final_score_str,
                'winning_team': winning_team_name,
            })
            return Response({"status": "success", "data": created_stats}, status=201)

        except Exception as e:
            # 如果 DEBUG=True，這裡的錯誤會顯示在終端機
            print(f"!!! AN UNEXPECTED ERROR OCCURRED: {e}, TYPE: {type(e)} !!!")
            api_logger.error('Game Report Exception', extra={
                'event_type': 'game_report_exception',
                'match_id': pk,
                'exception_type': type(e).__name__,
                'exception_message': str(e),
            })
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)