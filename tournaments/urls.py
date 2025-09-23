# tournaments/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 主要頁面
    path('', views.tournament_list, name='tournament_list'),
    path('tournaments/<int:pk>/', views.tournament_detail, name='tournament_detail'), # 網址用複數 tournaments 較符合慣例
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'), # 網址用複數 teams 較符合慣例
    path('players/<int:pk>/', views.player_detail, name='player_detail'), # 網址用複數 players 較符合慣例

    # 數據統計頁面
    path('tournaments/<int:pk>/stats/', views.tournament_stats, name='tournament_stats'),
    path('stats/', views.overall_stats, name='overall_stats'),

    # 使用者系統
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # 賽事建立精靈
    path('tournaments/create/step1/', views.tournament_create_step1, name='tournament_create_step1'),
    path('tournaments/create/step2/', views.tournament_create_step2, name='tournament_create_step2'),
    path('tournaments/create/step3/', views.tournament_create_step3, name='tournament_create_step3'),
]