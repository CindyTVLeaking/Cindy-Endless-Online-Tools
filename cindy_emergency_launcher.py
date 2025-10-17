"""
Emergency launcher for Project Cindy
Uses the working launcher.py instead of broken bot_ui.py
"""

import sys
import subprocess

print("\n" + "="*60)
print("PROJECT CINDY - EMERGENCY LAUNCHER")
print("="*60)
print("\nDetected corrupted bot_ui.py file.")
print("Using launcher.py instead...")
print("="*60 + "\n")

try:
    # Run the working launcher
    subprocess.run([sys.executable, "launcher.py"])
except FileNotFoundError:
    print("ERROR: launcher.py not found!")
    print("\nPlease run one of these instead:")
    print("  python launcher.py")
    print("  python start-bot.bat")
    print("  python run_cindy.py")
except Exception as e:
    print(f"ERROR: {e}")
    input("\nPress Enter to exit...")
