#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standalone script to trigger force reimport via API
"""

import requests
import json

def trigger_force_import():
    try:
        print("Triggering force import on production server...")
        
        # Make a simple request to health endpoint first
        health_response = requests.get("https://winnertakesall-tw.onrender.com/health/")
        print(f"Health check status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health data: {health_response.json()}")
        
        # Note: We would need a custom endpoint to trigger the import
        # For now, we can only monitor the automatic import in build.sh
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_force_import()
