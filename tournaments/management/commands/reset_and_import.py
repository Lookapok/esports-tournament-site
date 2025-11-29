#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete database reset and Docker data import
"""

import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing

class Command(BaseCommand):
    help = 'Reset database and import Docker data'

    def handle(self, *args, **options):
        try:
            self.stdout.write("=" * 60)
            self.stdout.write("🗑️  COMPLETE DATABASE RESET & DOCKER IMPORT")
            self.stdout.write("=" * 60)
            
            # Step 1: Clear all data
            self.stdout.write("\n🧹 STEP 1: Clearing all existing data...")
            Standing.objects.all().delete()
            Game.objects.all().delete() 
            Match.objects.all().delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            Group.objects.all().delete()
            Tournament.objects.all().delete()
            self.stdout.write("✅ All data cleared!")
            
            # Step 2: Check production_data.json
            if not os.path.exists('production_data.json'):
                self.stdout.write(self.style.ERROR("❌ production_data.json not found!"))
                return
            
            # Step 3: Load Docker data
            self.stdout.write("\n📁 STEP 2: Loading Docker data...")
            with open('production_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Show data stats
            self.stdout.write("📊 Docker data contains:")
            for key in ['tournaments', 'teams', 'players', 'matches', 'games', 'groups', 'standings']:
                count = len(data.get(key, []))
                self.stdout.write(f"  - {key}: {count}")
            
            # Step 4: Import tournaments first
            self.stdout.write("\n🏆 STEP 3: Importing tournaments...")
            tournaments_imported = 0
            for item in data.get('tournaments', []):
                try:
                    # Parse dates
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
                    
                    Tournament.objects.create(
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
                    self.stdout.write(f"  ✅ Tournament: {item['name']}")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with tournament {item.get('name')}: {e}")
            
            # Step 5: Import teams (without school field for now)
            self.stdout.write(f"\n👥 STEP 4: Importing teams...")
            teams_imported = 0
            for i, item in enumerate(data.get('teams', [])):
                try:
                    # Extract school from team name
                    school = ''
                    if '-' in item['name']:
                        school = item['name'].split('-')[0].strip()
                    
                    # Create team without school field if it doesn't exist
                    team_data = {
                        'id': item['id'],
                        'name': item['name'],
                        'logo': item.get('logo', '')
                    }
                    
                    # Try to add school field if it exists
                    try:
                        team_data['school'] = school
                        team = Team.objects.create(**team_data)
                    except Exception:
                        # If school field doesn't exist, create without it
                        del team_data['school']
                        team = Team.objects.create(**team_data)
                    
                    teams_imported += 1
                    if i < 5:  # Show first 5
                        self.stdout.write(f"  ✅ Team: {item['name']}")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with team {item.get('name')}: {e}")
            
            self.stdout.write(f"👥 Teams imported: {teams_imported}")
            
            # Step 6: Import groups (without max_teams if it doesn't exist)
            self.stdout.write(f"\n🗂️  STEP 5: Importing groups...")
            groups_imported = 0
            for item in data.get('groups', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    
                    # Create group without max_teams field if it doesn't exist
                    group_data = {
                        'id': item['id'],
                        'tournament': tournament,
                        'name': item['name']
                    }
                    
                    # Try to add max_teams field if it exists
                    try:
                        group_data['max_teams'] = 8  # Default value
                        group = Group.objects.create(**group_data)
                    except Exception:
                        # If max_teams field doesn't exist, create without it
                        del group_data['max_teams']
                        group = Group.objects.create(**group_data)
                    
                    groups_imported += 1
                    self.stdout.write(f"  ✅ Group: {item['name']}")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ ERROR with group {item.get('name')}: {e}")
            
            self.stdout.write(f"🗂️  Groups imported: {groups_imported}")
            
            # Step 7: Import players
            self.stdout.write(f"\n🎮 STEP 6: Importing players...")
            players_imported = 0
            player_errors = 0
            for i, item in enumerate(data.get('players', [])):
                try:
                    team = Team.objects.get(id=item['team_id'])
                    Player.objects.create(
                        id=item['id'],
                        nickname=item['nickname'],
                        team=team,
                        role=item.get('role', 'Flex'),
                        avatar=item.get('avatar', '')
                    )
                    players_imported += 1
                    
                    if i % 50 == 0 and i > 0:
                        self.stdout.write(f"  📊 Progress: {players_imported} players...")
                    
                except Exception as e:
                    player_errors += 1
                    if player_errors <= 3:
                        self.stdout.write(f"  ❌ ERROR with player {item.get('nickname')}: {e}")
            
            self.stdout.write(f"🎮 Players imported: {players_imported} (errors: {player_errors})")
            
            # Step 8: Import matches
            self.stdout.write(f"\n⚽ STEP 7: Importing matches...")
            matches_imported = 0
            for item in data.get('matches', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team1 = None
                    team2 = None
                    winner = None
                    
                    # Handle null team IDs (bye matches)
                    if item.get('team1_id'):
                        team1 = Team.objects.get(id=item['team1_id'])
                    if item.get('team2_id'):
                        team2 = Team.objects.get(id=item['team2_id'])
                    if item.get('winner_id'):
                        winner = Team.objects.get(id=item['winner_id'])
                    
                    Match.objects.create(
                        id=item['id'],
                        tournament=tournament,
                        round_number=item.get('round_number', 1),
                        map=item.get('map', ''),  # Match model uses 'map' not 'map_name'
                        team1=team1,
                        team2=team2,
                        team1_score=item.get('team1_score', 0),
                        team2_score=item.get('team2_score', 0),
                        winner=winner,
                        match_time=item.get('match_time'),
                        status=item.get('status', 'scheduled'),
                        is_lower_bracket=item.get('is_lower_bracket', False)
                    )
                    matches_imported += 1
                    
                    if matches_imported <= 5:
                        team1_name = team1.name if team1 else "TBD"
                        team2_name = team2.name if team2 else "TBD" 
                        self.stdout.write(f"  ✅ Match: {team1_name} vs {team2_name}")
                    
                except Exception as e:
                    if matches_imported <= 3:
                        self.stdout.write(f"  ❌ ERROR with match {item.get('id')}: {e}")
            
            self.stdout.write(f"⚽ Matches imported: {matches_imported}")
            
            # Step 9: Import games
            self.stdout.write(f"\n🎮 STEP 8: Importing games...")
            games_imported = 0
            for item in data.get('games', []):
                try:
                    match = Match.objects.get(id=item['match_id'])
                    winner = None
                    if item.get('winner_id'):
                        winner = Team.objects.get(id=item['winner_id'])
                    
                    Game.objects.create(
                        id=item['id'],
                        match=match,
                        map_number=item.get('map_number', 1),
                        map_name=item.get('map_name', 'Unknown'),
                        team1_score=item.get('team1_score', 0),
                        team2_score=item.get('team2_score', 0),
                        winner=winner
                    )
                    games_imported += 1
                    
                    if games_imported <= 5:
                        self.stdout.write(f"  ✅ Game {item['map_number']}: {item.get('map_name', 'Unknown')}")
                    
                except Exception as e:
                    if games_imported <= 3:
                        self.stdout.write(f"  ❌ ERROR with game {item.get('id')}: {e}")
            
            self.stdout.write(f"🎮 Games imported: {games_imported}")
            
            # Step 10: Import standings
            self.stdout.write(f"\n🏆 STEP 9: Importing standings...")
            standings_imported = 0
            for item in data.get('standings', []):
                try:
                    tournament = Tournament.objects.get(id=item['tournament_id'])
                    team = Team.objects.get(id=item['team_id'])
                    group = None
                    if item.get('group_id'):
                        group = Group.objects.get(id=item['group_id'])
                    
                    Standing.objects.create(
                        id=item['id'],
                        tournament=tournament,
                        team=team,
                        group=group,
                        wins=item.get('wins', 0),
                        losses=item.get('losses', 0),
                        draws=item.get('draws', 0),
                        points=item.get('points', 0)
                    )
                    standings_imported += 1
                    
                    if standings_imported <= 5:
                        self.stdout.write(f"  ✅ Standing: {team.name} - {item.get('points', 0)} pts")
                    
                except Exception as e:
                    if standings_imported <= 3:
                        self.stdout.write(f"  ❌ ERROR with standing {item.get('id')}: {e}")
            
            self.stdout.write(f"🏆 Standings imported: {standings_imported}")
            
            # Final status
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("📊 FINAL DATABASE STATUS:")
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
                if count > 0:
                    self.stdout.write(f"  ✅ {key}: {count}")
                else:
                    self.stdout.write(f"  ⚪ {key}: {count}")
            
            self.stdout.write("=" * 60)
            if tournaments_imported > 0 and teams_imported > 0:
                self.stdout.write("🎉 SUCCESS: Docker data imported successfully!")
            else:
                self.stdout.write("⚠️  WARNING: Some data may not have imported correctly")
            
        except Exception as e:
            self.stdout.write(f"❌ Fatal error: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
