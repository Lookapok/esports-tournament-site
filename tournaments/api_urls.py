# tournaments/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    # API 根路徑 - 顯示可用的 API 端點
    path('', api_views.APIRootView.as_view(), name='api_root'),
    
    # 具體的 API 端點
    path('tournaments/', api_views.TournamentListAPI.as_view(), name='api_tournament_list'),
    path('teams/', api_views.TeamListAPI.as_view(), name='api_team_list'),
    path('players/', api_views.PlayerListAPI.as_view(), name='api_player_list'),
    path('matches/<int:pk>/', api_views.MatchDetailAPI.as_view(), name='api_match_detail'),
    path('matches/<int:pk>/stats/', api_views.GameReportAPIView.as_view(), name='api_match_stats'),
]