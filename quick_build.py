"""
Quick Build Script - Project Cindy
Simple one-command build to .exe

Usage: python quick_build.py
"""

import os
import sys

def main():
    print("?? QUICK BUILD - PROJECT CINDY")
    print("="*50)
    
    # Check PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("\n?? Installing PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
    
    print("\n???  Building ProjectCindy.exe...")
    print("   (This takes 2-3 minutes)")
    
    # Simple build command
    cmd = f"pyinstaller --onefile --windowed --name=ProjectCindy run_cindy.py"
    
    result = os.system(cmd)
    
    if result == 0:
        print("\n? BUILD SUCCESS!")
        print("\n?? Location: dist/ProjectCindy.exe")
        print("\n?? Test it:")
        print("   cd dist")
        print("   .\\ProjectCindy.exe")
    else:
        print("\n? Build failed!")
        print("   Try: python build_cindy.py (for detailed build)")

if __name__ == "__main__":
    main()
