"""
Project Cindy - Build to .exe
Complete build script for creating standalone executables

Author: Kuuna
Version: 1.0.0
"""

import os
import sys
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("? PyInstaller found!")
        return True
    except ImportError:
        print("? PyInstaller not found!")
        print("\n?? Installing PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
        print("\n? PyInstaller installed!")
        return True

def clean_build():
    """Clean previous builds"""
    print("\n?? Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"   ? Removed {d}/")
            except Exception as e:
                print(f"   ??  Could not remove {d}/: {e}")
    
    # Remove .spec files
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            try:
                os.remove(f)
                print(f"   ? Removed {f}")
            except Exception as e:
                print(f"   ??  Could not remove {f}: {e}")

def build_main_exe():
    """Build main Cindy executable"""
    print("\n???  Building ProjectCindy.exe...")
    print("   This may take 2-5 minutes...\n")
    
    import PyInstaller.__main__
    
    # Build options
    options = [
        'run_cindy.py',                     # Entry point
        '--name=ProjectCindy',              # Output name
        '--onefile',                        # Single file
        '--windowed',                       # No console window
        
        # Hidden imports (force include)
        '--hidden-import=pymem',
        '--hidden-import=psutil',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=queue',
        '--hidden-import=threading',
        
        # Add data files
        '--add-data=cindycore.py;.',
        '--add-data=cindy_ui.py;.',
        '--add-data=cindy_config.py;.',
        '--add-data=cindy_splash.py;.',
        
        # Build settings
        '--clean',
        '--log-level=WARN',
    ]
    
    # Add icon if exists
    if os.path.exists('cindy_icon.ico'):
        options.append('--icon=cindy_icon.ico')
    
    try:
        PyInstaller.__main__.run(options)
        print("\n? ProjectCindy.exe built successfully!")
        return True
    except Exception as e:
        print(f"\n? Build failed: {e}")
        return False

def build_packet_sniffer():
    """Build packet sniffer executable"""
    print("\n???  Building CindyPacketSniffer.exe...")
    
    import PyInstaller.__main__
    
    options = [
        'cindy_packet_sniffer.py',
        '--name=CindyPacketSniffer',
        '--onefile',
        '--console',  # Keep console for packet output
        
        '--hidden-import=scapy',
        '--hidden-import=scapy.all',
        '--hidden-import=pydivert',
        
        '--add-data=cindy_packet_bridge.py;.',
        '--add-data=cindy_packet_parser.py;.',
        
        '--clean',
        '--log-level=WARN',
    ]
    
    try:
        PyInstaller.__main__.run(options)
        print("\n? CindyPacketSniffer.exe built successfully!")
        return True
    except Exception as e:
        print(f"\n? Build failed: {e}")
        return False

def build_monitor():
    """Build game state monitor executable"""
    print("\n???  Building CindyMonitor.exe...")
    
    import PyInstaller.__main__
    
    options = [
        'cindy_game_state_monitor.py',
        '--name=CindyMonitor',
        '--onefile',
        '--windowed',
        
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=socket',
        '--hidden-import=json',
        
        '--add-data=cindy_packet_bridge.py;.',
        
        '--clean',
        '--log-level=WARN',
    ]
    
    try:
        PyInstaller.__main__.run(options)
        print("\n? CindyMonitor.exe built successfully!")
        return True
    except Exception as e:
        print(f"\n? Build failed: {e}")
        return False

def create_distribution():
    """Create distribution package"""
    print("\n?? Creating distribution package...")
    
    dist_folder = 'ProjectCindy_Distribution'
    
    # Remove old distribution
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    
    os.makedirs(dist_folder)
    
    # Copy executables
    files_to_copy = {
        'dist/ProjectCindy.exe': 'ProjectCindy.exe',
        'dist/CindyPacketSniffer.exe': 'CindyPacketSniffer.exe',
        'dist/CindyMonitor.exe': 'CindyMonitor.exe',
    }
    
    for src, dst in files_to_copy.items():
        if os.path.exists(src):
            shutil.copy(src, os.path.join(dist_folder, dst))
            print(f"   ? Copied {dst}")
    
    # Create README
    readme_content = """PROJECT CINDY - ENDLESS ONLINE BOT
================================

QUICK START:
1. Run ProjectCindy.exe as Administrator
2. Attach to endless.exe process
3. Scan for player and mob addresses
4. Click START BOT

PACKET MONITORING:
1. Run CindyPacketSniffer.exe as Administrator
2. Attach to endless.exe when prompted
3. Enable packet bridge (y/n)
4. Run CindyMonitor.exe to view stats

REQUIREMENTS:
- Windows 10/11
- Endless Online running
- Administrator rights

TROUBLESHOOTING:
- If bot doesn't work, rescan addresses
- If antivirus blocks, add exception
- If game crashes, restart game first

Made by Kuuna with ??
"""
    
    with open(os.path.join(dist_folder, 'README.txt'), 'w') as f:
        f.write(readme_content)
    print(f"   ? Created README.txt")
    
    print(f"\n? Distribution package created!")
    print(f"   Location: {os.path.abspath(dist_folder)}/")
    
    return dist_folder

def main():
    """Main build process"""
    print("="*60)
    print("          PROJECT CINDY - BUILD TO .EXE")
    print("="*60)
    print("\n?? This will create standalone executables for:")
    print("   - Main bot (ProjectCindy.exe)")
    print("   - Packet Sniffer (CindyPacketSniffer.exe)")
    print("   - Stats Monitor (CindyMonitor.exe)")
    print("\n??  Estimated time: 5-10 minutes")
    
    input("\nPress ENTER to start build or Ctrl+C to cancel...")
    
    try:
        # Step 1: Check PyInstaller
        if not check_pyinstaller():
            print("\n? Could not install PyInstaller!")
            return 1
        
        # Step 2: Clean previous builds
        clean_build()
        
        # Step 3: Build main executable
        if not build_main_exe():
            print("\n? Main build failed!")
            return 1
        
        # Step 4: Build packet sniffer
        print("\n" + "="*60)
        if not build_packet_sniffer():
            print("\n??  Packet sniffer build failed (optional)")
        
        # Step 5: Build monitor
        print("\n" + "="*60)
        if not build_monitor():
            print("\n??  Monitor build failed (optional)")
        
        # Step 6: Create distribution package
        print("\n" + "="*60)
        dist_folder = create_distribution()
        
        # Final summary
        print("\n" + "="*60)
        print("?? BUILD COMPLETE!")
        print("="*60)
        print(f"\n?? Distribution package: {dist_folder}/")
        print(f"\n?? Contents:")
        print(f"   - ProjectCindy.exe (main bot)")
        print(f"   - CindyPacketSniffer.exe (packet capture)")
        print(f"   - CindyMonitor.exe (stats monitor)")
        print(f"   - README.txt (instructions)")
        
        print(f"\n? Ready to distribute!")
        print(f"\n?? Tip: Run executables as Administrator")
        print(f"\n?? Test: Run ProjectCindy.exe from {dist_folder}/")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n??  Build cancelled by user")
        return 1
    
    except Exception as e:
        print(f"\n? Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
