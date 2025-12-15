#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct force reimport script that can be run in production
"""

import os
import sys
import django

# Setup environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

# Now import after django setup
from tournaments.management.commands.force_reimport import Command

if __name__ == "__main__":
    print("=== Starting Force Reimport ===")
    command = Command()
    command.handle()
    print("=== Force Reimport Completed ===")
