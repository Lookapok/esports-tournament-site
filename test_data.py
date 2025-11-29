#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

try:
    with open('production_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"JSON格式正確:")
    print(f"  tournaments: {len(data.get('tournaments', []))}")
    print(f"  teams: {len(data.get('teams', []))}")
    print(f"  players: {len(data.get('players', []))}")
    print(f"  matches: {len(data.get('matches', []))}")
    print(f"  games: {len(data.get('games', []))}")
    print(f"  groups: {len(data.get('groups', []))}")
    print(f"  standings: {len(data.get('standings', []))}")
    
    # Check first team
    if data.get('teams'):
        first_team = data['teams'][0]
        print(f"\nFirst team structure:")
        for key, value in first_team.items():
            print(f"  {key}: {value}")
        
    # Check if teams have school field
    teams_with_school = [team for team in data.get('teams', []) if 'school' in team]
    print(f"\nTeams with school field: {len(teams_with_school)}")
    
except Exception as e:
    print(f"Error: {e}")
