import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import sys
import random
import subprocess
from io import StringIO
import cindycore as bot_module
import pymem
import psutil
from collections import defaultdict

# Funny scanning messages
SCANNING_MESSAGES = [
    "Hunting for a memory address that's not on vacation.",
    "Searching for a byte-sized home that's actually functional.",
    "On a quest for an address that doesn't crash the party.",
    "Scouting for a memory spot that's not playing hide-and-seek.",
    "Seeking a valid address that doesn't ghost me.",
    "Chasing a memory address that's not out to lunch.",
    "Tracking down a pointer that's not pointing to Narnia.",
    "Looking for a memory lane that's not a dead end.",
    "Trying to find an address that's not in the witness protection program.",
    "On the prowl for a memory slot that's open for business.",
    "Hunting for an address that's not lost in the digital void.",
    "Searching for a memory address that's not pulling a 404.",
    "Seeking a pointer that's not pointing to the Bermuda Triangle.",
    "Looking for an address that's not on a coffee break.",
    "Scouring for a memory spot that's not in the Twilight Zone.",
    "Chasing a valid address that's not playing hard to get.",
    "Trying to locate a memory address that's not on sabbatical.",
    "Hunting for a byte that's not dodging my calls.",
    "Seeking an address that's not stuck in a buffer loop.",
    "Looking for a memory slot that's not in the upside-down.",
    "On a mission for an address that's not AWOL.",
    "Searching for a pointer that's not lost in the matrix.",
    "Trying to find a memory address that's not on strike.",
    "Scouting for a byte that's not hiding behind a firewall.",
    "Looking for an address that's not in digital limbo.",
    "Chasing a memory spot that's not out of bounds.",
    "Seeking a pointer that's not pointing to the moon.",
    "Hunting for an address that's not in stealth mode.",
    "On the lookout for a memory slot that's not crashed out.",
    "Searching for an address that's not in the junk folder.",
    "Trying to track down a byte that's not on a wild goose chase.",
    "Looking for a memory address that's not playing hooky.",
    "Scouting for a pointer that's not stuck in quicksand.",
    "Seeking an address that's not in the digital Bermuda.",
    "Chasing a memory spot that's not in witness protection.",
    "Looking for a byte that's not on an extended vacation.",
    "Hunting for an address that's not in the recycle bin.",
    "Searching for a pointer that's not pointing to nowhere.",
    "Trying to find a memory slot that's not in a time-out.",
    "On a quest for an address that's not in the digital ether.",
    "Seeking a byte that's not dodging the spotlight.",
    "Looking for a memory address that's not in a black hole.",
    "Chasing a pointer that's not on a coffee run.",
    "Scouting for an address that's not in incognito mode.",
    "Hunting for a memory spot that's not out of service.",
    "Searching for a byte that's not lost in the cloud.",
    "Trying to locate an address that's not in the spam folder.",
    "Looking for a pointer that's not pointing to Pluto.",
    "Seeking a memory address that's not playing dead.",
    "On the hunt for a byte that's not in digital Narnia."
]

FAILURE_MESSAGES = [
    "No luck tracking down a memory address that's not on the run.",
    "Couldn't snag a byte-sized home that plays nice.",
    "Failed to find an address that's not crashing the system.",
    "Came up empty-handed looking for a pointer that's not in hiding.",
    "No dice on a memory slot that's not playing hard to get.",
    "Couldn't locate an address that's not on a coffee break.",
    "Struck out finding a pointer that's not pointing to Narnia.",
    "No valid memory lane, just a digital dead end.",
    "Couldn't catch an address that's not in witness protection.",
    "Failed to find a memory spot that's open for business.",
    "No address found; it's lost in the digital void.",
    "Couldn't track down a pointer that's not pulling a 404.",
    "No luck with an address that's not in the Bermuda Triangle.",
    "Came up short on a memory slot that's not AWOL.",
    "Couldn't find a byte that's not dodging my calls.",
    "No suitable address; it's stuck in a buffer loop.",
    "Failed to locate a memory spot that's not in the Twilight Zone.",
    "No valid pointer; it's playing hide-and-seek.",
    "Couldn't snag an address that's not on sabbatical.",
    "No dice on a memory slot that's not in the upside-down.",
    "Struck out chasing an address that's not out of bounds.",
    "Couldn't find a pointer that's not pointing to the moon.",
    "No luck with an address that's not in stealth mode.",
    "Failed to track down a byte that's not crashed out.",
    "No suitable address; it's stuck in the junk folder.",
    "Couldn't locate a memory spot that's not on a wild goose chase.",
    "No valid address; it's playing hooky.",
    "Struck out finding a pointer that's not stuck in quicksand.",
    "Couldn't snag an address that's not in digital limbo.",
    "No luck chasing a memory spot that's not in witness protection.",
    "Failed to find a byte that's not on an extended vacation.",
    "No suitable address; it's in the recycle bin.",
    "Couldn't track down a pointer that's not pointing to nowhere.",
    "No dice on a memory slot that's not in a time-out.",
    "Failed to find an address that's not in the digital ether.",
    "No luck with a byte that's not dodging the spotlight.",
    "Couldn't locate a memory address that's not in a black hole.",
    "No valid pointer; it's off on a coffee run.",
    "Struck out finding an address that's not in incognito mode.",
    "Couldn't snag a memory spot that's not out of service.",
    "No suitable address; it's lost in the cloud.",
    "Failed to track down a byte that's not in the spam folder.",
    "No luck with a pointer that's not pointing to Pluto.",
    "Couldn't find an address that's not playing dead.",
    "No dice on a memory slot that's not in digital Narnia.",
    "Struck out chasing a byte that's not in the matrix.",
    "Couldn't locate an address that's not on strike.",
    "No valid pointer; it's hiding behind a firewall.",
    "Failed to find a memory spot that's not in the digital Bermuda.",
    "No luck tracking down an address that's not just a myth."
]

SUCCESS_MESSAGES = [
    "Victory! Snagged a memory address... fingers crossed it's got enough juice!",
    "Boom! Found a byte-sized home... hope it's not a fixer-upper.",
    "Success! Landed a pointer... let's pray it doesn't crash the party.",
    "Jackpot! Got a memory address... hoping it's not just a summer rental.",
    "Nailed it! Secured an address... let's hope it's not in digital Narnia.",
    "Hooray! Found a memory slot... crossing fingers it's not a dud.",
    "Bingo! Locked in an address... hope it's not on shaky ground.",
    "Success! Tracked down a pointer... let's hope it's not pointing to nowhere.",
    "Got it! Snagged a memory address... praying it's not a one-room shack.",
    "Triumph! Found a byte... hope it's got enough bandwidth to hang.",
    "Eureka! Located a memory spot... fingers crossed it's not haunted.",
    "Score! Nabbed an address... let's hope it's not in the digital boonies.",
    "Success! Found a pointer... hoping it's not a ticket to crash city.",
    "Woohoo! Secured a memory address... let's pray it's not a lemon.",
    "Victory lap! Got an address... hope it's not just a digital mirage.",
    "Nailed it! Found a memory slot... fingers crossed it's not on life support.",
    "Success! Tracked down a byte... let's hope it's not low on storage.",
    "Gotcha! Snagged a pointer... praying it's not pointing to the void.",
    "Hallelujah! Found an address... hope it's not in the digital slums.",
    "Boom! Secured a memory spot... let's hope it's not a crash waiting to happen."
]

class BotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Cindy - EO Bot Controller")
        self.root.geometry("1000x750")
        self.root.configure(bg='#2b2b2b')
        
        # Bot state
        self.bot_thread = None
        self.bot_running = False
        self.log_queue = queue.Queue()
        self.original_stdout = sys.stdout
        
        # Scanning state
        self.scanning = False
        self.scan_thread = None
        self.scan_animation_index = 0
        self.scan_animation_timer = None
        
        # Process attachment state
        self.process_attached = False
        self.attached_pid = None
        
        # Debug mode
        self.debug_mode_var = tk.BooleanVar(value=False)
        
        # Stats tracking
        self.stats = {
            'mobs_killed': 0,
            'attacks_made': 0,
            'movements': 0,
            'start_time': None
        }
        
        # ASCII scanning animations
        self.scan_animations = [
            "[>  ] Scanning",
            "[>> ] Scanning",
            "[>>>] Scanning",
            "[>>>] Scanning",
            "[>>>] Scanning",
            "[ >>] Scanning",
            "[  >] Scanning",
            "[   ] Scanning",
        ]
        
        # Validation messages (funny!)
        self.validation_scanning_messages = [
            "Checking if old addresses are still hanging around...",
            "Verifying that addresses haven't gone on vacation...",
            "Making sure addresses aren't playing hide-and-seek...",
            "Confirming addresses haven't moved to Narnia...",
            "Testing if addresses are still accepting visitors...",
        ]
        
        self.validation_invalid_messages = [
            "Nope! Address went stale like old bread. Time for a fresh scan!",
            "Address ghosted us! Must've changed phone numbers.",
            "That address is now pointing to nowhere. Server reset detected!",
            "Address expired like milk. Better get a new one!",
            "Old address moved out without leaving a forwarding address!",
        ]
        
        self.setup_ui()
        self.update_log()
        
        # Check and validate addresses on startup
        self.root.after(500, self.validate_existing_addresses)
        
    def validate_existing_addresses(self):
        """Validate existing address files on startup - checks player first, then mob"""
        import os
        import pathlib
        
        script_dir = pathlib.Path(__file__).parent.absolute()
        player_file = os.path.join(script_dir, 'cindys_baby_daddy.txt')
        mob_file = os.path.join(script_dir, 'cindys_ex_bf.txt')
        
        # Check if files exist
        player_exists = os.path.exists(player_file)
        mob_exists = os.path.exists(mob_file)
        
        if not player_exists and not mob_exists:
            self.log_message("No existing addresses found. Please scan for addresses!", 'warning')
            self.check_address_files()
            return
        
        # Pick a random validation message
        validation_msg = random.choice(self.validation_scanning_messages)
        self.log_message(f"=== {validation_msg} ===", 'info')
        
        # Validate player address first
        if player_exists:
            self.log_message("Checking player address (cindys_baby_daddy.txt)...", 'info')
            if not self.validate_address_file(player_file, 'player'):
                invalid_msg = random.choice(self.validation_invalid_messages)
                self.log_message(f"Player address invalid! {invalid_msg}", 'error')
                os.remove(player_file)
                self.log_message("Deleted invalid player address file.", 'warning')
            else:
                self.log_message("Player address still valid! ✓", 'success')
        
        # Validate mob address
        if mob_exists:
            self.log_message("Checking mob address (cindys_ex_bf.txt)...", 'info')
            if not self.validate_address_file(mob_file, 'mob'):
                invalid_msg = random.choice(self.validation_invalid_messages)
                self.log_message(f"Mob address invalid! {invalid_msg}", 'error')
                os.remove(mob_file)
                self.log_message("Deleted invalid mob address file.", 'warning')
            else:
                self.log_message("Mob address still valid! ✓", 'success')
        
        # Update UI status
        self.check_address_files()
        
        # Check if both are missing now
        player_exists_after = os.path.exists(player_file)
        mob_exists_after = os.path.exists(mob_file)
        
        if not player_exists_after or not mob_exists_after:
            self.log_message("⚠️ WARNING: Server reset detected or addresses expired!", 'warning')
            self.log_message("Please scan for BOTH player and mob addresses again!", 'warning')
    
    def validate_address_file(self, filepath, addr_type):
        """Validate if an address file contains a valid address"""
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                
            # Try to parse as hex address
            if content.lower().startswith('0x'):
                addr = int(content, 16)
            else:
                addr = int(f"0x{content}", 16)
            
            # Basic validation: address should be in reasonable range
            if addr_type == 'player':
                # Player addresses typically in 0x04000000-0x07000000 range
                if 0x04000000 <= addr <= 0x07000000:
                    return True
            elif addr_type == 'mob':
                # Mob addresses typically in 0x00190000-0x001A0000 range (Changes per update)
                if 0x00190000 <= addr <= 0x001A0000:
                    return True
            
            return False
            
        except Exception as e:
            if bot_module.DEBUG:
                self.log_message(f"Debug: Validation error for {addr_type}: {e}", 'warning')
            return False

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg='#1e1e1e', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # Title
        title_label = tk.Label(
            left_panel, 
            text="Project Cindy", 
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        title_label.pack(pady=15)
        
        # Process Attachment Section
        attach_frame = tk.LabelFrame(
            left_panel,
            text="Process Attachment",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ff6600',
            relief=tk.GROOVE,
            borderwidth=2
        )
        attach_frame.pack(pady=10, padx=15, fill=tk.X)
        
        # Attachment status
        attach_status_row = tk.Frame(attach_frame, bg='#1e1e1e')
        attach_status_row.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(
            attach_status_row,
            text="Status:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.attach_status_label = tk.Label(
            attach_status_row,
            text="Not Attached",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ff0000',
            width=15
        )
        self.attach_status_label.pack(side=tk.LEFT, padx=5)
        
        self.attach_btn = tk.Button(
            attach_status_row,
            text="Attach to endless.exe",
            font=('Arial', 8, 'bold'),
            bg='#ff6600',
            fg='white',
            activebackground='#ff8800',
            cursor='hand2',
            command=self.attach_to_process
        )
        self.attach_btn.pack(side=tk.RIGHT)
        
        # Address Scanner Section
        scanner_frame = tk.LabelFrame(
            left_panel,
            text="Memory Scanner",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00',
            relief=tk.GROOVE,
            borderwidth=2
        )
        scanner_frame.pack(pady=10, padx=15, fill=tk.X)
        
        # Scan delay control
        delay_row = tk.Frame(scanner_frame, bg='#1e1e1e')
        delay_row.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(
            delay_row,
            text="Scan Delay:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Spinbox for delay value with black text
        self.scan_delay_var = tk.DoubleVar(value=1.0)
        self.delay_spinbox = tk.Spinbox(
            delay_row,
            from_=0.5,
            to=5.0,
            increment=0.5,
            textvariable=self.scan_delay_var,
            width=6,
            font=('Arial', 9, 'bold'),
            bg='#ffffff',
            fg='#000000',
            buttonbackground='#cccccc',
            relief=tk.SUNKEN,
            state='readonly'
        )
        self.delay_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            delay_row,
            text="seconds",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa'
        ).pack(side=tk.LEFT)
        
        # Debug mode checkbox
        debug_row = tk.Frame(scanner_frame, bg='#1e1e1e')
        debug_row.pack(fill=tk.X, pady=5, padx=10)
        
        self.debug_checkbox = tk.Checkbutton(
            debug_row,
            text="Debug Mode (Verbose Logging)",
            variable=self.debug_mode_var,
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#ffaa00',
            activebackground='#1e1e1e',
            activeforeground='#ffaa00',
            selectcolor='#0a0a0a',
            cursor='hand2',
            command=self.toggle_debug_mode
        )
        self.debug_checkbox.pack(anchor='w')
        
        # Memory range controls for Mob
        mob_range_frame = tk.LabelFrame(
            scanner_frame,
            text="Mob Memory Range",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00',
            relief=tk.FLAT
        )
        mob_range_frame.pack(fill=tk.X, pady=5, padx=10)
        
        mob_range_row = tk.Frame(mob_range_frame, bg='#1e1e1e')
        mob_range_row.pack(fill=tk.X, pady=3, padx=5)
        
        tk.Label(
            mob_range_row,
            text="Start:",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=6,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.mob_start_var = tk.StringVar(value="0x0019A000")
        mob_start_entry = tk.Entry(
            mob_range_row,
            textvariable=self.mob_start_var,
            width=12,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#000000',
            relief=tk.SUNKEN
        )
        mob_start_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            mob_range_row,
            text="End:",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=4,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.mob_end_var = tk.StringVar(value="0x0019D000")
        mob_end_entry = tk.Entry(
            mob_range_row,
            textvariable=self.mob_end_var,
            width=12,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#000000',
            relief=tk.SUNKEN
        )
        mob_end_entry.pack(side=tk.LEFT, padx=2)
        
        # Memory range controls for Player
        player_range_frame = tk.LabelFrame(
            scanner_frame,
            text="Player Memory Range",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00',
            relief=tk.FLAT
        )
        player_range_frame.pack(fill=tk.X, pady=5, padx=10)
        
        player_range_row = tk.Frame(player_range_frame, bg='#1e1e1e')
        player_range_row.pack(fill=tk.X, pady=3, padx=5)
        
        tk.Label(
            player_range_row,
            text="Start:",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=6,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.player_start_var = tk.StringVar(value="0x04000000")
        player_start_entry = tk.Entry(
            player_range_row,
            textvariable=self.player_start_var,
            width=12,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#000000',
            relief=tk.SUNKEN
        )
        player_start_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            player_range_row,
            text="End:",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=4,
            anchor='w'
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.player_end_var = tk.StringVar(value="0x07000000")
        player_end_entry = tk.Entry(
            player_range_row,
            textvariable=self.player_end_var,
            width=12,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#000000',
            relief=tk.SUNKEN
        )
        player_end_entry.pack(side=tk.LEFT, padx=2)
        
        # Mob address row
        mob_row = tk.Frame(scanner_frame, bg='#1e1e1e')
        mob_row.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(
            mob_row,
            text="Mob Address:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.mob_addr_status = tk.Label(
            mob_row,
            text="X Missing",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ff0000',
            width=10
        )
        self.mob_addr_status.pack(side=tk.LEFT, padx=5)
        
        self.scan_mob_btn = tk.Button(
            mob_row,
            text="Find",
            font=('Arial', 8, 'bold'),
            bg='#555555',
            fg='white',
            activebackground='#666666',
            cursor='hand2',
            command=lambda: self.start_scan('mob')
        )
        self.scan_mob_btn.pack(side=tk.RIGHT)
        
        # Player address row
        player_row = tk.Frame(scanner_frame, bg='#1e1e1e')
        player_row.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(
            player_row,
            text="Player Address:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.player_addr_status = tk.Label(
            player_row,
            text="X Missing",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ff0000',
            width=10
        )
        self.player_addr_status.pack(side=tk.LEFT, padx=5)
        
        self.scan_player_btn = tk.Button(
            player_row,
            text="Find",
            font=('Arial', 8, 'bold'),
            bg='#555555',
            fg='white',
            activebackground='#666666',
            cursor='hand2',
            command=lambda: self.start_scan('player')
        )
        self.scan_player_btn.pack(side=tk.RIGHT)
        
        # Scan status
        self.scan_status = tk.Label(
            scanner_frame,
            text="",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#ffaa00'
        )
        self.scan_status.pack(pady=5)
        
        # Status indicator
        self.status_frame = tk.Frame(left_panel, bg='#1e1e1e')
        self.status_frame.pack(pady=10)
        
        self.status_indicator = tk.Canvas(
            self.status_frame, 
            width=20, 
            height=20, 
            bg='#1e1e1e',
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, fill='red')
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Stopped",
            font=('Arial', 12),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Start/Stop button
        self.control_button = tk.Button(
            left_panel,
            text="START BOT",
            font=('Arial', 14, 'bold'),
            bg='#00aa00',
            fg='white',
            activebackground='#00cc00',
            activeforeground='white',
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3,
            command=self.toggle_bot
        )
        self.control_button.pack(pady=15, padx=20, fill=tk.X)
        
        # Clear logs button
        clear_button = tk.Button(
            left_panel,
            text="Clear Logs",
            font=('Arial', 10),
            bg='#555555',
            fg='white',
            activebackground='#666666',
            cursor='hand2',
            command=self.clear_logs
        )
        clear_button.pack(pady=10, padx=20, fill=tk.X)
        
        # Packet Sniffer button
        packet_button = tk.Button(
            left_panel,
            text="📡 Packet Sniffer (Experimental)",
            font=('Arial', 10, 'bold'),
            bg='#00aaff',
            fg='white',
            activebackground='#00ccff',
            cursor='hand2',
            command=self.launch_packet_sniffer
        )
        packet_button.pack(pady=(0, 10), padx=20, fill=tk.X)
        
        # Game State Monitor button
        monitor_button = tk.Button(
            left_panel,
            text="🎮 Game Monitor (Not Working)",
            font=('Arial', 10, 'bold'),
            bg='#ffaa00',
            fg='black',
            activebackground='#ffcc00',
            cursor='hand2',
            command=self.launch_game_state_monitor
        )
        monitor_button.pack(pady=(0, 10), padx=20, fill=tk.X)
        
        # Right panel - Console
        right_panel = tk.Frame(main_frame, bg='#1e1e1e', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Console title
        console_title = tk.Label(
            right_panel,
            text="Console Log",
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='#00aaff'
        )
        console_title.pack(pady=10)
        
        # Console text area
        self.console = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#0a0a0a',
            fg='#00ff00',
            insertbackground='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure text tags for colored output
        self.console.tag_config('info', foreground='#00ff00')
        self.console.tag_config('warning', foreground='#ffaa00')
        self.console.tag_config('error', foreground='#ff0000')
        self.console.tag_config('success', foreground='#00ffff')
        self.console.tag_config('timestamp', foreground='#888888')
        self.console.tag_config('ascii_art', foreground='#00ff00', font=('Courier', 9, 'bold'))
        
        # Display ASCII art banner for Project Cindy
        ascii_art = r"""
  ____            _           _      ____ _           _       
 |  _ \ _ __ ___ (_) ___  ___| |_   / ___(_)_ __   __| |_   _ 
 | |_) | '__/ _ \| |/ _ \/ __| __| | |   | | '_ \ / _` | | | |
 |  __/| | | (_) | |  __/ (__| |_  | |___| | | | | (_| | |_| |
 |_|   |_|  \___// |\___|\___|\__|  \____|_|_| |_|\__,_|\__, |
                |__/                                     |___/ 

              Endless Online Bot
         Cindy is always watching...
"""
        self.console.insert(tk.END, ascii_art, 'ascii_art')
        self.console.insert(tk.END, '\n' + '='*50 + '\n\n', 'info')
        
        self.log_message("Project Cindy initialized. Ready to start.", 'info')
        self.log_message("IMPORTANT: Attach to endless.exe first!", 'warning')
        self.log_message("NOTE: Some features are still in development.", 'warning')

    def log_message(self, message, tag='info'):
        """Add message to console with timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        self.console.insert(tk.END, f'[{timestamp}] ', 'timestamp')
        self.console.insert(tk.END, f'{message}\n', tag)
        self.console.see(tk.END)
        
    def clear_logs(self):
        """Clear console logs"""
        self.console.delete(1.0, tk.END)
        self.log_message("Logs cleared.", 'info')
    
    def launch_packet_sniffer(self):
        """Launch the packet sniffer in a completely isolated process"""
        self.log_message("Launching Packet Sniffer...", 'info')
        
        # Show info about requirements
        info_msg = messagebox.showinfo(
            "Packet Sniffer Requirements",
            "📡 Packet Sniffer\n\n"
            "Requirements:\n"
            "• Administrator rights\n"
            "• endless.exe running\n"
            "• WinPcap/Npcap installed\n\n"
            "⚠️ This feature is experimental.\n\n"
            "Continue?",
            type=messagebox.OKCANCEL
        )
        
        if info_msg == 'cancel':
            self.log_message("Packet Sniffer launch cancelled.", 'info')
            return
        
        try:
            import platform
            
            if platform.system() == 'Windows':
                # Windows: Launch in new console window (isolated)
                subprocess.Popen(
                    [sys.executable, 'cindy_packet_sniffer.py'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Unix: Launch with stream redirection
                subprocess.Popen(
                    [sys.executable, 'cindy_packet_sniffer.py'],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            messagebox.showinfo(
                "Launched", 
                "Packet Sniffer launched in new window!\n\n"
                "The sniffer runs independently.\n\n"
                "Press Ctrl+C in the sniffer window to stop capture.\n\n"
                "⚠️ Experimental feature - may not work correctly."
            )
            self.log_message("Packet Sniffer launched successfully!", 'success')
        except Exception as e:
            self.log_message(f"ERROR: Could not launch Packet Sniffer: {e}", 'error')
            messagebox.showerror("Launch Error", f"Failed to launch Packet Sniffer:\n\n{e}")
    
    def launch_game_state_monitor(self):
        """Launch the real-time game state monitor"""
        self.log_message("Launching Game State Monitor...", 'info')
        
        # Show warning about current status
        warning_msg = messagebox.showwarning(
            "Feature In Development",
            "⚠️ Game State Monitor Status:\n\n"
            "The monitor is currently not working properly.\n"
            "HP/TP values may be incorrect or not update.\n\n"
            "This feature is still being developed.\n\n"
            "Continue anyway?",
            type=messagebox.OKCANCEL
        )
        
        if warning_msg == 'cancel':
            self.log_message("Monitor launch cancelled.", 'info')
            return
        
        try:
            subprocess.Popen([sys.executable, 'cindy_game_state_monitor.py'])
            messagebox.showinfo(
                "Launched",
                "Game State Monitor launched!\n\n"
                "⚠️ Note: This feature is not fully functional yet.\n"
                "HP/TP readings may be inaccurate.\n\n"
                "Requires Packet Sniffer to be running."
            )
            self.log_message("Game State Monitor launched (EXPERIMENTAL)", 'warning')
        except Exception as e:
            self.log_message(f"ERROR: Could not launch Game State Monitor: {e}", 'error')
            messagebox.showerror("Launch Error", f"Failed to launch monitor:\n\n{e}")
    
    def attach_to_process(self):
        """Attach to endless.exe process"""
        try:
            # Find all endless.exe processes
            endless_pids = []
            for proc in psutil.process_iter():
                try:
                    if proc.name().lower() == 'endless.exe':
                        endless_pids.append((proc.pid, proc))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not endless_pids:
                self.log_message("ERROR: endless.exe not found. Please start the game first.", 'error')
                messagebox.showerror("Process Not Found", "endless.exe is not running.\n\nPlease start Endless Online first.")
                return
            
            # If multiple processes, let user choose
            if len(endless_pids) > 1:
                pid = self.select_process_dialog(endless_pids)
                if pid is None:
                    return  # User cancelled
            else:
                pid = endless_pids[0][0]
            
            # Try to attach
            try:
                pm = pymem.Pymem(pid)
                pm.close_process()  # Close immediately, just testing
                
                self.process_attached = True
                self.attached_pid = pid
                self.attach_status_label.config(text=f"Attached (PID: {pid})", fg='#00ff00')
                self.attach_btn.config(text="Detach", bg='#cc0000', command=self.detach_from_process)
                self.log_message(f"Successfully attached to endless.exe (PID: {pid})", 'success')
                
            except Exception as e:
                self.log_message(f"ERROR: Failed to attach to process: {e}", 'error')
                messagebox.showerror("Attachment Failed", f"Could not attach to endless.exe:\n\n{e}")
                
        except Exception as e:
            self.log_message(f"ERROR: {e}", 'error')
    
    def select_process_dialog(self, endless_pids):
        """Show dialog to select which endless.exe process to attach to"""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Multiple Processes Found")
        dialog.geometry("400x300")
        dialog.configure(bg='#2b2b2b')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        selected_pid = [None]  # Use list to allow modification in nested function
        
        # Title frame
        title_frame = tk.Frame(dialog, bg='#1e1e1e', relief=tk.RAISED, borderwidth=2)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text="Multiple instances of endless.exe found.\nCindy is confused. Please choose preferred instance.",
            font=('Arial', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00',
            justify=tk.CENTER,
            pady=10
        ).pack()
        
        # Process list frame
        list_frame = tk.Frame(dialog, bg='#2b2b2b')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            list_frame,
            text="Select Process:",
            font=('Arial', 9, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff'
        ).pack(anchor='w', pady=(0, 5))
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#1e1e1e', relief=tk.SUNKEN, borderwidth=2)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            listbox_frame,
            font=('Consolas', 9),
            bg='#0a0a0a',
            fg='#00ff00',
            selectbackground='#ff6600',
            selectforeground='#ffffff',
            yscrollcommand=scrollbar.set,
            height=8
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with process info
        for i, (pid, proc) in enumerate(endless_pids):
            try:
                # Get additional process info
                create_time = time.strftime('%H:%M:%S', time.localtime(proc.create_time()))
                memory_mb = proc.memory_info().rss / (1024 * 1024)
                listbox.insert(tk.END, f"PID: {pid:5d}  |  Started: {create_time}  |  Memory: {memory_mb:.1f} MB")
            except:
                listbox.insert(tk.END, f"PID: {pid:5d}  |  endless.exe")
        
        listbox.select_set(0)  # Select first by default
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_pid[0] = endless_pids[selection[0]][0]
                dialog.destroy()
        
        def on_cancel():
            selected_pid[0] = None
            dialog.destroy()
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="Select",
            font=('Arial', 10, 'bold'),
            bg='#00aa00',
            fg='white',
            activebackground='#00cc00',
            cursor='hand2',
            width=10,
            command=on_select
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=('Arial', 10, 'bold'),
            bg='#cc0000',
            fg='white',
            activebackground='#ff0000',
            cursor='hand2',
            width=10,
            command=on_cancel
        ).pack(side=tk.RIGHT, padx=5)
        
        # Bind double-click to select
        listbox.bind('<Double-Button-1>', lambda e: on_select())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return selected_pid[0]
    
    def detach_from_process(self):
        """Detach from process"""
        if self.bot_running:
            messagebox.showwarning("Bot Running", "Please stop the bot before detaching.")
            return
            
        self.process_attached = False
        self.attached_pid = None
        self.attach_status_label.config(text="Not Attached", fg='#ff0000')
        self.attach_btn.config(text="Attach to endless.exe", bg='#ff6600', command=self.attach_to_process)
        self.log_message("Detached from process.", 'warning')
    
    def toggle_debug_mode(self):
        """Toggle debug mode in cindycore"""
        enabled = self.debug_mode_var.get()
        bot_module.set_debug_mode(enabled)
        if enabled:
            self.log_message("Debug mode ENABLED - Verbose logging active", 'warning')
        else:
            self.log_message("Debug mode DISABLED - Normal logging", 'info')
    
    def update_scan_animation(self):
        """Update the scanning animation"""
        if not self.scanning:
            if self.scan_animation_timer:
                self.root.after_cancel(self.scan_animation_timer)
                self.scan_animation_timer = None
            return
        
        # Cycle through animation frames
        frame = self.scan_animations[self.scan_animation_index]
        self.scan_status.config(text=frame)
        self.scan_animation_index = (self.scan_animation_index + 1) % len(self.scan_animations)
        
        # Schedule next frame (150ms for smooth animation)
        self.scan_animation_timer = self.root.after(150, self.update_scan_animation)
    
    def start_scan(self, scan_type):
        """Start memory scanning for addresses"""
        # Require process attachment
        if not self.process_attached:
            messagebox.showerror("Not Attached", "Please attach to endless.exe first!\n\nUse the 'Attach to endless.exe' button.")
            return
            
        if self.scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running. Please wait for it to complete.")
            return
            
        if self.bot_running:
            messagebox.showwarning("Bot Running", "Please stop the bot before scanning for addresses.")
            return
        
        # Start scan in separate thread
        self.scanning = True
        self.scan_animation_index = 0
        self.update_scan_animation()  # Start animation
        self.scan_thread = threading.Thread(target=self.run_scan, args=(scan_type,), daemon=True)
        self.scan_thread.start()
        
    def run_scan(self, scan_type):
        """Run the memory scan"""
        try:
            if scan_type == 'mob':
                self.scan_mob_address()
            elif scan_type == 'player':
                self.scan_player_address()
        finally:
            self.scanning = False
            self.scan_status.config(text="")
            # Stop animation
            if self.scan_animation_timer:
                self.root.after_cancel(self.scan_animation_timer)
                self.scan_animation_timer = None
            self.root.after(0, self.check_address_files)
    
    def scan_mob_address(self):
        """Scan for mob address"""
        # Pick a random scanning message
        scan_message = random.choice(SCANNING_MESSAGES)
        self.log_message(f"=== {scan_message} ===", 'warning')
        
        # Animation handles the status display
        self.scan_mob_btn.config(state='disabled')
        self.delay_spinbox.config(state='disabled')
        
        try:
            # Find process
            pid = self.select_endless_pid_silent()
            if not pid:
                self.log_message("ERROR: No endless.exe process found. Please start the game first.", 'error')
                return
            
            pm = pymem.Pymem(pid)
            self.log_message(f"Attached to process PID {pid}", 'info')
            
            # Get memory range from UI
            try:
                START_ADDR = int(self.mob_start_var.get(), 16)
                END_ADDR = int(self.mob_end_var.get(), 16)
            except ValueError:
                self.log_message("ERROR: Invalid memory range format. Use hex format like 0x0019A000", 'error')
                messagebox.showerror("Invalid Range", "Memory range must be in hex format (e.g., 0x0019A000)")
                return
            
            MIN_SCANS = 4
            MIN_DIFFERENT_VALUES = 4
            
            # Don't log technical details
            address_scans = defaultdict(list)
            
            scan_count = 0
            valid_addresses = []
            
            # Get the scan delay from UI
            scan_delay = self.scan_delay_var.get()
            
            while scan_count < 20 and (scan_count < MIN_SCANS or not valid_addresses):
                scan_count += 1
                # Animation handles the status display - no text update here
                
                # Perform scan (silently)
                scan_results = self.scan_mob_memory(pm, START_ADDR, END_ADDR, scan_count)
                
                if scan_results:
                    for addr, pattern, dynamic_values in scan_results:
                        address_scans[addr].append((scan_count, pattern, dynamic_values))
                    
                    if scan_count >= MIN_SCANS:
                        valid_addresses = []
                        for addr, scans in address_scans.items():
                            if len(scans) >= MIN_SCANS:
                                if self.check_mob_pattern_changes(scans, MIN_DIFFERENT_VALUES):
                                    valid_addresses.append(addr)
                        
                        if valid_addresses:
                            break
                
                if scan_count < 20 and (scan_count < MIN_SCANS or not valid_addresses):
                    time.sleep(scan_delay)
            
            if valid_addresses:
                # Write to file
                import os
                import pathlib
                script_dir = pathlib.Path(__file__).parent.absolute()
                filename = os.path.join(script_dir, "cindys_ex_bf.txt")
                
                with open(filename, "w") as f:
                    f.write(f"0x{valid_addresses[0]:08X}")
                
                # Pick a random success message with address
                success_msg = random.choice(SUCCESS_MESSAGES)
                self.log_message(f"{success_msg} (0x{valid_addresses[0]:08X})", 'success')
                self.mob_addr_status.config(text="[OK] Found", fg='#00ff00')
                messagebox.showinfo("Success", f"Mob address found and saved!\n\n0x{valid_addresses[0]:08X}")
            else:
                # Pick a random failure message
                failure_msg = random.choice(FAILURE_MESSAGES)
                self.log_message(f"{failure_msg}", 'error')
                messagebox.showwarning("Scan Failed", "Could not find a valid mob address.\n\nMake sure you're in-game and mobs are moving around.")
            
            pm.close_process()
            
        except Exception as e:
            self.log_message(f"ERROR during mob scan: {e}", 'error')
            messagebox.showerror("Scan Error", f"An error occurred:\n{e}")
        finally:
            self.scan_mob_btn.config(state='normal')
            self.delay_spinbox.config(state='readonly')
    
    def scan_player_address(self):
        """Scan for player address"""
        # Pick a random scanning message
        scan_message = random.choice(SCANNING_MESSAGES)
        self.log_message(f"=== {scan_message} ===", 'warning')
        
        # Animation handles the status display
        self.scan_player_btn.config(state='disabled')
        self.delay_spinbox.config(state='disabled')
        
        try:
            # Find process
            pid = self.select_endless_pid_silent()
            if not pid:
                self.log_message("ERROR: No endless.exe process found. Please start the game first.", 'error')
                return
            
            pm = pymem.Pymem(pid)
            self.log_message(f"Attached to process PID {pid}", 'info')
            
            # Get memory range from UI
            try:
                START_ADDR = int(self.player_start_var.get(), 16)
                END_ADDR = int(self.player_end_var.get(), 16)
            except ValueError:
                self.log_message("ERROR: Invalid memory range format. Use hex format like 0x04000000", 'error')
                messagebox.showerror("Invalid Range", "Memory range must be in hex format (e.g., 0x04000000)")
                return
            
            NUM_SCANS = 2
            CHUNK_SIZE = 1024 * 1024
            
            self.log_message(f"Scanning memory range 0x{START_ADDR:08X} to 0x{END_ADDR:08X}", 'info')
            self.log_message(f"This may take a moment...", 'info')
            
            address_scans = defaultdict(list)
            
            # Get the scan delay from UI
            scan_delay = self.scan_delay_var.get()
            
            for scan_num in range(1, NUM_SCANS + 1):
                # Animation handles the status display - no text update here
                
                scan_results = self.scan_player_memory(pm, START_ADDR, END_ADDR, CHUNK_SIZE, scan_num)
                
                if scan_results:
                    for addr, pattern, static_values in scan_results:
                        address_scans[addr].append((scan_num, pattern, static_values))
                
                if scan_num < NUM_SCANS:
                    time.sleep(scan_delay)
            
            # Find consistent addresses
            consistent_addresses = []
            for addr, scans in address_scans.items():
                if len(scans) == NUM_SCANS:
                    first_values = set(values['first_byte'] for _, _, values in scans)
                    fifth_values = set(values['fifth_byte'] for _, _, values in scans)
                    
                    if len(first_values) == 1 and len(fifth_values) == 1:
                        consistent_addresses.append(addr)
            
            if consistent_addresses:
                # Write to file
                import os
                import pathlib
                script_dir = pathlib.Path(__file__).parent.absolute()
                filename = os.path.join(script_dir, "cindys_baby_daddy.txt")
                
                with open(filename, "w") as f:
                    f.write(f"0x{consistent_addresses[0]:08X}\n")
                
                # Pick a random success message with address
                success_msg = random.choice(SUCCESS_MESSAGES)
                self.log_message(f"{success_msg} (0x{consistent_addresses[0]:08X})", 'success')
                self.player_addr_status.config(text="[OK] Found", fg='#00ff00')
                messagebox.showinfo("Success", f"Player address found and saved!\n\n0x{consistent_addresses[0]:08X}")
            else:
                # Pick a random failure message
                failure_msg = random.choice(FAILURE_MESSAGES)  # Fixed: was Failure_MESSAGES
                self.log_message(f"{failure_msg}", 'error')
                messagebox.showwarning("Scan Failed", "Could not find a valid player address.\n\nMake sure you're in-game.")
            
            pm.close_process()
            
        except Exception as e:
            self.log_message(f"ERROR during player scan: {e}", 'error')
            messagebox.showerror("Scan Error", f"An error occurred:\n{e}")
        finally:
            self.scan_player_btn.config(state='normal')
            self.delay_spinbox.config(state='readonly')
    
    def scan_mob_memory(self, pm, start_addr, end_addr, scan_number):
        """Scan memory for mob pattern in chunks with aggressive reading (silently)"""
        CHUNK_SIZE = 4096  # 4KB chunks
        matches = []
        current_addr = start_addr
        
        while current_addr < end_addr:
            size = min(CHUNK_SIZE, end_addr - current_addr)
            buffer = None
            
            # Try multiple methods to read memory
            try:
                # Method 1: Normal read
                buffer = pm.read_bytes(current_addr, size)
            except Exception:
                try:
                    # Method 2: Try reading with process handle directly
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    buffer_array = (ctypes.c_char * size)()
                    bytes_read = ctypes.c_size_t()
                    
                    success = kernel32.ReadProcessMemory(
                        pm.process_handle,
                        ctypes.c_void_p(current_addr),
                        ctypes.byref(buffer_array),
                        size,
                        ctypes.byref(bytes_read)
                    )
                    
                    if success and bytes_read.value > 0:
                        buffer = bytes(buffer_array[:bytes_read.value])
                except Exception:
                    # Method 3: Try reading smaller chunks
                    try:
                        small_size = 1024  # Try 1KB instead
                        buffer = pm.read_bytes(current_addr, small_size)
                        size = small_size
                    except Exception:
                        pass
            
            # If we got any data, scan it
            if buffer:
                for offset in range(0, len(buffer) - 32):
                    if self.is_mob_pattern_match(buffer, offset):
                        addr = current_addr + offset
                        dynamic_values = self.extract_mob_dynamic_values(buffer, offset)
                        matches.append((addr, None, dynamic_values))
            
            current_addr += size
        
        return matches
    
    def is_mob_pattern_match(self, buffer, offset):
        """Check if bytes match mob pattern"""
        try:
            # Pattern: [00-03] 00 00 00 [01-FF] 00 00 00 [01-FF] 00 00 00 [00-03] 00 00 00 [00-03] 00 00 00 ...
            if not (0 <= buffer[offset] <= 3):
                return False
            if buffer[offset+1] != 0 or buffer[offset+2] != 0 or buffer[offset+3] != 0:
                return False
            if not (1 <= buffer[offset+4] <= 255):
                return False
            if buffer[offset+5] != 0 or buffer[offset+6] != 0 or buffer[offset+7] != 0:
                return False
            if not (1 <= buffer[offset+8] <= 255):
                return False
            if buffer[offset+9] != 0 or buffer[offset+10] != 0 or buffer[offset+11] != 0:
                return False
            if not (0 <= buffer[offset+12] <= 3):
                return False
            if buffer[offset+13] != 0 or buffer[offset+14] != 0 or buffer[offset+15] != 0:
                return False
            if not (0 <= buffer[offset+16] <= 3) or buffer[offset+16] != buffer[offset+12]:
                return False
            if buffer[offset+17] != 0 or buffer[offset+18] != 0 or buffer[offset+19] != 0:
                return False
            for i in range(20, 32):
                if buffer[offset+i] != 0:
                    return False
            return True
        except IndexError:
            return False
    
    def extract_mob_dynamic_values(self, buffer, offset):
        """Extract dynamic values from mob pattern"""
        return {
            'first_byte': buffer[offset],
            'fifth_byte': buffer[offset+4],
            'ninth_byte': buffer[offset+8],
            'control_bytes': buffer[offset+12]
        }
    
    def check_mob_pattern_changes(self, address_scans, min_different):
        """Check if mob pattern has enough variation (silent)"""
        first_bytes = [v['first_byte'] for _, _, v in address_scans]
        fifth_bytes = [v['fifth_byte'] for _, _, v in address_scans]
        ninth_bytes = [v['ninth_byte'] for _, _, v in address_scans]
        
        unique_first = set(first_bytes)
        unique_fifth = set(fifth_bytes)
        unique_ninth = set(ninth_bytes)
        
        total_different = len(unique_first) + len(unique_fifth) + len(unique_ninth)
        
        # Check for position variation silently
        has_position_variation = len(unique_fifth) >= 2 or len(unique_ninth) >= 2
        
        if has_position_variation:
            return True
        elif total_different >= min_different:
            return True
        else:
            return False
    
    def scan_player_memory(self, pm, start_addr, end_addr, chunk_size, scan_number):
        """Scan memory for player pattern in chunks (silent)"""
        matches = []
        current_addr = start_addr
        
        while current_addr < end_addr:
            size = min(chunk_size, end_addr - current_addr)
            
            try:
                buffer = pm.read_bytes(current_addr, size)
                
                for offset in range(0, len(buffer) - 32):
                    if self.is_player_pattern_match(buffer, offset):
                        addr = current_addr + offset
                        static_values = self.extract_player_static_values(buffer, offset)
                        matches.append((addr, None, static_values))
                
            except Exception:
                pass
            
            current_addr += size
        
        return matches
    
    def is_player_pattern_match(self, buffer, offset):
        """Check if bytes match player pattern"""
        try:
            # Pattern: (4-180) 00 00 00 (4-180) 00 00 00 ?? ?? 00 00 ?? ?? 00 00 ... FF FF
            if not (4 <= buffer[offset] <= 180):
                return False
            if buffer[offset+1] != 0 or buffer[offset+2] != 0 or buffer[offset+3] != 0:
                return False
            if not (4 <= buffer[offset+4] <= 180):
                return False
            if buffer[offset+5] != 0 or buffer[offset+6] != 0 or buffer[offset+7] != 0:
                return False
            if buffer[offset+10] != 0 or buffer[offset+11] != 0:
                return False
            if buffer[offset+14] != 0 or buffer[offset+15] != 0:
                return False
            for i in range(16, 24):
                if buffer[offset+i] != 0:
                    return False
            if buffer[offset+30] != 0xFF or buffer[offset+31] != 0xFF:
                return False
            return True
        except IndexError:
            return False
    
    def extract_player_static_values(self, buffer, offset):
        """Extract static values from player pattern"""
        return {
            'first_byte': buffer[offset],
            'fifth_byte': buffer[offset+4]
        }
    
    def select_endless_pid_silent(self):
        """Find endless.exe process without prompts"""
        for proc in psutil.process_iter():
            if proc.name().lower() == 'endless.exe':
                return proc.pid
        return None
    
    def check_address_files(self):
        """Check if address files exist and update UI accordingly"""
        import os
        import pathlib
        
        script_dir = pathlib.Path(__file__).parent.absolute()
        mob_file = os.path.join(script_dir, 'cindys_ex_bf.txt')
        player_file = os.path.join(script_dir, 'cindys_baby_daddy.txt')
        
        # Check mob address
        if os.path.exists(mob_file):
            self.mob_addr_status.config(text="[OK] Found", fg='#00ff00')
        else:
            self.mob_addr_status.config(text="X Missing", fg='#ff0000')
        
        # Check player address
        if os.path.exists(player_file):
            self.player_addr_status.config(text="[OK] Found", fg='#00ff00')
        else:
            self.player_addr_status.config(text="X Missing", fg='#ff0000')
    
    def toggle_bot(self):
        """Start or stop the bot"""
        if not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
            
    def start_bot(self):
        """Start the bot in a separate thread"""
        # Require process attachment
        if not self.process_attached:
            messagebox.showerror("Not Attached", "Please attach to endless.exe first!\n\nUse the 'Attach to endless.exe' button.")
            return
        
        # Check if addresses exist
        import os
        import pathlib
        script_dir = pathlib.Path(__file__).parent.absolute()
        mob_file = os.path.join(script_dir, 'cindys_ex_bf.txt')
        player_file = os.path.join(script_dir, 'cindys_baby_daddy.txt')
        
        if not os.path.exists(mob_file) or not os.path.exists(player_file):
            messagebox.showerror(
                "Missing Addresses",
                "Please find mob and player addresses first!\n\nUse the Memory Scanner buttons above."
            )
            return
        
        # Focus game window before starting bot
        self.log_message("Focusing game window...", 'info')
        if bot_module.focus_endless_window(self.attached_pid):
            self.log_message("Game window focused successfully", 'success')
        else:
            self.log_message("Could not focus window - bot will still run", 'warning')
        
        self.bot_running = True
        self.stats['start_time'] = time.time()
        
        # Update UI
        self.control_button.config(
            text="STOP BOT",
            bg='#cc0000',
            activebackground='#ff0000'
        )
        self.status_indicator.itemconfig(self.status_circle, fill='#00ff00')
        self.status_label.config(text="Running")
        
        # Disable scan buttons and attach button while bot is running
        self.scan_mob_btn.config(state='disabled')
        self.scan_player_btn.config(state='disabled')
        self.attach_btn.config(state='disabled')
        
        self.log_message("Starting Project Cindy bot...", 'success')
        
        # Start bot thread
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
        # Start statsUpdater
        self.update_stats()
    
    def stop_bot(self):
        """Stop the bot"""
        self.bot_running = False
        
        # Update UI
        self.control_button.config(
            text="START BOT",
            bg='#00aa00',
            activebackground='#00cc00'
        )
        self.status_indicator.itemconfig(self.status_circle, fill='#ff0000')
        self.status_label.config(text="Stopped")
        
        # Re-enable scan buttons
        self.scan_mob_btn.config(state='normal')
        self.scan_player_btn.config(state='normal')
        
        self.log_message("Bot stopped.", 'warning')
        
    def run_bot(self):
        """Run the bot with output redirection"""
        # Redirect stdout to capture bot output
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.log_queue, self.stats)
        
        try:
            # Verify addresses are available
            if bot_module.CHAR_X_ADDR is None or bot_module.CHAR_Y_ADDR is None:
                print("ERROR: Missing player addresses.")
                self.bot_running = False
                return
            
            if bot_module.MOB_BASE_ADDR is None:
                print("ERROR: Missing mob base address.")
                self.bot_running = False
                return

            # Get process
            pid = bot_module.select_endless_pid()
            if pid is None:
                print("ERROR: Could not find endless.exe process.")
                self.bot_running = False
                return

            # Attach to process
            pm = pymem.Pymem(pid)
            print(f"Attached to process PID {pid}")
            print("Bot is now running. Use the STOP BOT button to stop.")
            
            # Initialize tracking
            tracked_mobs = {}
            spawn_locations = {}
            next_mob_id = 1
            
            # Main bot loop
            while self.bot_running:
                try:
                    # Read character position
                    char_x = pm.read_int(bot_module.CHAR_X_ADDR)
                    char_y = pm.read_int(bot_module.CHAR_Y_ADDR)
                    
                    # Read mob movement data
                    face_val = pm.read_int(bot_module.FACE_ADDR)
                    y_val = pm.read_int(bot_module.Y_ADDR)
                    x_val = pm.read_int(bot_module.X_ADDR)
                    
                    # Read spawn data
                    spawn_face_val = pm.read_int(bot_module.SPAWN_FACE_ADDR)
                    spawn_y_val = pm.read_int(bot_module.SPAWN_Y_ADDR)
                    spawn_x_val = pm.read_int(bot_module.SPAWN_X_ADDR)
                    
                    # Process mob movements and spawns here
                    # (simplified for now - can be expanded later)
                    
                    # Small delay to prevent CPU overuse
                    time.sleep(0.01)
                    
                except Exception as e:
                    print(f"Memory read error: {e}")
                    time.sleep(0.5)
                    continue
            
            # Close process handle
            pm.close_process()
            print("Bot stopped successfully.")
            
        except Exception as e:
            print(f"Bot error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Ensure original stdout is restored
            sys.stdout = old_stdout
            
            # Clean up
            self.log_message("Bot has exited.", 'warning')
            self.bot_running = False
            self.root.after(0, lambda: self.control_button.config(text="START BOT", bg='#00aa00', activebackground='#00cc00'))
            self.root.after(0, lambda: self.status_indicator.itemconfig(self.status_circle, fill='#ff0000'))
            self.root.after(0, lambda: self.status_label.config(text="Stopped"))
        
    def update_stats(self):
        """Update stats display"""
        if not self.bot_running:
            return
        
        # Update runtime
        if self.stats['start_time'] is not None:
            elapsed_time = time.time() - self.stats['start_time']
            self.stats_labels['runtime'].config(text=f"{elapsed_time:.1f} s")
        else:
            self.stats_labels['runtime'].config(text="0.0 s")
        
        # Repeat every second
        self.root.after(1000, self.update_stats)
    
    def update_log(self):
        """Update console from log queue (thread-safe)"""
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                # Determine tag based on content
                if 'ERROR' in message or 'Error' in message:
                    tag = 'error'
                elif 'WARNING' in message or 'Warning' in message:
                    tag = 'warning'
                elif 'Kill' in message or 'killed' in message:
                    tag = 'success'
                else:
                    tag = 'info'
                
                self.log_message(message, tag)
        except queue.Empty:
            pass
        finally:
            # Schedule next update
            if hasattr(self.root, 'winfo_exists') and self.root.winfo_exists():
                self.root.after(100, self.update_log)

class StdoutRedirector:
    """Redirector for stdout to display in Tkinter Text widget"""
    def __init__(self, queue, stats):
        self.queue = queue
        self.stats = stats
        
    def write(self, message):
        """Write message to queue"""
        if message.strip() == "":
            return
        
        # Add to queue for thread-safe access
        self.queue.put(message)
        
    def flush(self):
        """Flush method (no-op)"""
        pass

# End of bot_ui.py
