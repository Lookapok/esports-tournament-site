#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic management command to check database status
"""

import os
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Diagnose database connection and configuration'

    def handle(self, *args, **options):
        try:
            self.stdout.write("🔍 Database Diagnostic Report")
            self.stdout.write("=" * 50)
            
            # Check environment
            database_url = os.environ.get('DATABASE_URL', 'Not set')
            self.stdout.write(f"📊 DATABASE_URL: {database_url[:50]}...")
            
            # Test connection
            self.stdout.write("\n🔗 Testing connection...")
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            self.stdout.write(f"✅ PostgreSQL: {version[0][:50]}...")
            
            # Check tables
            self.stdout.write("\n📋 Checking tables...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_name LIKE 'tournaments_%'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            self.stdout.write(f"📊 Found {len(tables)} tournament tables:")
            for table in tables[:5]:  # Show first 5
                self.stdout.write(f"  ✅ {table[0]}")
            
            # Check data
            self.stdout.write("\n📈 Checking data...")
            from tournaments.models import Tournament, Team, Player
            
            counts = {
                'tournaments': Tournament.objects.count(),
                'teams': Team.objects.count(),
                'players': Player.objects.count(),
            }
            
            for model, count in counts.items():
                self.stdout.write(f"  📊 {model}: {count}")
            
            # Check file existence
            self.stdout.write("\n📁 Checking data file...")
            if os.path.exists('production_data.json'):
                import json
                with open('production_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.stdout.write(f"  ✅ production_data.json found")
                self.stdout.write(f"  📊 Contains {len(data.get('teams', []))} teams")
            else:
                self.stdout.write(f"  ❌ production_data.json not found")
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("✅ Diagnostic completed")
            
        except Exception as e:
            self.stdout.write(f"❌ Diagnostic failed: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
