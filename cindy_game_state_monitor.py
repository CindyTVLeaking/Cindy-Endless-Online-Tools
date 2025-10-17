# -*- coding: utf-8 -*-
"""
Cindy's Real-Time Game State Monitor - ENHANCED
Live dashboard showing complete character state from packet capture
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import queue

class GameStateMonitor:
    """Enhanced real-time game state monitoring window"""
    
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Cindy's Game State Monitor - Enhanced")
        self.root.geometry("900x800")
        self.root.configure(bg='#1e1e1e')
        
        # Packet bridge client
        self.bridge_client = None
        self.bridge_connected = False
        
        # Game state - EXPANDED
        self.game_state = {
            # Basic vitals
            'hp': 0, 'max_hp': 100,
            'tp': 0, 'max_tp': 100,
            'sp': 0, 'max_sp': 0,
            'exp': 0, 'level': 1,
            'gold': 0,
            
            # Character info
            'name': 'Unknown',
            'class': 'Peasant',
            'guild': 'None',
            
            # Position
            'x': 0, 'y': 0,
            'map_id': 0,
            'map_name': 'Unknown',
            
            # Status
            'sitting': False,
            'status': 'Unknown',
            
            # Base stats
            'str': 0, 'int': 0,
            'wis': 0, 'agi': 0,
            'con': 0, 'cha': 0,
            'stat_points': 0,
            'skill_points': 0,
            
            # Combat stats
            'dps': 0.0,
            'hits': 0,
            'misses': 0,
            'kills': 0,
            'damage_dealt': 0,
            
            # Inventory
            'inventory_used': 0,
            'inventory_max': 50,
            'weight': 0,
            'max_weight': 250,
            
            # Buffs (list of dicts)
            'buffs': []
        }
        
        self.running = True
        self.monitoring = False
        self.update_thread = None
        self.update_queue = queue.Queue()
        
        self.setup_ui()
        self.start_update_thread()
        
    def setup_ui(self):
        """Setup the enhanced monitoring UI"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#0a0a0a', relief=tk.RAISED, borderwidth=2)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text="?? Real-Time Game State Monitor",
            font=('Arial', 16, 'bold'),
            bg='#0a0a0a',
            fg='#00ff00',
            pady=10
        ).pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#1e1e1e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create 2-column layout
        left_column = tk.Frame(content_frame, bg='#1e1e1e')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = tk.Frame(content_frame, bg='#1e1e1e')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # === LEFT COLUMN ===
        
        # Vitals Section
        self.create_vitals_section(left_column)
        
        # Base Stats Section
        self.create_base_stats_section(left_column)
        
        # Inventory Section
        self.create_inventory_section(left_column)
        
        # === RIGHT COLUMN ===
        
        # Character Info Section
        self.create_character_info_section(right_column)
        
        # Combat Stats Section
        self.create_combat_stats_section(right_column)
        
        # Buffs Section
        self.create_buffs_section(right_column)
        
        # === BOTTOM BAR ===
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#0a0a0a', relief=tk.SUNKEN, borderwidth=2)
        status_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        status_left = tk.Frame(status_frame, bg='#0a0a0a')
        status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            status_left,
            text="?? Packet Feed:",
            font=('Arial', 9),
            bg='#0a0a0a',
            fg='#aaaaaa'
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.connection_status = tk.Label(
            status_left,
            text="?? Waiting...",
            font=('Arial', 9, 'bold'),
            bg='#0a0a0a',
            fg='#ffaa00'
        )
        self.connection_status.pack(side=tk.LEFT, padx=5)
        
        self.packet_counter = tk.Label(
            status_frame,
            text="Packets: 0",
            font=('Arial', 8),
            bg='#0a0a0a',
            fg='#888888'
        )
        self.packet_counter.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(
            button_frame,
            text="?? Start Monitoring",
            font=('Arial', 10, 'bold'),
            bg='#00aa00',
            fg='white',
            activebackground='#00cc00',
            cursor='hand2',
            command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="?? Stop",
            font=('Arial', 10, 'bold'),
            bg='#cc0000',
            fg='white',
            activebackground='#ff0000',
            cursor='hand2',
            state='disabled',
            command=self.stop_monitoring
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="?? Refresh",
            font=('Arial', 10, 'bold'),
            bg='#0088ff',
            fg='white',
            activebackground='#00aaff',
            cursor='hand2',
            command=self.refresh_display
        ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="? Close",
            font=('Arial', 10, 'bold'),
            bg='#555555',
            fg='white',
            activebackground='#666666',
            cursor='hand2',
            command=self.close_window
        ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def create_vitals_section(self, parent):
        """Create vitals (HP/TP/SP/EXP) section"""
        frame = tk.LabelFrame(
            parent,
            text="?? Vitals",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # HP Bar
        self.create_stat_bar(frame, "?? Health", 'hp', '#ff0000')
        
        # TP Bar
        self.create_stat_bar(frame, "? TP", 'tp', '#0088ff')
        
        # SP Bar
        self.create_stat_bar(frame, "? SP", 'sp', '#ffaa00')
        
        # EXP Bar
        self.create_stat_bar(frame, "? Experience", 'exp', '#00ff00')
    
    def create_base_stats_section(self, parent):
        """Create base stats section"""
        frame = tk.LabelFrame(
            parent,
            text="?? Base Stats",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#00aaff',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Stats grid
        stats_grid = tk.Frame(frame, bg='#1e1e1e')
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1
        self.create_stat_label(stats_grid, "?? STR:", 'str_label', 0, 0)
        self.create_stat_label(stats_grid, "?? INT:", 'int_label', 0, 2)
        
        # Row 2
        self.create_stat_label(stats_grid, "?? WIS:", 'wis_label', 1, 0)
        self.create_stat_label(stats_grid, "?? AGI:", 'agi_label', 1, 2)
        
        # Row 3
        self.create_stat_label(stats_grid, "??? CON:", 'con_label', 2, 0)
        self.create_stat_label(stats_grid, "? CHA:", 'cha_label', 2, 2)
        
        # Points available
        points_frame = tk.Frame(frame, bg='#1e1e1e')
        points_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            points_frame,
            text="Available:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa'
        ).pack(side=tk.LEFT)
        
        self.stat_points_label = tk.Label(
            points_frame,
            text="Stat: 0  |  Skill: 0",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00'
        )
        self.stat_points_label.pack(side=tk.LEFT, padx=10)
    
    def create_inventory_section(self, parent):
        """Create inventory section"""
        frame = tk.LabelFrame(
            parent,
            text="?? Inventory",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ffaa00',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Items used
        items_row = tk.Frame(frame, bg='#1e1e1e')
        items_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            items_row,
            text="?? Items:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.items_label = tk.Label(
            items_row,
            text="0 / 50",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.items_label.pack(side=tk.LEFT)
        
        # Items bar
        self.items_bar = ttk.Progressbar(
            frame,
            length=300,
            mode='determinate'
        )
        self.items_bar.pack(pady=5, padx=10)
        
        # Weight
        weight_row = tk.Frame(frame, bg='#1e1e1e')
        weight_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            weight_row,
            text="?? Weight:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.weight_label = tk.Label(
            weight_row,
            text="0 / 250 lbs",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.weight_label.pack(side=tk.LEFT)
        
        # Gold
        gold_row = tk.Frame(frame, bg='#1e1e1e')
        gold_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            gold_row,
            text="?? Gold:",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.gold_label = tk.Label(
            gold_row,
            text="0",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffff00'
        )
        self.gold_label.pack(side=tk.LEFT)
    
    def create_character_info_section(self, parent):
        """Create character info section"""
        frame = tk.LabelFrame(
            parent,
            text="?? Character Info",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#00aaff',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.create_info_row(frame, "?? Name:", 'name_label')
        self.create_info_row(frame, "? Level:", 'level_label')
        self.create_info_row(frame, "?? Class:", 'class_label')
        self.create_info_row(frame, "?? Guild:", 'guild_label')
        self.create_info_row(frame, "?? Position:", 'position_label')
        self.create_info_row(frame, "??? Map:", 'map_label')
        self.create_info_row(frame, "?? Status:", 'status_label')
    
    def create_combat_stats_section(self, parent):
        """Create combat stats section"""
        frame = tk.LabelFrame(
            parent,
            text="?? Combat Statistics",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ff6600',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.create_info_row(frame, "?? DPS:", 'dps_label')
        self.create_info_row(frame, "?? Hits:", 'hits_label')
        self.create_info_row(frame, "? Misses:", 'misses_label')
        self.create_info_row(frame, "?? Accuracy:", 'accuracy_label')
        self.create_info_row(frame, "?? Kills:", 'kills_label')
        self.create_info_row(frame, "? Damage:", 'damage_label')
    
    def create_buffs_section(self, parent):
        """Create active buffs section"""
        frame = tk.LabelFrame(
            parent,
            text="? Active Effects",
            font=('Arial', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ff00ff',
            relief=tk.GROOVE,
            borderwidth=2
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Scrolled text for buffs
        self.buffs_display = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#0a0a0a',
            fg='#00ff00',
            height=6,
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.buffs_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.buffs_display.insert('1.0', 'No active effects')
        self.buffs_display.config(state='disabled')
    
    def create_stat_bar(self, parent, label_text, stat_key, color='#00ff00'):
        """Create a visual stat bar with label and value"""
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(fill=tk.X, pady=3, padx=10)
        
        # Label
        tk.Label(
            container,
            text=label_text,
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Progress bar
        style_name = f'{stat_key}.Horizontal.TProgressbar'
        style = ttk.Style()
        style.configure(
            style_name,
            troughcolor='#0a0a0a',
            bordercolor=color,
            background=color,
            lightcolor=color,
            darkcolor=color
        )
        
        progress = ttk.Progressbar(
            container,
            length=180,
            mode='determinate',
            style=style_name
        )
        progress.pack(side=tk.LEFT, padx=5)
        
        # Value label
        value_label = tk.Label(
            container,
            text="0/100 (0%)",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#00ffff',
            width=15,
            anchor='e'
        )
        value_label.pack(side=tk.LEFT)
        
        # Store references
        setattr(self, f'{stat_key}_bar', progress)
        setattr(self, f'{stat_key}_value', value_label)
    
    def create_stat_label(self, parent, label_text, attr_name, row, col):
        """Create a stat label in grid"""
        label = tk.Label(
            parent,
            text=label_text,
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=8,
            anchor='w'
        )
        label.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        
        value = tk.Label(
            parent,
            text="0",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff',
            width=5,
            anchor='e'
        )
        value.grid(row=row, column=col+1, sticky='e', padx=5, pady=2)
        
        setattr(self, attr_name, value)
    
    def create_info_row(self, parent, label_text, attr_name):
        """Create an info row with label and value"""
        row = tk.Frame(parent, bg='#1e1e1e')
        row.pack(fill=tk.X, pady=3, padx=10)
        
        tk.Label(
            row,
            text=label_text,
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#aaaaaa',
            width=12,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        value_label = tk.Label(
            row,
            text="--",
            font=('Arial', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff',
            anchor='w'
        )
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        setattr(self, attr_name, value_label)
    
    def start_update_thread(self):
        """Start the UI update thread"""
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def update_loop(self):
        """Background thread for processing updates"""
        packet_count = 0
        while self.running:
            try:
                # Check for updates in queue
                if not self.update_queue.empty():
                    update = self.update_queue.get_nowait()
                    if update['type'] == 'state':
                        self.game_state.update(update['data'])
                        packet_count += 1
                        self.root.after(0, self.refresh_ui)
                        self.root.after(0, lambda: self.packet_counter.config(text=f"Packets: {packet_count}"))
                
                time.sleep(0.05)  # 20 Hz update rate
            except Exception as e:
                print(f"Update loop error: {e}")
    
    def update_game_state(self, state_dict):
        """Update game state from external source (thread-safe)"""
        self.update_queue.put({
            'type': 'state',
            'data': state_dict
        })
    
    def refresh_ui(self):
        """Refresh all UI elements with current game state"""
        try:
            # Update vitals
            self.update_vital_bar('hp')
            self.update_vital_bar('tp')
            self.update_vital_bar('sp')
            self.update_vital_bar('exp')
            
            # Update base stats
            self.str_label.config(text=str(self.game_state['str']))
            self.int_label.config(text=str(self.game_state['int']))
            self.wis_label.config(text=str(self.game_state['wis']))
            self.agi_label.config(text=str(self.game_state['agi']))
            self.con_label.config(text=str(self.game_state['con']))
            self.cha_label.config(text=str(self.game_state['cha']))
            
            self.stat_points_label.config(
                text=f"Stat: {self.game_state['stat_points']}  |  Skill: {self.game_state['skill_points']}"
            )
            
            # Update inventory
            items_percent = (self.game_state['inventory_used'] / max(self.game_state['inventory_max'], 1)) * 100
            self.items_bar['value'] = items_percent
            self.items_label.config(
                text=f"{self.game_state['inventory_used']} / {self.game_state['inventory_max']}"
            )
            
            weight_text = f"{self.game_state['weight']} / {self.game_state['max_weight']} lbs"
            self.weight_label.config(text=weight_text)
            
            self.gold_label.config(text=f"{self.game_state['gold']:,}")
            
            # Update character info
            self.name_label.config(text=self.game_state['name'])
            self.level_label.config(text=str(self.game_state['level']))
            self.class_label.config(text=self.game_state['class'])
            self.guild_label.config(text=self.game_state['guild'])
            self.position_label.config(
                text=f"({self.game_state['x']}, {self.game_state['y']})"
            )
            self.map_label.config(
                text=f"{self.game_state['map_name']} ({self.game_state['map_id']})"
            )
            
            # Update status
            if self.game_state['sitting']:
                status_text = "?? Sitting"
                status_color = '#00aaff'
            elif self.monitoring:
                status_text = "?? Active"
                status_color = '#00ff00'
            else:
                status_text = self.game_state['status']
                status_color = '#ffaa00'
            
            self.status_label.config(text=status_text, fg=status_color)
            
            # Update combat stats
            self.dps_label.config(text=f"{self.game_state['dps']:.1f}")
            self.hits_label.config(text=str(self.game_state['hits']))
            self.misses_label.config(text=str(self.game_state['misses']))
            
            total_attacks = self.game_state['hits'] + self.game_state['misses']
            accuracy = (self.game_state['hits'] / max(total_attacks, 1)) * 100 if total_attacks > 0 else 0
            self.accuracy_label.config(text=f"{accuracy:.1f}%")
            
            self.kills_label.config(text=str(self.game_state['kills']))
            self.damage_label.config(text=f"{self.game_state['damage_dealt']:,}")
            
            # Update buffs
            self.update_buffs_display()
            
        except Exception as e:
            print(f"UI update error: {e}")
    
    def update_vital_bar(self, stat_key):
        """Update a vital bar (HP/TP/SP/EXP)"""
        current = self.game_state[stat_key]
        
        # Special handling for EXP (doesn't have max_exp)
        if stat_key == 'exp':
            # For demo purposes, show EXP as progress to next level
            # In real implementation, would calculate based on level tables
            level = self.game_state.get('level', 1)
            # Simplified: assume 1000 * level for next level
            exp_needed = 1000 * level
            maximum = exp_needed
        else:
            maximum = self.game_state.get(f'max_{stat_key}', 100)
        
        if maximum > 0:
            percent = (current / maximum) * 100
            bar = getattr(self, f'{stat_key}_bar')
            value_label = getattr(self, f'{stat_key}_value')
            
            bar['value'] = min(percent, 100)  # Cap at 100%
            
            if stat_key == 'exp':
                value_label.config(text=f"{current:,} ({percent:.0f}%)")
            else:
                value_label.config(text=f"{current}/{maximum} ({percent:.0f}%)")
        else:
            bar = getattr(self, f'{stat_key}_bar')
            value_label = getattr(self, f'{stat_key}_value')
            bar['value'] = 0
            value_label.config(text="N/A")
    
    def update_buffs_display(self):
        """Update the buffs display"""
        self.buffs_display.config(state='normal')
        self.buffs_display.delete('1.0', tk.END)
        
        if not self.game_state['buffs']:
            self.buffs_display.insert('1.0', 'No active effects')
        else:
            for buff in self.game_state['buffs']:
                duration = buff.get('duration', 0)
                name = buff.get('name', 'Unknown')
                bars = int((duration / 100) * 10)  # Assuming max 100s
                bar_visual = '?' * bars + '?' * (10 - bars)
                self.buffs_display.insert(tk.END, f"{name:<20} [{bar_visual}] {duration}s\n")
        
        self.buffs_display.config(state='disabled')
    
    def start_monitoring(self):
        """Start packet monitoring"""
        # Try to read max HP/TP from memory first
        try:
            from cindycore import CindyCore
            cindy = CindyCore()
            
            # Try to get max HP/TP from memory
            max_hp = cindy.read_max_hp()
            max_tp = cindy.read_max_tp()
            
            if max_hp and max_hp > 0:
                self.game_state['max_hp'] = max_hp
                print(f"?? Max HP from memory: {max_hp}")
            
            if max_tp and max_tp > 0:
                self.game_state['max_tp'] = max_tp
                print(f"?? Max TP from memory: {max_tp}")
                
        except Exception as e:
            print(f"Could not read max HP/TP from memory: {e}")
        
        # Try to connect to packet bridge
        try:
            from cindy_packet_bridge import PacketBridgeClient
            
            if not self.bridge_connected:
                self.bridge_client = PacketBridgeClient()
                self.bridge_client.set_callback(self.on_bridge_update)
                
                if self.bridge_client.connect():
                    self.bridge_connected = True
                    self.monitoring = True
                    self.connection_status.config(text="? Connected", fg='#00ff00')
                    self.start_btn.config(state='disabled')
                    self.stop_btn.config(state='normal')
                    
                    messagebox.showinfo(
                        "Connected",
                        f"?? Connected to Packet Sniffer!\n\n"
                        f"Max HP: {self.game_state['max_hp']}\n"
                        f"Max TP: {self.game_state['max_tp']}\n\n"
                        "Real-time HP/TP will now update from packets!"
                    )
                    return
                    
        except Exception as e:
            print(f"Bridge connection failed: {e}")
        
        # If bridge connection failed, use demo mode
        self.monitoring = True
        self.connection_status.config(text="?? Demo Mode", fg='#ffaa00')
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        messagebox.showinfo(
            "Demo Mode",
            "?? Could not connect to Packet Sniffer\n\n"
            "Running in DEMO MODE instead.\n\n"
            "To use real data:\n"
            "1. Start packet sniffer\n"
            "2. Enable bridge when prompted\n"
            "3. Restart monitor"
        )
        
        # Demo: Simulate complete character state
        self.update_game_state({
            'hp': 450, 'max_hp': 500,
            'tp': 120, 'max_tp': 200,
            'sp': 85, 'max_sp': 100,
            'exp': 12450, 'level': 25,
            'gold': 54320,
            'name': 'Kuuna',
            'class': 'Warrior',
            'guild': 'Project Cindy',
            'x': 45, 'y': 67,
            'map_id': 12,
            'map_name': 'Aeven',
            'sitting': False,
            'status': '?? Fighting',
            'str': 25, 'int': 30,
            'wis': 20, 'agi': 35,
            'con': 28, 'cha': 15,
            'stat_points': 3,
            'skill_points': 5,
            'dps': 23.4,
            'hits': 156,
            'misses': 12,
            'kills': 45,
            'damage_dealt': 3642,
            'inventory_used': 25,
            'inventory_max': 50,
            'weight': 145,
            'max_weight': 250,
            'buffs': [
                {'name': '? Haste', 'duration': 45},
                {'name': '??? Defense Up', 'duration': 62},
                {'name': '?? Strength', 'duration': 98}
            ]
        })
    
    def on_bridge_update(self, state_data):
        """Callback for bridge updates"""
        self.update_game_state(state_data)
    
    def stop_monitoring(self):
        """Stop packet monitoring"""
        self.monitoring = False
        self.connection_status.config(text="?? Stopped", fg='#ff0000')
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # Disconnect from bridge
        if self.bridge_connected and self.bridge_client:
            self.bridge_client.disconnect()
            self.bridge_connected = False
    
    def refresh_display(self):
        """Manually refresh the display"""
        self.refresh_ui()
        messagebox.showinfo("Refreshed", "Display refreshed!")
    
    def close_window(self):
        """Close the monitor window"""
        self.running = False
        
        # Disconnect from bridge
        if self.bridge_connected and self.bridge_client:
            self.bridge_client.disconnect()
        
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.root.destroy()
    
    def run(self):
        """Run the monitor window"""
        self.root.mainloop()


if __name__ == "__main__":
    # Configure ttk style for progress bars
    style = ttk.Style()
    style.theme_use('clam')
    
    monitor = GameStateMonitor()
    monitor.run()
