#!/usr/bin/env python3
"""
Streamlit Photo Assistant Launcher

Simple launcher script to run the Streamlit Photo Assistant application.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    try:
        # Get the path to the Streamlit app
        app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
        
        if not app_path.exists():
            print(f"Error: Streamlit app not found at {app_path}")
            sys.exit(1)
        
        # Set environment variables for better Streamlit experience
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = '8501'
        env['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        print("🚀 Starting Photo Assistant Streamlit App...")
        print("📱 The app will be available at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 50)
        
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ], env=env)
        
    except KeyboardInterrupt:
        print("\n👋 Photo Assistant stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 