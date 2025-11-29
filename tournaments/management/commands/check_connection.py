#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database connection diagnosis and fix script
"""

import os
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Diagnose database connection issues'

    def handle(self, *args, **options):
        try:
            self.stdout.write("=" * 60)
            self.stdout.write("🔍 DATABASE CONNECTION DIAGNOSIS")
            self.stdout.write("=" * 60)
            
            # Check DATABASE_URL
            database_url = os.environ.get('DATABASE_URL', 'Not set')
            self.stdout.write(f"\n📡 DATABASE_URL:")
            self.stdout.write(f"  {database_url}")
            
            # Analyze URL
            if 'supabase.co' in database_url:
                self.stdout.write(f"\n✅ Supabase connection detected")
                
                if ':5432' in database_url and '.pooler.' not in database_url:
                    self.stdout.write(f"⚠️  WARNING: Using direct connection (port 5432)")
                    self.stdout.write(f"   This may cause IPv4 compatibility issues!")
                    
                    # Suggest pooler URL
                    if 'db.' in database_url:
                        suggested_url = database_url.replace('db.', 'db.').replace(':5432', ':6543')
                        if '.supabase.co' in suggested_url:
                            suggested_url = suggested_url.replace('.supabase.co', '.pooler.supabase.com')
                        self.stdout.write(f"\n💡 SUGGESTED SESSION POOLER URL:")
                        self.stdout.write(f"  {suggested_url}")
                        self.stdout.write(f"\n🔧 TO FIX:")
                        self.stdout.write(f"  1. Go to Render Dashboard → Your Service → Environment")
                        self.stdout.write(f"  2. Update DATABASE_URL to the suggested URL above")
                        self.stdout.write(f"  3. Deploy again")
                
                elif '.pooler.' in database_url and ':6543' in database_url:
                    self.stdout.write(f"✅ Using Session Pooler - Good!")
                    
            else:
                self.stdout.write(f"❓ Non-Supabase connection")
            
            # Test actual connection
            self.stdout.write(f"\n🔌 Testing database connection...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        self.stdout.write(f"✅ Database connection successful!")
                        
                        # Get connection info
                        cursor.execute("SELECT version()")
                        version = cursor.fetchone()[0]
                        self.stdout.write(f"📊 Database version: {version}")
                        
                        # Get current connection info
                        cursor.execute("SELECT inet_server_addr(), inet_server_port()")
                        server_info = cursor.fetchone()
                        self.stdout.write(f"🌐 Server: {server_info[0]}:{server_info[1]}")
                        
            except Exception as e:
                self.stdout.write(f"❌ Database connection failed: {e}")
                self.stdout.write(f"   This confirms the IPv4/pooler issue!")
            
            self.stdout.write("=" * 60)
            
        except Exception as e:
            self.stdout.write(f"❌ Error in diagnosis: {e}")
