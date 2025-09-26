# tournaments/serializers.py
from rest_framework import serializers
from .models import Tournament, Team, Match, Game, PlayerGameStat

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'logo']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__' # 允許所有欄位

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        # 只允許更新這幾個欄位
        fields = ['team1_score', 'team2_score', 'winner', 'status']

class PlayerGameStatSerializer(serializers.ModelSerializer): # <--- 類別名稱也要改
    class Meta:
        model = PlayerGameStat # <--- 在這裡更新模型名稱
        fields = '__all__'