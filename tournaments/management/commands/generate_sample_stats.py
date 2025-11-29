#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate sample player game stats for existing games
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import Game, Player, Team, PlayerGameStat

class Command(BaseCommand):
    help = 'Generate sample player stats for existing games'

    def handle(self, *args, **options):
        try:
            self.stdout.write("=" * 50)
            self.stdout.write("🎯 GENERATING SAMPLE PLAYER STATS")
            self.stdout.write("=" * 50)
            
            # Check existing data
            game_count = Game.objects.count()
            stats_count = PlayerGameStat.objects.count()
            
            self.stdout.write(f"📊 Current status:")
            self.stdout.write(f"  - Games: {game_count}")
            self.stdout.write(f"  - Player stats: {stats_count}")
            
            if game_count == 0:
                self.stdout.write(self.style.ERROR("❌ No games found! Cannot generate stats."))
                return
            
            if stats_count > 0:
                self.stdout.write(self.style.WARNING("⚠️  Player stats already exist!"))
                confirm = input("Continue and add more stats? (y/N): ")
                if confirm.lower() != 'y':
                    return
            
            # Generate stats for each game
            self.stdout.write("\n🎮 Generating stats for games...")
            stats_created = 0
            
            with transaction.atomic():
                for game in Game.objects.select_related('match', 'match__team1', 'match__team2').all():
                    try:
                        # Get teams from this match
                        team1 = game.match.team1
                        team2 = game.match.team2
                        
                        if not team1 or not team2:
                            continue
                        
                        # Get players for each team
                        team1_players = list(Player.objects.filter(team=team1))
                        team2_players = list(Player.objects.filter(team=team2))
                        
                        # Generate stats for team1 players (random 3-5 players per team)
                        players_count1 = min(len(team1_players), random.randint(3, 5))
                        selected_players1 = random.sample(team1_players, players_count1)
                        
                        for player in selected_players1:
                            # Check if stat already exists
                            if not PlayerGameStat.objects.filter(game=game, player=player).exists():
                                kills = random.randint(5, 25)
                                deaths = random.randint(3, 20)
                                assists = random.randint(1, 15)
                                first_kills = random.randint(0, 3)
                                acs = round(random.uniform(120.0, 300.0), 1)
                                
                                PlayerGameStat.objects.create(
                                    game=game,
                                    player=player,
                                    team=team1,
                                    kills=kills,
                                    deaths=deaths,
                                    assists=assists,
                                    first_kills=first_kills,
                                    acs=acs
                                )
                                stats_created += 1
                        
                        # Generate stats for team2 players
                        players_count2 = min(len(team2_players), random.randint(3, 5))
                        selected_players2 = random.sample(team2_players, players_count2)
                        
                        for player in selected_players2:
                            # Check if stat already exists
                            if not PlayerGameStat.objects.filter(game=game, player=player).exists():
                                kills = random.randint(5, 25)
                                deaths = random.randint(3, 20)
                                assists = random.randint(1, 15)
                                first_kills = random.randint(0, 3)
                                acs = round(random.uniform(120.0, 300.0), 1)
                                
                                PlayerGameStat.objects.create(
                                    game=game,
                                    player=player,
                                    team=team2,
                                    kills=kills,
                                    deaths=deaths,
                                    assists=assists,
                                    first_kills=first_kills,
                                    acs=acs
                                )
                                stats_created += 1
                        
                        if stats_created % 50 == 0:
                            self.stdout.write(f"  📊 Progress: {stats_created} stats created...")
                    
                    except Exception as e:
                        self.stdout.write(f"  ❌ Error with game {game.id}: {e}")
            
            self.stdout.write(f"\n🎉 SUCCESS!")
            self.stdout.write(f"📊 Generated {stats_created} player stats")
            
            # Final verification
            final_stats_count = PlayerGameStat.objects.count()
            self.stdout.write(f"📈 Total player stats now: {final_stats_count}")
            
        except Exception as e:
            self.stdout.write(f"❌ Fatal error: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
