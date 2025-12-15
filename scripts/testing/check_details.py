#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查分組和比賽的詳細信息
"""

import requests

def check_tournament_details():
    """檢查錦標賽的詳細信息"""
    
    print("🔍 檢查錦標賽詳細信息...")
    
    # 創建一個 API 端點來獲取詳細信息
    api_script = '''
from tournaments.models import Tournament, Team, Group, Match, Standing
import json

tournament = Tournament.objects.first()
if tournament:
    data = {
        "tournament_name": tournament.name,
        "tournament_format": tournament.format,
        "groups": [],
        "total_matches": Match.objects.filter(tournament=tournament).count(),
        "total_standings": Standing.objects.filter(tournament=tournament).count()
    }
    
    for group in tournament.groups.order_by("name"):
        group_teams = list(group.teams.values("id", "name"))
        group_matches = Match.objects.filter(
            tournament=tournament,
            team1__in=group.teams.all(),
            team2__in=group.teams.all()
        ).count()
        
        data["groups"].append({
            "name": group.name,
            "team_count": group.teams.count(),
            "teams": [team["name"] for team in group_teams],
            "matches_count": group_matches
        })
    
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("No tournament found")
'''
    
    # 我們需要直接在雲端執行這個腳本
    print("需要在雲端環境檢查詳細信息...")
    print("請稍後，正在分析問題...")

if __name__ == "__main__":
    check_tournament_details()
