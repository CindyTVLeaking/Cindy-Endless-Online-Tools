# -*- coding: utf-8 -*-
"""
Cindy Packet Bridge - Enhanced with proper EO packet parsing
Connects Packet Sniffer to Game State Monitor
"""

import threading
import queue
import time
import json
import socket
import struct

# EO Number Encoding (from eolib)
def decode_number(data, offset=0):
    """Decode EO-encoded number (1-4 bytes)"""
    try:
        if offset >= len(data):
            return 0
        
        b1 = data[offset]
        
        # Single byte (0-252)
        if b1 < 253:
            return b1
        
        # Two bytes (253-64008)
        if b1 == 253 and offset + 1 < len(data):
            b2 = data[offset + 1]
            return 253 + b2
        
        # Three bytes
        if b1 == 254 and offset + 2 < len(data):
            b2 = data[offset + 1]
            b3 = data[offset + 2]
            return 253 + 253 + (b2 * 253) + b3
        
        # Four bytes (max)
        if b1 == 255 and offset + 3 < len(data):
            b2 = data[offset + 1]
            b3 = data[offset + 2]
            b4 = data[offset + 3]
            return 253 + 253 + (253 * 253) + (b2 * 253 * 253) + (b3 * 253) + b4
        
        return 0
    except:
        return 0

def get_number_size(data, offset=0):
    """Get size of encoded number in bytes"""
    if offset >= len(data):
        return 0
    
    b1 = data[offset]
    if b1 < 253:
        return 1
    elif b1 == 253:
        return 2
    elif b1 == 254:
        return 3
    elif b1 == 255:
        return 4
    return 0


class PacketBridge:
    """Bridge between packet sniffer and game state monitor"""
    
    def __init__(self, host='localhost', port=9999):
        """Initialize packet bridge"""
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.clients = []
        
        # Game state cache
        self.game_state = {
            'hp': 0, 'max_hp': 0,  # Auto-detect from packets
            'tp': 0, 'max_tp': 0,
            'sp': 0, 'max_sp': 0,
            'exp': 0, 'level': 1,
            'gold': 0,
            'name': 'Unknown',
            'class': 'Peasant',
            'guild': 'None',
            'x': 0, 'y': 0,
            'map_id': 0,
            'map_name': 'Unknown',
            'sitting': False,
            'status': 'Unknown',
            'str': 0, 'int': 0,
            'wis': 0, 'agi': 0,
            'con': 0, 'cha': 0,
            'stat_points': 0,
            'skill_points': 0,
            'dps': 0.0,
            'hits': 0,
            'misses': 0,
            'kills': 0,
            'damage_dealt': 0,
            'inventory_used': 0,
            'inventory_max': 50,
            'weight': 0,
            'max_weight': 250,
            'buffs': []
        }
        
        # Combat tracking
        self.combat_start_time = None
        self.packets_processed = 0
    
    def start(self):
        """Start the bridge server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            # Start broadcast thread
            self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
            self.broadcast_thread.start()
            
            print(f"?? Packet Bridge started on {self.host}:{self.port}")
            print(f"   Enhanced EO packet parsing enabled")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start bridge: {e}")
            return False
    
    def stop(self):
        """Stop the bridge server"""
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("Packet Bridge stopped")
    
    def _server_loop(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"? Client connected from {addr}")
                self.clients.append(client_socket)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"ERROR: Accept failed: {e}")
                break
    
    def _broadcast_loop(self):
        """Broadcast game state to all clients"""
        while self.running:
            try:
                # Send current game state to all clients
                message = json.dumps({
                    'type': 'state_update',
                    'data': self.game_state
                })
                
                # Send to all clients
                dead_clients = []
                for client in self.clients:
                    try:
                        msg_bytes = message.encode('utf-8')
                        length = struct.pack('!I', len(msg_bytes))
                        client.sendall(length + msg_bytes)
                    except:
                        dead_clients.append(client)
                
                # Remove dead clients
                for client in dead_clients:
                    self.clients.remove(client)
                    try:
                        client.close()
                    except:
                        pass
                
                time.sleep(0.1)  # 10 Hz update rate
                
            except Exception as e:
                if self.running:
                    print(f"ERROR: Broadcast failed: {e}")
    
    def process_packet(self, packet_info):
        """Process a captured packet and update game state"""
        try:
            direction = packet_info.get('direction', '')
            family = packet_info.get('family', '')
            action = packet_info.get('action', '')
            data = packet_info.get('data', b'')
            
            # Only process server->client packets
            if 'SERVER' not in direction:
                return
            
            self.packets_processed += 1
            
            # Parse different packet types - SIMPLE VERSION
            if family == 'DOOR' and action == 'TARGETGROUP':
                self._parse_door_packet(data)
            elif family == 'STATSKILL':
                self._parse_statskill_packet(action, data)
            elif family == 'WALK':
                self._parse_walk_packet(action, data)
            elif family == 'WARP':
                self._parse_warp_packet(action, data)
            
        except Exception as e:
            # Silently ignore errors
            pass
    
    def _parse_door_packet(self, data):
        """Parse DOOR packet - Custom server uses this for HP healing"""
        try:
            if len(data) < 11:
                return
            
            # DOOR packet byte [10] shows HP value
            tick_or_hp = data[10]
            
            if tick_or_hp > 0 and tick_or_hp <= 255:
                # Update current HP
                self.game_state['hp'] = tick_or_hp
                
                # Auto-detect max HP
                if tick_or_hp > self.game_state.get('max_hp', 0):
                    self.game_state['max_hp'] = tick_or_hp
                    
        except Exception as e:
            pass
    
    def _parse_statskill_packet(self, action, data):
        """Parse STATSKILL packet"""
        try:
            if len(data) < 10:
                return
            
            offset = 4
            
            if action == 'PLAYER' or action == 'TARGET':
                # Skip player ID
                id_size = get_number_size(data, offset)
                offset += id_size
                
                # Try to read HP
                if offset < len(data):
                    self.game_state['hp'] = decode_number(data, offset)
                    offset += get_number_size(data, offset)
                
                # Try to read Max HP
                if offset < len(data):
                    self.game_state['max_hp'] = decode_number(data, offset)
                    offset += get_number_size(data, offset)
                    
        except Exception as e:
            pass
    
    def _parse_walk_packet(self, action, data):
        """Parse WALK packet for position"""
        try:
            if len(data) < 8:
                return
            
            offset = 4
            
            if action == 'PLAYER' or action == 'AGREE':
                # Skip player ID
                offset += get_number_size(data, offset)
                
                # Direction (1 byte)
                if offset < len(data):
                    offset += 1
                
                # X coordinate
                if offset < len(data):
                    self.game_state['x'] = decode_number(data, offset)
                    offset += get_number_size(data, offset)
                
                # Y coordinate
                if offset < len(data):
                    self.game_state['y'] = decode_number(data, offset)
                    
        except Exception as e:
            pass
    
    def _parse_warp_packet(self, action, data):
        """Parse WARP packet for map changes"""
        try:
            if len(data) < 6:
                return
            
            offset = 4
            if action == 'AGREE':
                self.game_state['map_id'] = decode_number(data, offset)
                
        except Exception as e:
            pass


class PacketBridgeClient:
    """Client for game state monitor to receive updates from bridge"""
    
    def __init__(self, host='localhost', port=9999):
        """Initialize bridge client"""
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        self.callback = None
        self.receive_thread = None
    
    def connect(self):
        """Connect to bridge server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            print(f"? Connected to packet bridge at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to connect to bridge: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from bridge server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("Disconnected from packet bridge")
    
    def set_callback(self, callback):
        """Set callback function for state updates"""
        self.callback = callback
    
    def _receive_loop(self):
        """Receive and process updates from bridge"""
        while self.running:
            try:
                # Receive message length
                length_data = self._recv_exactly(4)
                if not length_data:
                    break
                
                length = struct.unpack('!I', length_data)[0]
                
                # Receive message
                message_data = self._recv_exactly(length)
                if not message_data:
                    break
                
                # Parse JSON
                message = json.loads(message_data.decode('utf-8'))
                
                # Call callback if set
                if self.callback and message['type'] == 'state_update':
                    self.callback(message['data'])
                    
            except Exception as e:
                if self.running:
                    print(f"ERROR: Receive failed: {e}")
                break
        
        self.connected = False
        self.running = False
    
    def _recv_exactly(self, size):
        """Receive exactly size bytes"""
        data = b''
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data


if __name__ == "__main__":
    # Test the bridge
    print("Starting Packet Bridge...")
    
    bridge = PacketBridge()
    if bridge.start():
        print("Bridge started. Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping bridge...")
            bridge.stop()
    else:
        print("Failed to start bridge")
