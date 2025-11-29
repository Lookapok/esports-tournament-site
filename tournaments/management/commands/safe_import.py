#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Safe step-by-step import without transactions to identify exact error points
"""

import json
import os
from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing

class Command(BaseCommand):
    help = 'Safe step-by-step import from production_data.json'

    def handle(self, *args, **options):
        try:
            self.stdout.write("=" * 50)
            self.stdout.write("🚀 Starting SAFE step-by-step import...")
            
            # Check file exists
            if not os.path.exists('production_data.json'):
                self.stdout.write(self.style.ERROR("❌ production_data.json not found!"))
                return
            
            # Load data
            self.stdout.write("📁 Loading data file...")
            with open('production_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Show data stats
            self.stdout.write("📊 Data file contains:")
            for key in ['tournaments', 'teams', 'players', 'matches', 'games', 'groups', 'standings']:
                count = len(data.get(key, []))
                self.stdout.write(f"  - {key}: {count}")
            
            # Check current database state
            self.stdout.write("\n🗄️  Current database state:")
            current_counts = {
                'tournaments': Tournament.objects.count(),
                'teams': Team.objects.count(),
                'players': Player.objects.count(),
                'matches': Match.objects.count(),
                'games': Game.objects.count(),
                'groups': Group.objects.count(),
                'standings': Standing.objects.count(),
            }
            for key, count in current_counts.items():
                self.stdout.write(f"  - {key}: {count}")
            
            # STEP 1: Import tournaments (most critical)
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("🏆 STEP 1: Importing tournaments...")
            tournaments_imported = 0
            for item in data.get('tournaments', []):
                try:
                    # Parse dates carefully
                    start_date = None
                    if item.get('start_date'):
                        date_str = str(item['start_date']).replace('+00:00', '').replace('Z', '')
                        if 'T' in date_str:
                            start_date = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                        else:
                            start_date = date_str
                    
                    end_date = None
                    if item.get('end_date'):
                        date_str = str(item['end_date']).replace('+00:00', '').replace('Z', '')
                        if 'T' in date_str:
                            end_date = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                        else:
                            end_date = date_str
                    
                    # Try to create tournament
                    tournament = Tournament.objects.create(
                        id=item['id'],
                        name=item['name'],
                        game=item.get('game', 'Unknown'),
                        start_date=start_date,
                        end_date=end_date,
                        rules=item.get('rules', ''),
                        status=item.get('status', 'upcoming'),
                        format=item.get('format', 'single_elimination')
                    )
                    tournaments_imported += 1
                    self.stdout.write(f"  ✅ Created tournament: {item['name']}")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with tournament {item.get('name')}: {e}")
                    self.stdout.write(f"     Data: {item}")
            
            self.stdout.write(f"🏆 Tournaments imported: {tournaments_imported}")
            
            # STEP 2: Import teams
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("👥 STEP 2: Importing teams...")
            teams_imported = 0
            for i, item in enumerate(data.get('teams', [])):
                try:
                    # Extract school name from team name if needed
                    school = item.get('school', '')
                    if not school and '-' in item['name']:
                        # Try to extract school from name like "啟英高級中學-CYVS"
                        school = item['name'].split('-')[0].strip()
                    
                    team = Team.objects.create(
                        id=item['id'],
                        name=item['name'],
                        school=school,
                        logo=item.get('logo', '')
                    )
                    teams_imported += 1
                    
                    # Show progress for first few teams
                    if i < 5:
                        self.stdout.write(f"  ✅ Created team: {item['name']} (school: {school})")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with team {item.get('name')}: {e}")
                    if i < 5:  # Show details for first few errors
                        self.stdout.write(f"     Data: {item}")
            
            self.stdout.write(f"👥 Teams imported: {teams_imported}")
            
            # STEP 3: Import groups  
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("🗂️  STEP 3: Importing groups...")
            groups_imported = 0
            for item in data.get('groups', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    group = Group.objects.create(
                        id=item['id'],
                        tournament=tournament,
                        name=item['name'],
                        max_teams=item.get('max_teams', 8)
                    )
                    groups_imported += 1
                    self.stdout.write(f"  ✅ Created group: {item['name']}")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with group {item.get('name')}: {e}")
                    self.stdout.write(f"     Data: {item}")
            
            self.stdout.write(f"🗂️  Groups imported: {groups_imported}")
            
            # STEP 4: Import players
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("🎮 STEP 4: Importing players...")
            players_imported = 0
            player_errors = 0
            for i, item in enumerate(data.get('players', [])):
                try:
                    team = Team.objects.get(id=item['team_id'])
                    player = Player.objects.create(
                        id=item['id'],
                        nickname=item['nickname'],
                        team=team,
                        role=item.get('role', 'Flex'),
                        avatar=item.get('avatar', '')
                    )
                    players_imported += 1
                    
                    # Show progress every 50 players
                    if i % 50 == 0 and i > 0:
                        self.stdout.write(f"  📊 Progress: {players_imported} players imported...")
                    
                except Exception as e:
                    player_errors += 1
                    if player_errors <= 5:  # Show first 5 errors
                        self.stdout.write(f"  ❌ ERROR with player {item.get('nickname')}: {e}")
                        self.stdout.write(f"     Data: {item}")
            
            self.stdout.write(f"🎮 Players imported: {players_imported} (errors: {player_errors})")
            
            # FINAL STATUS CHECK
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("🔍 FINAL STATUS CHECK:")
            final_counts = {
                'tournaments': Tournament.objects.count(),
                'teams': Team.objects.count(),
                'players': Player.objects.count(),
                'matches': Match.objects.count(),
                'games': Game.objects.count(),
                'groups': Group.objects.count(),
                'standings': Standing.objects.count(),
            }
            
            for key, count in final_counts.items():
                change = count - current_counts[key]
                if change > 0:
                    self.stdout.write(f"  ✅ {key}: {count} (+{change})")
                else:
                    self.stdout.write(f"  ⚪ {key}: {count} (no change)")
            
            self.stdout.write("=" * 50)
            self.stdout.write("✅ Safe import completed!")
            
        except Exception as e:
            self.stdout.write(f"❌ Fatal error in safe import: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
