"""
Complete restart script - clears everything and tests fresh
"""
import os
import sys
import subprocess

def restart_python_process():
    """Restart the Python process to clear all caches"""
    print("🔄 Restarting Python process to clear all caches...")
    
    # Get the current script arguments
    args = [sys.executable] + ['debug_email_fresh.py']
    
    # Execute the fresh debug script in a new process
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error restarting process: {e}")
        return False

if __name__ == "__main__":
    restart_python_process()
