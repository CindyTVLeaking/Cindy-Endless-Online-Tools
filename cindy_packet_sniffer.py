"""
Cindy Packet Sniffer - Network Traffic Analyzer for Endless Online
Captures and logs all packets between the EO client and server
Requires attachment to endless.exe process for security

Author: Kuuna
Version: 2.0.0
"""

import socket
import struct
import threading
import time
import queue
from datetime import datetime
from collections import defaultdict
import sys
import psutil
import pymem

# Try to import scapy for packet capture
try:
    from scapy.all import sniff, IP, TCP, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: scapy not installed. Install with: pip install scapy")

# Packet family and action names (from EO protocol)
PACKET_FAMILIES = {
    0x01: "CONNECTION",
    0x02: "ACCOUNT",
    0x03: "CHARACTER",
    0x04: "LOGIN",
    0x05: "WELCOME",
    0x06: "WALK",
    0x07: "FACE",
    0x08: "CHAIR",
    0x09: "EMOTE",
    0x0A: "ATTACK",
    0x0B: "SPELL",
    0x0C: "SHOP",
    0x0D: "ITEM",
    0x0E: "STATSKILL",
    0x0F: "GLOBAL",
    0x10: "TALK",
    0x11: "WARP",
    0x12: "JUKEBOX",
    0x13: "PLAYERS",
    0x14: "AVATAR",
    0x15: "PARTY",
    0x16: "REFRESH",
    0x17: "NPC",
    0x18: "PLAYERRANGE",
    0x19: "NPCRANGE",
    0x1A: "RANGE",
    0x1B: "PAPERDOLL",
    0x1C: "EFFECT",
    0x1D: "TRADE",
    0x1E: "CHEST",
    0x1F: "DOOR",
    0x20: "MESSAGE",
    0x21: "BANK",
    0x22: "LOCKER",
    0x23: "BARBER",
    0x24: "GUILD",
    0x25: "MUSIC",
    0x26: "SIT",
    0x27: "RECOVER",
    0x28: "BOARD",
    0x29: "CAST",
    0x2A: "ARENA",
    0x2B: "PRIEST",
    0x2C: "MARRIAGE",
    0x2D: "ADMININTERACT",
    0x2E: "CITIZENREPLY",
    0x2F: "QUEST",
    0xFF: "INIT"
}

PACKET_ACTIONS = {
    0x01: "REQUEST",
    0x02: "ACCEPT",
    0x03: "REPLY",
    0x04: "REMOVE",
    0x05: "AGREE",
    0x06: "CREATE",
    0x07: "ADD",
    0x08: "PLAYER",
    0x09: "TAKE",
    0x0A: "USE",
    0x0B: "BUY",
    0x0C: "SELL",
    0x0D: "OPEN",
    0x0E: "CLOSE",
    0x0F: "MESSAGE",
    0x10: "SPEC",
    0x11: "ADMIN",
    0x12: "LIST",
    0x13: "TELL",
    0x14: "REPORT",
    0x15: "ANNOUNCE",
    0x16: "SERVER",
    0x17: "DROP",
    0x18: "JUNK",
    0x19: "OBTAIN",
    0x1A: "GET",
    0x1B: "KICK",
    0x1C: "RANK",
    0x1D: "TARGET",
    0x1E: "TARGETGROUP",
    0x1F: "DIALOG",
    0x20: "PING",
    0x21: "PONG",
    0x22: "NET3",
    0x23: "INIT"
}


class PacketSniffer:
    """Captures and analyzes EO network packets - requires endless.exe attachment"""
    
    def __init__(self, eo_server_ip="69.10.49.30", eo_port=8078):
        """
        Initialize packet sniffer
        
        Args:
            eo_server_ip: IP address of EO server (default: 69.10.49.30 - Endless Online official server)
            eo_port: Port number of EO server (default: 8078)
        """
        self.server_ip = eo_server_ip
        self.port = eo_port
        self.running = False
        self.sniff_thread = None
        self.packet_queue = queue.Queue()
        
        # Process attachment state
        self.attached = False
        self.process = None
        self.pid = None
        
        # Packet bridge connection
        self.bridge = None
        self.bridge_enabled = False
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'client_to_server': 0,
            'server_to_client': 0,
            'by_family': defaultdict(int),
            'by_action': defaultdict(int),
            'start_time': None
        }
        
        # Packet log
        self.packet_log = []
        self.max_log_size = 1000
    
    def attach_to_endless(self):
        """Attach to endless.exe process"""
        print("\n" + "="*80)
        print("PROCESS ATTACHMENT")
        print("="*80)
        
        # Find all endless.exe processes
        endless_pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'endless.exe':
                    endless_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not endless_pids:
            print("ERROR: endless.exe not found. Please start Endless Online first.")
            return False
        
        # If multiple processes, let user choose
        if len(endless_pids) > 1:
            print(f"\nFound {len(endless_pids)} instances of endless.exe:")
            for i, pid in enumerate(endless_pids, 1):
                try:
                    proc = psutil.Process(pid)
                    create_time = datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')
                    memory_mb = proc.memory_info().rss / (1024 * 1024)
                    print(f"  {i}. PID: {pid:5d}  |  Started: {create_time}  |  Memory: {memory_mb:.1f} MB")
                except:
                    print(f"  {i}. PID: {pid:5d}")
            
            choice = input(f"\nSelect process (1-{len(endless_pids)}): ").strip()
            try:
                selected = int(choice) - 1
                if 0 <= selected < len(endless_pids):
                    self.pid = endless_pids[selected]
                else:
                    print("ERROR: Invalid selection")
                    return False
            except ValueError:
                print("ERROR: Invalid input")
                return False
        else:
            self.pid = endless_pids[0]
        
        # Try to attach
        try:
            pm = pymem.Pymem(self.pid)
            pm.close_process()  # Close immediately, just testing
            
            self.attached = True
            self.process = psutil.Process(self.pid)
            print(f"\n? Successfully attached to endless.exe (PID: {self.pid})")
            print(f"? Ready to capture packets from {self.server_ip}:{self.port}")
            return True
            
        except Exception as e:
            print(f"\nERROR: Failed to attach to process: {e}")
            return False
    
    def detach(self):
        """Detach from process"""
        self.attached = False
        self.process = None
        self.pid = None
        print("\nDetached from endless.exe")
    
    def start(self):
        """Start packet capture - requires endless.exe attachment"""
        if not SCAPY_AVAILABLE:
            print("ERROR: scapy library not available. Cannot start packet capture.")
            return False
        
        if not self.attached:
            print("ERROR: Not attached to endless.exe. Please attach first!")
            return False
        
        if self.running:
            print("Packet sniffer already running")
            return False
        
        # Verify process is still running
        if not self.process.is_running():
            print("ERROR: endless.exe process has terminated. Please reattach.")
            self.attached = False
            return False
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Start capture thread
        self.sniff_thread = threading.Thread(target=self._capture_packets, daemon=True)
        self.sniff_thread.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_packets, daemon=True)
        self.process_thread.start()
        
        print(f"[{self._timestamp()}] Packet sniffer started")
        print(f"Monitoring traffic to/from {self.server_ip}:{self.port}")
        print(f"Attached to endless.exe (PID: {self.pid})")
        return True
    
    def stop(self):
        """Stop packet capture"""
        if not self.running:
            return
        
        self.running = False
        print(f"\n[{self._timestamp()}] Packet sniffer stopped")
        self._print_statistics()
    
    def _capture_packets(self):
        """Capture packets using scapy"""
        try:
            # Filter for EO server traffic
            filter_str = f"tcp and (host {self.server_ip} and port {self.port})"
            
            print(f"[{self._timestamp()}] Starting packet capture...")
            print(f"Filter: {filter_str}")
            
            sniff(
                filter=filter_str,
                prn=self._packet_callback,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            print(f"ERROR: Packet capture failed: {e}")
            self.running = False
    
    def _packet_callback(self, packet):
        """Callback for captured packets"""
        if not self.running:
            return
        
        try:
            if IP in packet and TCP in packet and Raw in packet:
                # Get packet data
                ip_layer = packet[IP]
                tcp_layer = packet[TCP]
                raw_data = bytes(packet[Raw])
                
                # Determine direction
                if ip_layer.dst == self.server_ip:
                    direction = "CLIENT->SERVER"
                    self.stats['client_to_server'] += 1
                else:
                    direction = "SERVER->CLIENT"
                    self.stats['server_to_client'] += 1
                
                # Queue for processing
                self.packet_queue.put({
                    'timestamp': time.time(),
                    'direction': direction,
                    'data': raw_data,
                    'src_ip': ip_layer.src,
                    'dst_ip': ip_layer.dst,
                    'src_port': tcp_layer.sport,
                    'dst_port': tcp_layer.dport,
                    'seq': tcp_layer.seq,
                    'flags': tcp_layer.flags
                })
                
        except Exception as e:
            print(f"ERROR: Packet processing failed: {e}")
    
    def _process_packets(self):
        """Process captured packets from queue"""
        while self.running:
            try:
                # Get packet from queue (with timeout)
                packet = self.packet_queue.get(timeout=0.1)
                
                # Parse EO packet structure
                self._parse_eo_packet(packet)
                
                # Update stats
                self.stats['total_packets'] += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"ERROR: Packet analysis failed: {e}")
    
    def _parse_eo_packet(self, packet):
        """Parse EO packet structure and log"""
        data = packet['data']
        
        if len(data) < 2:
            return  # Too small to be valid EO packet
        
        try:
            # EO packets start with 2-byte length, then family and action
            if len(data) >= 4:
                # Try to parse as EO packet
                length = struct.unpack('<H', data[0:2])[0]
                family = data[2]
                action = data[3]
                
                # Get names
                family_name = PACKET_FAMILIES.get(family, f"UNKNOWN_0x{family:02X}")
                action_name = PACKET_ACTIONS.get(action, f"UNKNOWN_0x{action:02X}")
                
                # Update stats
                self.stats['by_family'][family_name] += 1
                self.stats['by_action'][action_name] += 1
                
                # Log packet - store FULL data for bridge!
                log_entry = {
                    'timestamp': datetime.fromtimestamp(packet['timestamp']).strftime('%H:%M:%S.%f')[:-3],
                    'direction': packet['direction'],
                    'family': family_name,
                    'action': action_name,
                    'length': len(data),
                    'raw_data': data.hex()[:100],  # Truncated for display
                    'full_data': data  # FULL data for bridge!
                }
                
                self._log_packet(log_entry)
                
        except Exception as e:
            # Not a valid EO packet, skip
            pass
    
    def _log_packet(self, entry):
        """Log packet information"""
        # Add to log
        self.packet_log.append(entry)
        
        # Trim log if too large
        if len(self.packet_log) > self.max_log_size:
            self.packet_log = self.packet_log[-self.max_log_size:]
        
        # DIAGNOSTIC: Full hex dump for important packets
        # Dump by RAW FAMILY ID (hex values), not names!
        full_data = entry.get('full_data', b'')
        if full_data and len(full_data) >= 3:
            family_id = full_data[2]  # Get raw family byte
            
            # Dump these family IDs:
            # 0x03 = CHARACTER
            # 0x06 = WALK  
            # 0x0E = STATSKILL
            # 0x1C = EFFECT (damage numbers)
            # 0x27 = RECOVER (HP/TP healing - standard EO)
            # 0x2D = "ADMININTERACT" (but might be movement!)
            # 0xE1 = UNKNOWN (skill casting?)
            # 0xE3 = UNKNOWN (might be healing response!)
            # 0xFB = Whatever this is (you get lots - might contain HP!)
            if family_id in [0x03, 0x06, 0x0E, 0x1C, 0x27, 0x2D, 0xE1, 0xE3, 0xFB]:  # Added more!
                print(f"\n{'='*60}")
                print(f"FULL PACKET DUMP: {entry['family']} / {entry['action']}")
                print(f"Direction: {entry['direction']}")
                print(f"Family ID: 0x{family_id:02X} ({family_id})")
                print(f"Length: {len(full_data)} bytes")
                print(f"Full Hex: {full_data.hex()}")
                print(f"Bytes: {' '.join(f'{b:02x}' for b in full_data)}")
                
                # Try to decode EO numbers from offset 4 onwards
                if len(full_data) > 4:
                    print(f"\nDecoding from offset 4:")
                    offset = 4
                    nums = []
                    while offset < len(full_data) and len(nums) < 20:  # More numbers!
                        b = full_data[offset]
                        if b < 253:
                            nums.append(f"[{offset}]={b}")
                            offset += 1
                        elif b == 253 and offset + 1 < len(full_data):
                            val = 253 + full_data[offset + 1]
                            nums.append(f"[{offset}]={val}")
                            offset += 2
                        elif b == 254 and offset + 2 < len(full_data):
                            val = 253 + 253 + (full_data[offset + 1] * 253) + full_data[offset + 2]
                            nums.append(f"[{offset}]={val}")
                            offset += 3
                        elif b == 255 and offset + 3 < len(full_data):
                            val = 253 + 253 + (253 * 253) + (full_data[offset + 1] * 253 * 253) + (full_data[offset + 2] * 253) + full_data[offset + 3]
                            nums.append(f"[{offset}]={val}")
                            offset += 4
                        else:
                            break
                    print(f"Decoded numbers: {', '.join(nums)}")
                print(f"{'='*60}\n")
        
        # Send to bridge if enabled
        if self.bridge_enabled and self.bridge:
            try:
                full_data = entry.get('full_data')
                
                if full_data:
                    packet_info = {
                        'direction': entry['direction'],
                        'family': entry['family'],
                        'action': entry['action'],
                        'data': full_data
                    }
                    
                    self.bridge.process_packet(packet_info)
                    
            except Exception as e:
                # Only log critical errors
                if entry['family'] in ['STATSKILL', 'WALK', 'WARP', 'RECOVER', 'ATTACK']:
                    print(f"[ERROR] Bridge failed for {entry['family']}: {e}")
        
        # Print to console (use truncated for display)
        print(f"[{entry['timestamp']}] {entry['direction']:18s} | "
              f"{entry['family']:15s} / {entry['action']:15s} | "
              f"Len: {entry['length']:4d} | "
              f"Data: {entry['raw_data'][:40]}...")
    
    def _print_statistics(self):
        """Print capture statistics"""
        runtime = time.time() - self.stats['start_time']
        
        print("\n" + "="*80)
        print("PACKET CAPTURE STATISTICS")
        print("="*80)
        print(f"Runtime: {runtime:.1f} seconds")
        print(f"Total Packets: {self.stats['total_packets']}")
        print(f"  Client->Server: {self.stats['client_to_server']}")
        print(f"  Server->Client: {self.stats['server_to_client']}")
        print(f"  Rate: {self.stats['total_packets']/runtime:.1f} packets/sec")
        
        print("\nTop Packet Families:")
        top_families = sorted(self.stats['by_family'].items(), key=lambda x: x[1], reverse=True)[:10]
        for family, count in top_families:
            print(f"  {family:20s}: {count:4d} ({count/self.stats['total_packets']*100:.1f}%)")
        
        print("\nTop Packet Actions:")
        top_actions = sorted(self.stats['by_action'].items(), key=lambda x: x[1], reverse=True)[:10]
        for action, count in top_actions:
            print(f"  {action:20s}: {count:4d} ({count/self.stats['total_packets']*100:.1f}%)")
        
        print("="*80)
    
    def save_log(self, filename="packet_log.txt"):
        """Save packet log to file"""
        try:
            with open(filename, 'w') as f:
                f.write("ENDLESS ONLINE PACKET LOG\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for entry in self.packet_log:
                    f.write(f"[{entry['timestamp']}] {entry['direction']:18s} | "
                           f"{entry['family']:15s} / {entry['action']:15s} | "
                           f"Len: {entry['length']:4d}\n")
                    f.write(f"  Data: {entry['raw_data']}\n\n")
                
                # Write statistics
                f.write("\n" + "="*80 + "\n")
                f.write("STATISTICS\n")
                f.write("="*80 + "\n")
                runtime = time.time() - self.stats['start_time']
                f.write(f"Total Packets: {self.stats['total_packets']}\n")
                f.write(f"Runtime: {runtime:.1f} seconds\n")
                
            print(f"[{self._timestamp()}] Packet log saved to {filename}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save log: {e}")
            return False
    
    def enable_bridge(self):
        """Enable packet bridge for live monitoring"""
        try:
            from cindy_packet_bridge import PacketBridge
            
            self.bridge = PacketBridge()
            if self.bridge.start():
                self.bridge_enabled = True
                print("? Packet bridge enabled - Game State Monitor can now connect!")
                print(f"   Bridge listening on localhost:9999")
                return True
            else:
                print("? Failed to start packet bridge")
                return False
                
        except Exception as e:
            print(f"? Failed to enable bridge: {e}")
            return False
    
    def disable_bridge(self):
        """Disable packet bridge"""
        if self.bridge:
            self.bridge.stop()
            self.bridge = None
            self.bridge_enabled = False
            print("Packet bridge disabled")
    
    @staticmethod
    def _timestamp():
        """Get current timestamp string"""
        return datetime.now().strftime('%H:%M:%S')


def main():
    """Main function"""
    try:
        print("\n")
        print("?" + "="*78 + "?")
        print("?" + " "*20 + "CINDY PACKET SNIFFER" + " "*38 + "?")
        print("?" + " "*15 + "Network Traffic Analyzer for Endless Online" + " "*20 + "?")
        print("?" + " "*25 + "Requires endless.exe Attachment" + " "*23 + "?")
        print("?" + "="*78 + "?")
        print()
        
        # Check requirements
        if not SCAPY_AVAILABLE:
            print("ERROR: scapy library required")
            print("Install with: pip install scapy")
            print("\nOn Windows, you may also need to install Npcap:")
            print("https://npcap.com/#download")
            return 1
        
        # Server is pre-configured
        server_ip = "69.10.49.30"
        port = 8078
        
        print("Server Configuration:")
        print(f"  IP: {server_ip} (Endless Online Official Server)")
        print(f"  Port: {port}")
        print()
        
        # Create sniffer
        sniffer = PacketSniffer(server_ip, port)
        
        # Attach to endless.exe
        print("="*80)
        print("STEP 1: ATTACH TO ENDLESS.EXE")
        print("="*80)
        print("The packet sniffer must attach to endless.exe for security.")
        print("Make sure Endless Online is running before proceeding.")
        print()
        
        try:
            input("Press ENTER to attach to endless.exe...")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            return 0
        
        if not sniffer.attach_to_endless():
            print("\nFailed to attach to endless.exe. Exiting.")
            return 1
        
        print("\n" + "="*80)
        print("STEP 2: ENABLE LIVE MONITORING (OPTIONAL)")
        print("="*80)
        print("Enable packet bridge to send data to Game State Monitor?")
        print("This allows real-time stat tracking in a separate window.")
        print()
        
        try:
            enable = input("Enable bridge? (y/n): ").strip().lower()
            if enable == 'y':
                sniffer.enable_bridge()
        except (KeyboardInterrupt, EOFError):
            print("\nSkipping bridge setup.")
        
        print("\n" + "="*80)
        print("STEP 3: START PACKET CAPTURE")
        print("="*80)
        print("Ready to capture network traffic!")
        print("Perform actions in-game to see packets.")
        print("Press Ctrl+C to stop capture and view statistics.")
        print("="*80)
        
        try:
            input("\nPress ENTER to start capture...")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            if sniffer.attached:
                sniffer.detach()
            return 0
        
        # Start capture
        if not sniffer.start():
            print("\nFailed to start packet capture.")
            return 1
        
        try:
            # Monitor process and keep running
            while sniffer.running:
                # Check if endless.exe is still running
                if not sniffer.process.is_running():
                    print("\n\nWARNING: endless.exe has terminated. Stopping capture...")
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\nStopping packet capture...")
        
        # Stop sniffer
        sniffer.stop()
        
        # Detach from process
        if sniffer.attached:
            sniffer.detach()
        
        # Ask to save log
        try:
            save = input("\nSave packet log to file? (y/n): "),
            if save == 'y':
                filename = input("Enter filename (default: packet_log.txt): ").strip() or "packet_log.txt"
                sniffer.save_log(filename)
        except (KeyboardInterrupt, EOFError):
            print("\n\nSkipping log save.")
        
        print("\nPacket sniffer terminated.")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n? Operation cancelled by user (Ctrl+C)")
        return 0
    except Exception as e:
        print(f"\n\n? Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
