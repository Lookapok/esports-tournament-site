# tournaments/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tournament, Team, Match, PlayerMatchStat
from .serializers import TournamentSerializer, TeamSerializer, MatchSerializer, PlayerMatchStatSerializer

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

class MatchStatsAPI(APIView):
    def post(self, request, pk):
        try:
            match = Match.objects.get(pk=pk)
        except Match.DoesNotExist:
            return Response({"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

        stats_data = request.data
        if not isinstance(stats_data, list):
            return Response({"error": "Request data must be a list of stats."}, status=status.HTTP_400_BAD_REQUEST)

        # 為每一筆傳來的數據，都加上 match 的 id
        for stat in stats_data:
            stat['match'] = match.id

        serializer = PlayerMatchStatSerializer(data=stats_data, many=True)
        if serializer.is_valid():
            # 先刪除這場比賽可能已存在的舊數據，避免重複寫入
            PlayerMatchStat.objects.filter(match=match).delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)