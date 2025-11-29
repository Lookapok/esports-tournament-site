#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trigger generation of sample PlayerGameStat data
"""

import requests

def trigger_sample_stats():
    """Trigger sample stats generation via API"""
    url = "https://winnertakesall-tw.onrender.com/api/generate-sample-stats/"
    
    print("🎯 Triggering sample player stats generation...")
    
    try:
        response = requests.post(url, timeout=180)
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📊 Generated: {result.get('stats_created', 0)} player stats")
            print(f"🎮 Games processed: {result.get('games_processed', 0)}")
            print(f"📈 Total stats now: {result.get('total_stats', 0)}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_sample_stats()
