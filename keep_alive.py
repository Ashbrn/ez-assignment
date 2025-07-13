#!/usr/bin/env python3
"""
Keep the Streamlit app alive by monitoring and restarting if needed
"""

import subprocess
import time
import requests
import sys
import os

def is_app_running():
    """Check if the app is responding"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_app():
    """Start the Streamlit app"""
    print("🚀 Starting Streamlit app...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ], cwd="d:/ez assignment")

def main():
    print("🔄 Starting app monitor...")
    print("📱 App will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("-" * 50)
    
    process = None
    
    try:
        while True:
            if not is_app_running():
                if process:
                    print("⚠️  App stopped, restarting...")
                    process.terminate()
                    time.sleep(2)
                
                process = start_app()
                print("✅ App started")
                
                # Wait for app to be ready
                for i in range(30):  # Wait up to 30 seconds
                    if is_app_running():
                        print("🟢 App is responding")
                        break
                    time.sleep(1)
                else:
                    print("❌ App failed to start properly")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Stopping monitor...")
        if process:
            process.terminate()
        print("✅ Monitor stopped")

if __name__ == "__main__":
    main()