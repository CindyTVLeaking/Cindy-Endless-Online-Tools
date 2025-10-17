# -*- coding: utf-8 -*-
"""
Project Cindy - Configuration File
Central configuration for all bot components

Server Information:
  IP: 69.10.49.30 (Endless Online Official Server)
  Port: 8078
  Protocol: EO Protocol (custom binary protocol)
"""

# ===================================
# ENDLESS ONLINE SERVER CONFIGURATION
# ===================================

# Server connection details
SERVER_IP = "69.10.49.30"
SERVER_PORT = 8078
SERVER_NAME = "Endless Online Official Server"

# Packet capture filter for network analysis
PACKET_FILTER = f"host {SERVER_IP} and port {SERVER_PORT}"

# ==================================================
# MEMORY SCANNER CONFIGURATION
# ==================================================

# Player memory range
PLAYER_MEMORY_START = 0x04000000
PLAYER_MEMORY_END = 0x07000000

# Mob memory range (may change per update)
MOB_MEMORY_START = 0x0019A000
MOB_MEMORY_END = 0x0019D000

# Scan settings
DEFAULT_SCAN_DELAY = 1.0  # seconds
MIN_SCANS_REQUIRED = 4
MIN_DIFFERENT_VALUES = 4

# ==================================================
# UI CONFIGURATION
# ==================================================

# Color scheme
UI_COLORS = {
    'background': '#2b2b2b',
    'panel': '#1e1e1e',
    'console': '#0a0a0a',
    'success': '#00ff00',
    'warning': '#ffaa00',
    'error': '#ff0000',
    'info': '#00ffff',
    'timestamp': '#888888',
    'primary': '#00ff00',
    'secondary': '#00aaff',
    'accent': '#ff6600',
    'advanced': '#9933ff',
}

# Window dimensions
MAIN_WINDOW_WIDTH = 1000
MAIN_WINDOW_HEIGHT = 750

SPLASH_WINDOW_WIDTH = 600
SPLASH_WINDOW_HEIGHT = 700

TOOLS_WINDOW_WIDTH = 700
TOOLS_WINDOW_HEIGHT = 600

# ==================================================
# BOT CONFIGURATION
# ==================================================

# Bot behavior
MOVEMENT_COOLDOWN = 0.02  # seconds
STUCK_TIMEOUT = 1.0  # seconds
ATTACK_RANGE = 1  # tiles

# Performance
CPU_USAGE_LIMIT = 25  # percent
MEMORY_LIMIT = 150  # MB

# ==================================================
# DEBUG CONFIGURATION
# ==================================================

DEBUG_MODE = False
VERBOSE_LOGGING = False

# ==================================================
# FILE PATHS
# ==================================================

# Address files
PLAYER_ADDRESS_FILE = "cindys_baby_daddy.txt"
MOB_ADDRESS_FILE = "cindys_ex_bf.txt"

# Image file
CINDY_IMAGE_FILE = "projectcindy.gla"

# Backup directory
BACKUP_DIR = "backup_before_rename"

# ==================================================
# PACKET SNIFFER CONFIGURATION
# ==================================================

# Network capture settings
CAPTURE_FILTER = f"host {SERVER_IP} and port {SERVER_PORT}"
PACKET_BUFFER_SIZE = 1000
SAVE_PACKETS = True
PACKET_LOG_DIR = "packet_logs"

# ==================================================
# ADVANCED TOOLS CONFIGURATION
# ==================================================

TOOLS_AVAILABLE = {
    'packet_sniffer': True,
    'eolib_test': True,
    'memory_viewer': False,  # Coming soon
    'address_manager': False,  # Coming soon
    'pattern_scanner': False,  # Coming soon
    'performance_monitor': False,  # Coming soon
    'debug_console': False,  # Coming soon
}

# ==================================================
# VERSION INFO
# ==================================================

VERSION = "1.0.0"
PROJECT_NAME = "Project Cindy"
AUTHOR = "Kuuna"
DESCRIPTION = "Endless Online Bot - Memory-based automation"

# ==================================================
# SERVER INFORMATION (for documentation/reference)
# ==================================================

SERVER_INFO = f"""
Endless Online Server Details:
  IP Address: {SERVER_IP}
  Port: {SERVER_PORT}
  Protocol: EO Protocol (custom)
  
Connection String: {SERVER_IP}:{SERVER_PORT}

Note: This information is for packet sniffing and 
network analysis purposes only.
"""

def get_server_endpoint():
    """Get server endpoint as tuple"""
    return (SERVER_IP, SERVER_PORT)

def get_capture_filter():
    """Get packet capture filter string"""
    return CAPTURE_FILTER

def print_server_info():
    """Print server information"""
    print(SERVER_INFO)

if __name__ == "__main__":
    # Display configuration when run directly
    print("="*50)
    print(f"  {PROJECT_NAME} v{VERSION}")
    print("  Configuration File")
    print("="*50)
    print()
    print_server_info()
    print()
    print(f"Player Memory Range: 0x{PLAYER_MEMORY_START:08X} - 0x{PLAYER_MEMORY_END:08X}")
    print(f"Mob Memory Range: 0x{MOB_MEMORY_START:08X} - 0x{MOB_MEMORY_END:08X}")
    print()
    print(f"UI Theme: Dark")
    print(f"Main Window: {MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")
    print()
    print("Available Tools:")
    for tool, available in TOOLS_AVAILABLE.items():
        status = "?" if available else "??"
        print(f"  {status} {tool.replace('_', ' ').title()}")
    print()
    print("="*50)
