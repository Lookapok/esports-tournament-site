#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified force import with maximum error handling
"""

import os
import sys
import json
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.db import transaction
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing

def safe_import():
    print("🚀 Starting simplified force import...")
    
    try:
        # Check if file exists
        if not os.path.exists('production_data.json'):
            print("❌ production_data.json not found!")
            return False
            
        # Load data
        with open('production_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Data loaded: {len(data.get('teams', []))} teams, {len(data.get('players', []))} players")
        
        # Clear and import in transaction
        with transaction.atomic():
            print("🧹 Clearing existing data...")
            Standing.objects.all().delete()
            Game.objects.all().delete() 
            Match.objects.all().delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            Group.objects.all().delete()
            Tournament.objects.all().delete()
            
            # Import tournaments first
            print("📊 Importing tournaments...")
            for item in data.get('tournaments', []):
                Tournament.objects.create(
                    id=item['id'],
                    name=item['name'],
                    game=item['game'],
                    start_date=item.get('start_date'),
                    end_date=item.get('end_date'),
                    rules=item.get('rules', ''),
                    status=item.get('status', 'upcoming'),
                    format=item.get('format', 'round_robin')
                )
            print(f"✅ {Tournament.objects.count()} tournaments imported")
            
            # Import teams
            print("🏆 Importing teams...")
            for item in data.get('teams', []):
                Team.objects.create(
                    id=item['id'],
                    name=item['name'],
                    school=item.get('school', ''),  # Default empty string if no school
                    logo=item.get('logo', '')
                )
            print(f"✅ {Team.objects.count()} teams imported")
            
            # Import groups
            print("📋 Importing groups...")
            for item in data.get('groups', []):
                tournament = Tournament.objects.get(id=item['tournament_id'])
                Group.objects.create(
                    id=item['id'],
                    tournament=tournament,
                    name=item['name'],
                    max_teams=item.get('max_teams', 8)  # Default 8 if no max_teams
                )
            print(f"✅ {Group.objects.count()} groups imported")
            
            print("🎯 Import completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    safe_import()
