#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Force re-import all data from production_data.json
"""

import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing

class Command(BaseCommand):
    help = 'Force re-import all data from production_data.json'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Starting force re-import...")
            
            # Check if production_data.json exists
            if not os.path.exists('production_data.json'):
                self.stdout.write(self.style.ERROR("ERROR: production_data.json not found!"))
                return
            
            # Load data
            self.stdout.write("Loading data file...")
            with open('production_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Show data stats
            self.stdout.write(f"Data in file:")
            self.stdout.write(f"  - Tournaments: {len(data.get('tournaments', []))}")
            self.stdout.write(f"  - Teams: {len(data.get('teams', []))}")
            self.stdout.write(f"  - Players: {len(data.get('players', []))}")
            self.stdout.write(f"  - Matches: {len(data.get('matches', []))}")
            self.stdout.write(f"  - Games: {len(data.get('games', []))}")
            self.stdout.write(f"  - Groups: {len(data.get('groups', []))}")
            self.stdout.write(f"  - Standings: {len(data.get('standings', []))}")
            
            # Check current database state
            self.stdout.write("Current database state:")
            self.stdout.write(f"  - Tournaments: {Tournament.objects.count()}")
            self.stdout.write(f"  - Teams: {Team.objects.count()}")
            self.stdout.write(f"  - Players: {Player.objects.count()}")
            self.stdout.write(f"  - Matches: {Match.objects.count()}")
            self.stdout.write(f"  - Games: {Game.objects.count()}")
            self.stdout.write(f"  - Groups: {Group.objects.count()}")
            self.stdout.write(f"  - Standings: {Standing.objects.count()}")
            
            # Clear all data and re-import
            with transaction.atomic():
                self.stdout.write("Clearing all existing data...")
                Standing.objects.all().delete()
                Game.objects.all().delete()
                Match.objects.all().delete()
                Player.objects.all().delete()
                Team.objects.all().delete()
                Group.objects.all().delete()
                Tournament.objects.all().delete()
                
                self.stdout.write("Starting full re-import...")
                
                # 1. Import tournaments
                tournaments_imported = 0
                for item in data.get('tournaments', []):
                    try:
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
                            game=item.get('game', ''),
                            start_date=start_date,
                            end_date=end_date,
                            rules=item.get('rules', ''),
                            status=item.get('status', 'upcoming'),
                            format=item.get('format', 'single_elimination')
                        )
                        tournaments_imported += 1
                        self.stdout.write(f"  Created tournament: {item['name']}")
                    except Exception as e:
                        self.stdout.write(f"  ERROR importing tournament {item.get('name')}: {e}")
                self.stdout.write(f"Tournaments imported: {tournaments_imported}")
                
                # 2. Import teams
                teams_imported = 0
                for item in data.get('teams', []):
                    try:
                        Team.objects.create(
                            id=item['id'],
                            name=item['name'],
                            school=item.get('school', ''),
                            logo=item.get('logo', '')
                        )
                        teams_imported += 1
                        if teams_imported <= 5:  # Show first 5 teams
                            self.stdout.write(f"  Created team: {item['name']}")
                    except Exception as e:
                        self.stdout.write(f"  ERROR importing team {item.get('name')}: {e}")
                self.stdout.write(f"Teams imported: {teams_imported}")
                
                # 3. Import groups
                groups_imported = 0
                for item in data.get('groups', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        Group.objects.create(
                            id=item['id'],
                            tournament=tournament,
                            name=item['name'],
                            max_teams=item.get('max_teams', 8)
                        )
                        groups_imported += 1
                        self.stdout.write(f"  Created group: {item['name']}")
                    except Exception as e:
                        self.stdout.write(f"  ERROR importing group {item.get('name')}: {e}")
                self.stdout.write(f"Groups imported: {groups_imported}")
                
                # 4. Import players
                players_imported = 0
                for item in data.get('players', []):
                    try:
                        team = Team.objects.get(id=item['team_id'])
                        Player.objects.create(
                            id=item['id'],
                            name=item['name'],
                            team=team,
                            position=item.get('position', ''),
                            avatar=item.get('avatar', '')
                        )
                        players_imported += 1
                    except Exception as e:
                        if players_imported < 5:  # Show first few errors
                            self.stdout.write(f"  ERROR importing player {item.get('name')}: {e}")
                if players_imported <= 5:
                    self.stdout.write(f"  First 5 players imported successfully")
                self.stdout.write(f"Players imported: {players_imported}")
                
                # 5. Import matches
                matches_imported = 0
                for item in data.get('matches', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        team1 = Team.objects.get(id=item['team1_id'])
                        team2 = Team.objects.get(id=item['team2_id'])
                        winner = None
                        if item.get('winner_id'):
                            try:
                                winner = Team.objects.get(id=item['winner_id'])
                            except:
                                pass
                        
                        match_time = None
                        if item.get('match_time'):
                            date_str = str(item['match_time']).replace('+00:00', '').replace('Z', '')
                            if 'T' in date_str:
                                match_time = date_str.split('T')[0] + ' ' + date_str.split('T')[1]
                            else:
                                match_time = date_str
                        
                        Match.objects.create(
                            id=item['id'],
                            tournament=tournament,
                            round_number=item.get('round_number', 1),
                            map=item.get('map', ''),
                            team1=team1,
                            team2=team2,
                            team1_score=item.get('team1_score', 0),
                            team2_score=item.get('team2_score', 0),
                            winner=winner,
                            match_time=match_time,
                            status=item.get('status', 'scheduled'),
                            is_lower_bracket=item.get('is_lower_bracket', False)
                        )
                        matches_imported += 1
                    except Exception as e:
                        if matches_imported < 5:  # Show first few errors
                            self.stdout.write(f"  ERROR importing match {item.get('id')}: {e}")
                self.stdout.write(f"Matches imported: {matches_imported}")
                
                # 6. Import standings
                standings_imported = 0
                for item in data.get('standings', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        team = Team.objects.get(id=item['team_id'])
                        group = None
                        if item.get('group_id'):
                            try:
                                group = Group.objects.get(id=item['group_id'])
                            except:
                                pass
                        
                        standing, created = Standing.objects.get_or_create(
                            tournament=tournament,
                            team=team,
                            defaults={
                                'group': group,
                                'wins': item.get('wins', 0),
                                'losses': item.get('losses', 0),
                                'draws': item.get('draws', 0),
                                'points': item.get('points', 0)
                            }
                        )
                        if created:
                            standings_imported += 1
                    except Exception as e:
                        if standings_imported < 5:  # Show first few errors
                            self.stdout.write(f"  ERROR importing standing: {e}")
                self.stdout.write(f"Standings imported: {standings_imported}")
            
            # Final verification
            self.stdout.write(self.style.SUCCESS("\nForce re-import completed! Final verification:"))
            self.stdout.write(f"  - Tournaments: {Tournament.objects.count()}")
            self.stdout.write(f"  - Teams: {Team.objects.count()}")
            self.stdout.write(f"  - Players: {Player.objects.count()}")
            self.stdout.write(f"  - Matches: {Match.objects.count()}")
            self.stdout.write(f"  - Games: {Game.objects.count()}")
            self.stdout.write(f"  - Groups: {Group.objects.count()}")
            self.stdout.write(f"  - Standings: {Standing.objects.count()}")
            
            # Create migration marker
            with open('.migrated_from_docker', 'w') as f:
                f.write('completed')
            
            self.stdout.write(self.style.SUCCESS("\nForce re-import completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Force re-import failed: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
