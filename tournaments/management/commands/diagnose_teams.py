#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnose team_list view issues
"""

from django.core.management.base import BaseCommand
from tournaments.models import Team, Player

class Command(BaseCommand):
    help = 'Diagnose team_list view issues'

    def handle(self, *args, **options):
        try:
            self.stdout.write("=" * 50)
            self.stdout.write("🔍 DIAGNOSING TEAM_LIST VIEW ISSUES")
            self.stdout.write("=" * 50)
            
            # Test basic Team query
            self.stdout.write("\n📊 Testing basic Team.objects.all()...")
            try:
                teams = Team.objects.all()
                self.stdout.write(f"✅ Found {teams.count()} teams")
                
                # Show first few teams
                for i, team in enumerate(teams[:5]):
                    self.stdout.write(f"  Team {i+1}: {team.name}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Basic Team query failed: {e}")
                return
            
            # Test Team query with school field
            self.stdout.write("\n📊 Testing Team.objects.only() with school field...")
            try:
                teams = Team.objects.only('id', 'name', 'school', 'logo')
                for i, team in enumerate(teams[:3]):
                    self.stdout.write(f"  Team {i+1}: {team.name} (school: {getattr(team, 'school', 'NO_FIELD')})")
                    
            except Exception as e:
                self.stdout.write(f"❌ Team query with school field failed: {e}")
                self.stdout.write("   This suggests the 'school' field doesn't exist in production DB")
            
            # Test prefetch_related with players
            self.stdout.write("\n📊 Testing prefetch_related with players...")
            try:
                teams = Team.objects.prefetch_related('players').only('id', 'name', 'logo')
                for i, team in enumerate(teams[:3]):
                    player_count = team.players.count()
                    self.stdout.write(f"  Team {i+1}: {team.name} ({player_count} players)")
                    
            except Exception as e:
                self.stdout.write(f"❌ Prefetch players failed: {e}")
            
            # Test the exact query from team_list view
            self.stdout.write("\n📊 Testing exact team_list view query...")
            try:
                from django.db.models import Prefetch
                teams = Team.objects.prefetch_related(
                    Prefetch('players', queryset=Player.objects.only('id', 'nickname', 'role'))
                ).only('id', 'name', 'logo').order_by('name')
                
                self.stdout.write(f"✅ Team_list query successful: {teams.count()} teams")
                
            except Exception as e:
                self.stdout.write(f"❌ Team_list view query failed: {e}")
                self.stdout.write("   This is the exact error causing the 500 error!")
            
            # Test simpler query without problematic fields
            self.stdout.write("\n📊 Testing simplified query...")
            try:
                teams = Team.objects.all().order_by('name')
                self.stdout.write(f"✅ Simplified query successful: {teams.count()} teams")
                
                # Show sample team data
                if teams.exists():
                    sample_team = teams.first()
                    self.stdout.write(f"   Sample team: {sample_team.name}")
                    self.stdout.write(f"   Team fields: {[f.name for f in sample_team._meta.fields]}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Even simplified query failed: {e}")
            
            self.stdout.write("=" * 50)
            
        except Exception as e:
            self.stdout.write(f"❌ Fatal error in diagnosis: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
