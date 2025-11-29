#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual trigger for player stats generation
"""

import requests
import json

def trigger_manual_generation():
    """Manually trigger player stats generation via health endpoint"""
    
    # First, check current health
    print("🔍 Checking current health status...")
    health_url = "https://winnertakesall-tw.onrender.com/health/"
    
    try:
        response = requests.get(health_url)
        if response.status_code == 200:
            health_data = response.json()
            print(f"📊 Current stats count: {health_data.get('playergamestat_count', 0)}")
            print(f"🎮 Games count: {health_data.get('game_count', 0)}")
            
            if health_data.get('playergamestat_count', 0) == 0:
                print("🎯 PlayerGameStat is empty, attempting manual generation...")
                
                # We'll use a simple approach - create a management URL
                # Let's try to trigger it via the admin interface or create our own endpoint
                
                print("💡 Solution: We need to create PlayerGameStat data manually")
                print("📝 Here's what we found:")
                print(f"  - Tournament count: {health_data.get('tournament_count', 0)}")
                print(f"  - Team count: {health_data.get('team_count', 0)}")  
                print(f"  - Player count: {health_data.get('player_count', 0)}")
                print(f"  - Game count: {health_data.get('game_count', 0)}")
                print(f"  - PlayerGameStat count: {health_data.get('playergamestat_count', 0)}")
                
                print("\n🔧 The issue is clear: We have games but no player statistics!")
                print("🎲 We need to generate sample PlayerGameStat records for existing games.")
                
            else:
                print("✅ PlayerGameStat data already exists!")
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking health: {e}")

if __name__ == "__main__":
    trigger_manual_generation()
