#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trigger generation of sample PlayerGameStat data
"""

import requests

def trigger_sample_stats():
    """Trigger sample stats generation via web hook"""
    url = "https://winnertakesall-tw.onrender.com/admin/generate-stats/"
    
    print("🎯 Triggering sample player stats generation...")
    
    try:
        response = requests.post(url, timeout=120)
        if response.status_code == 200:
            print("✅ Sample stats generation triggered successfully!")
            print("📊 Check health endpoint for results")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_sample_stats()
