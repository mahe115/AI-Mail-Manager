#!/usr/bin/env python3
"""
AI Communication Assistant - Frontend Launcher
Simple launcher script for the unified dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    print("🚀 Starting AI Communication Assistant...")
    print("📧 Unified Dashboard with Modern UI")
    print("=" * 50)
    
    # Change to frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Communication Assistant...")
        sys.exit(0)

if __name__ == "__main__":
    main()
