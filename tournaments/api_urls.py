# tournaments/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('tournaments/', api_views.TournamentListAPI.as_view(), name='api_tournament_list'),
    path('teams/', api_views.TeamListAPI.as_view(), name='api_team_list'),
    path('matches/<int:pk>/', api_views.MatchDetailAPI.as_view(), name='api_match_detail'),
    path('matches/<int:pk>/stats/', api_views.MatchStatsAPI.as_view(), name='api_match_stats'),
]