import time
import pymem
import psutil
import ctypes
import math
import os
import pathlib
import random

# Debug mode flag
DEBUG = False

def set_debug_mode(enabled):
    """Enable or disable debug mode."""
    global DEBUG
    DEBUG = enabled
    print(f"Debug mode: {'ENABLED' if enabled else 'DISABLED'}")

def focus_endless_window(pid):
    """Bring Endless Online window to foreground."""
    try:
        import win32gui
        import win32process
        
        def callback(hwnd, list_to_append):
            list_to_append.append((hwnd, win32gui.GetWindowText(hwnd)))
        
        window_list = []
        win32gui.EnumWindows(callback, window_list)
        for i in window_list:
            w = i[0]
            p = win32process.GetWindowThreadProcessId(w)[1]
            if pid == p:
                win32gui.ShowWindow(w, 5)
                win32gui.SetForegroundWindow(w)
                win32gui.SetActiveWindow(w)
                print("Focused Endless Online window")
                return True
        print("Warning: Could not find Endless Online window")
        return False
    except ImportError:
        print("Warning: pywin32 not installed. Window focus disabled.")
        return False
    except Exception as e:
        print(f"Warning: Could not focus window: {e}")
        return False

def read_address_from_file(filename):
    """Read hex address from file."""
    try:
        script_dir = pathlib.Path(__file__).parent.absolute()
        file_path = os.path.join(script_dir, filename)
        
        with open(file_path, 'r') as f:
            # Read only the first line and strip whitespace
            content = f.readline().strip()
            if content.lower().startswith('0x'):
                return int(content, 16)
            else:
                return int(f"0x{content}", 16)
    except Exception as e:
        print(f"Error reading from {filename}: {e}")
        return None

# Read addresses
MOB_BASE_ADDR = read_address_from_file('cindys_ex_bf.txt')
CHAR_X_ADDR = read_address_from_file('cindys_baby_daddy.txt')

# Calculate offsets
if MOB_BASE_ADDR is not None:
    # Movement addresses
    FACE_ADDR = MOB_BASE_ADDR
    Y_ADDR = MOB_BASE_ADDR + 0x4
    X_ADDR = MOB_BASE_ADDR + 0x8
    
    # Spawn addresses - CORRECTED using 0x0019B4EC as the face reference
    SPAWN_FACE_ADDR = MOB_BASE_ADDR - 0x14  
    SPAWN_Y_ADDR = MOB_BASE_ADDR - 0x10     
    SPAWN_X_ADDR = MOB_BASE_ADDR - 0xC      
    
    # Mob ID addresses (for hit detection)
    MOB_ID_ADDR1 = MOB_BASE_ADDR + 0x98
    MOB_ID_ADDR2 = MOB_BASE_ADDR + 0xA0
    
    # Kill detection addresses
    KILL_ADDR1 = MOB_BASE_ADDR + 0x9C
    KILL_ADDR2 = MOB_BASE_ADDR + 0xA4
else:
    print("Error: Failed to read mob address")
    FACE_ADDR = Y_ADDR = X_ADDR = None
    SPAWN_FACE_ADDR = SPAWN_Y_ADDR = SPAWN_X_ADDR = None
    MOB_ID_ADDR1 = MOB_ID_ADDR2 = None

if CHAR_X_ADDR is not None:
    CHAR_Y_ADDR = CHAR_X_ADDR + 0x4
else:
    print("Error: Failed to read player address")
    CHAR_Y_ADDR = None

# Direction mapping
FACE_OFFSETS = {0: (0, 1), 1: (-1, 0), 2: (0, -1), 3: (1, 0)}  # down, left, up, right
FACE_NAMES = {0: 'down', 1: 'left', 2: 'up', 3: 'right'}

# Virtual key codes
VK_CODE = {'up': 0x68, 'left': 0x64, 'down': 0x62, 'right': 0x66, 'ctrl': 0x11}

# Adaptive key press durations
INITIAL_MOVEMENT_DURATION = 0.03  # 50ms
MAX_MOVEMENT_DURATION = 0.05
INITIAL_CTRL_DURATION = 0.05
MAX_CTRL_DURATION = 0.3
FACING_DURATION = 0.5
DURATION_INCREMENT = 0.05

# Movement tracking
movement_durations = {key: INITIAL_MOVEMENT_DURATION for key in ['up', 'down', 'left', 'right']}
ctrl_duration = INITIAL_CTRL_DURATION
movement_success_rate = {key: {'attempts': 0, 'successes': 0} for key in ['up', 'down', 'left', 'right', 'ctrl']}

def select_endless_pid():
    """Find endless.exe process."""
    endless_pids = []
    for proc in psutil.process_iter():
        if proc.name().lower() == 'endless.exe':
            endless_pids.append(proc.pid)

    if not endless_pids:
        print("No 'endless.exe' found.")
        return None

    if len(endless_pids) == 1:
        pid = endless_pids[0]
        print(f"Found process (PID {pid}).")
        return pid

    print("Multiple processes found:")
    for i, pid in enumerate(endless_pids, start=1):
        print(f"{i}. PID = {pid}")

    while True:
        choice = input("Select process #: ")