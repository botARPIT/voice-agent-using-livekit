#!/usr/bin/env python3
"""
Entry point script for running the Real Estate Voice Agent.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_estate_agent.main import main

if __name__ == "__main__":
    main()
