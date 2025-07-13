#!/usr/bin/env python3
"""
Script to stop any running Streamlit processes
"""

import subprocess
import sys
import os

def stop_streamlit():
    print("🛑 Stopping Streamlit processes...")
    
    try:
        # Kill processes using port 8501
        result = subprocess.run([
            "netstat", "-ano"
        ], capture_output=True, text=True)
        
        lines = result.stdout.split('\n')
        pids_to_kill = []
        
        for line in lines:
            if ':8501' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    pids_to_kill.append(pid)
        
        # Also find python processes running streamlit
        result2 = subprocess.run([
            "wmic", "process", "where", "name='python.exe'", "get", "processid,commandline", "/format:csv"
        ], capture_output=True, text=True)
        
        for line in result2.stdout.split('\n'):
            if 'streamlit' in line.lower() and 'app.py' in line.lower():
                parts = line.split(',')
                if len(parts) > 2:
                    pid = parts[-1].strip()
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Remove duplicates
        pids_to_kill = list(set(pids_to_kill))
        
        if pids_to_kill:
            for pid in pids_to_kill:
                try:
                    subprocess.run(["taskkill", "/F", "/PID", pid], check=True, capture_output=True)
                    print(f"✅ Stopped process {pid}")
                except subprocess.CalledProcessError:
                    print(f"❌ Could not stop process {pid}")
        else:
            print("ℹ️  No Streamlit processes found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 You can manually stop the app by pressing Ctrl+C in the terminal")

if __name__ == "__main__":
    stop_streamlit()