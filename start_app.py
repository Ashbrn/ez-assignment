#!/usr/bin/env python3
"""
Simple startup script for the Smart Assistant app
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Smart Assistant for Research Summarization")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir("d:/ez assignment")
    
    try:
        # Start Streamlit
        print("📱 Launching Streamlit app...")
        print("🌐 The app will open at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 50)
        
        # Run streamlit with proper configuration
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Try running: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()