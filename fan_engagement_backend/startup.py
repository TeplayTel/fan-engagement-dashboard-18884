#!/usr/bin/env python3
"""
Startup script for Fan Engagement Backend.
Initializes database tables and default data.
"""

import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.init_db import init_database

if __name__ == "__main__":
    print("Starting Fan Engagement Backend initialization...")
    init_database()
    print("Initialization completed successfully!")
