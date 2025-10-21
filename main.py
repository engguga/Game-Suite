#!/usr/bin/env python3
"""
Game Suite - Main Entry Point
Professional Game Collection Platform
"""

import os
import sys
import traceback

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point"""
    try:
        from core.engine import GameEngine
        print("Initializing Game Suite...")
        
        engine = GameEngine()
        engine.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
