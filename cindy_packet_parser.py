# -*- coding: utf-8 -*-
"""
Cindy's Packet Parser
Parses EO protocol packets for game state monitoring
"""

from eolib.data.eo_reader import EoReader
from eolib.protocol.net.packet import Packet
from eolib.protocol.net import PacketFamily, PacketAction
import struct

class PacketParser:
    """Parser for Endless Online packets"""
    
    def __init__(self):
        self.last_stats = {
            'hp': 0,
            'max_hp': 100,
            'tp': 0,
            'max_tp': 100,
            'sp': 0,
            'max_sp': 0,
            'exp': 0,
            'level': 1,
            'gold': 0,
            'stat_points': 0,
            'skill_points': 0
        }
        self.last_position = {
            'x': 0,
            'y': 0,
            'direction': 0,
            'map_id': 0
        }
        self.sitting = False
        
    def parse_packet(self, packet_data):
        """
        Parse a packet and extract useful information
        Returns a dictionary with packet type and data
        """
        if len(packet_data) < 4:
            return None
        
        try:
            # Read packet header (2 bytes length, 1 byte family, 1 byte action)
            length = struct.unpack('<H', packet_data[0:2])[0]
            family = packet_data[2]
            action = packet_data[3]
            
            # Parse based on family/action
            if family == PacketFamily.STATSKILL.value:  # 0x0E
                return self.parse_stats_packet(packet_data[4:], action)
            elif family == PacketFamily.WALK.value:  # 0x06
                return self.parse_walk_packet(packet_data[4:], action)
            elif family == PacketFamily.WARP.value:  # 0x11
                return self.parse_warp_packet(packet_data[4:], action)
            elif family == PacketFamily.SIT.value:  # 0x26
                return self.parse_sit_packet(packet_data[4:], action)
            elif family == PacketFamily.ATTACK.value:  # 0x0A
                return self.parse_attack_packet(packet_data[4:], action)
            elif family == PacketFamily.ITEM.value:  # 0x0D
                return self.parse_item_packet(packet_data[4:], action)
            
            return {
                'type': 'unknown',
                'family': family,
                'action': action,
                'length': length
            }
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    def parse_stats_packet(self, data, action):
        """Parse STATSKILL packets for HP/TP/EXP/Gold"""
        try:
            reader = EoReader(data)
            
            # Action 0x08 (PLAYER) = full stats update
            if action == PacketAction.PLAYER.value:
                stats = {}
                
                # Stats packet structure (may vary by server):
                # HP, MaxHP, TP, MaxTP, (SP, MaxSP - if exists), 
                # Experience, Level, StatPoints, SkillPoints, ...
                
                try:
                    stats['hp'] = reader.get_short()
                    stats['max_hp'] = reader.get_short()
                    stats['tp'] = reader.get_short()
                    stats['max_tp'] = reader.get_short()
                    
                    # Try to read SP if it exists (some servers don't have it)
                    remaining = len(data) - reader.position
                    if remaining >= 8:  # SP + MaxSP + more
                        stats['sp'] = reader.get_short()
                        stats['max_sp'] = reader.get_short()
                    
                    # Experience and level
                    if remaining >= 12:
                        stats['exp'] = reader.get_int()
                        stats['level'] = reader.get_char()
                    
                    # Stat/skill points
                    if remaining >= 6:
                        stats['stat_points'] = reader.get_short()
                        stats['skill_points'] = reader.get_short()
                    
                    # Note: Gold is often in a separate packet or different position
                    # You may need to capture real packets to find exact position
                    
                except Exception as e:
                    # If we fail partway through, keep what we got
                    print(f"Stats partial parse: {e}")
                
                # Update cached stats
                self.last_stats.update(stats)
                
                return {
                    'type': 'stats_update',
                    'data': stats
                }
            
            return None
            
        except Exception as e:
            print(f"Stats parse error: {e}")
            return None
    
    def parse_walk_packet(self, data, action):
        """Parse WALK packets for position updates"""
        try:
            reader = EoReader(data)
            
            # Action 0x04 (AGREE) = movement confirmed by server
            if action == PacketAction.AGREE.value:
                pos = {}
                
                # Walk packet typically: PlayerID (optional), X, Y, Direction
                # Try reading with and without player ID
                try:
                    # Some servers include player ID, some don't
                    remaining = len(data)
                    if remaining >= 4:
                        # Try with player ID first
                        player_id = reader.get_short()
                        pos['player_id'] = player_id
                    
                    pos['x'] = reader.get_char()
                    pos['y'] = reader.get_char()
                    pos['direction'] = reader.get_char()
                    
                except Exception:
                    # If that fails, try without player ID
                    reader = EoReader(data)
                    pos['x'] = reader.get_char()
                    pos['y'] = reader.get_char()
                    pos['direction'] = reader.get_char()
                
                # Update cached position
                self.last_position.update(pos)
                
                return {
                    'type': 'position_update',
                    'data': pos
                }
            
            return None
            
        except Exception as e:
            print(f"Walk parse error: {e}")
            return None
    
    def parse_warp_packet(self, data, action):
        """Parse WARP packets for map changes"""
        try:
            reader = EoReader(data)
            
            # Action 0x01 (AGREE) = warp confirmed
            if action == PacketAction.AGREE.value:
                warp = {}
                
                # Warp packet: MapID, (optional: X, Y, session info)
                warp['map_id'] = reader.get_short()
                
                # Try to get spawn position if available
                try:
                    remaining = len(data) - reader.position
                    if remaining >= 2:
                        warp['x'] = reader.get_char()
                        warp['y'] = reader.get_char()
                        self.last_position.update(warp)
                except:
                    pass
                
                # Update map ID
                self.last_position['map_id'] = warp['map_id']
                
                return {
                    'type': 'map_change',
                    'data': warp
                }
            
            return None
            
        except Exception as e:
            print(f"Warp parse error: {e}")
            return None
    
    def parse_sit_packet(self, data, action):
        """Parse SIT packets for sitting status"""
        try:
            reader = EoReader(data)
            
            # Action 0x0C (PLAYER) = sit action
            if action == PacketAction.PLAYER.value:
                sit = {}
                
                # Sit packet: PlayerID (optional), SitState (0=standing, 1=sitting)
                try:
                    # Try with player ID
                    player_id = reader.get_short()
                    sit['player_id'] = player_id
                except:
                    reader = EoReader(data)
                
                sit_state = reader.get_char()
                sit['sitting'] = (sit_state == 1)
                
                # Update cached state
                self.sitting = sit['sitting']
                
                return {
                    'type': 'sit_status',
                    'data': sit
                }
            
            return None
            
        except Exception as e:
            print(f"Sit parse error: {e}")
            return None
    
    def parse_attack_packet(self, data, action):
        """Parse ATTACK packets for combat info"""
        try:
            reader = EoReader(data)
            
            # Action 0x05 (REPLY) = attack result
            if action == PacketAction.REPLY.value:
                attack = {}
                
                # Attack reply: Damage, HP remaining, etc.
                try:
                    attack['damage'] = reader.get_short()
                    attack['hp_remaining'] = reader.get_short()
                    # More fields may exist...
                except:
                    pass
                
                return {
                    'type': 'attack_result',
                    'data': attack
                }
            
            return None
            
        except Exception as e:
            print(f"Attack parse error: {e}")
            return None
    
    def parse_item_packet(self, data, action):
        """Parse ITEM packets for inventory/gold changes"""
        try:
            reader = EoReader(data)
            
            # Various item actions could contain gold updates
            # This is highly server-dependent
            
            return {
                'type': 'item_packet',
                'action': action,
                'data': {}
            }
            
        except Exception as e:
            print(f"Item parse error: {e}")
            return None
    
    def get_current_stats(self):
        """Get the last known stats"""
        return self.last_stats.copy()
    
    def get_current_position(self):
        """Get the last known position"""
        return self.last_position.copy()
    
    def get_sitting_status(self):
        """Get current sitting status"""
        return self.sitting


# Packet Family/Action constants (for reference)
class PacketType:
    # Families (from eolib)
    CONNECTION = 0x01
    ACCOUNT = 0x02
    CHARACTER = 0x03
    LOGIN = 0x04
    WELCOME = 0x05
    WALK = 0x06
    FACE = 0x07
    CHAIR = 0x08
    EMOTE = 0x09
    ATTACK = 0x0A
    SPELL = 0x0B
    SHOP = 0x0C
    ITEM = 0x0D
    STATSKILL = 0x0E
    GLOBAL = 0x0F
    TALK = 0x10
    WARP = 0x11
    JUKEBOX = 0x12
    PLAYERS = 0x13
    AVATAR = 0x14
    PARTY = 0x15
    REFRESH = 0x16
    NPC = 0x17
    PLAYERRANGE = 0x18
    NPCRANGE = 0x19
    RANGE = 0x1A
    PAPERDOLL = 0x1B
    EFFECT = 0x1C
    TRADE = 0x1D
    CHEST = 0x1E
    DOOR = 0x1F
    MESSAGE = 0x20
    BANK = 0x21
    LOCKER = 0x22
    BARBER = 0x23
    GUILD = 0x24
    MUSIC = 0x25
    SIT = 0x26
    RECOVER = 0x27
    BOARD = 0x28
    CAST = 0x29
    ARENA = 0x2A
    PRIEST = 0x2B
    MARRIAGE = 0x2C
    ADMININTERACT = 0x2D
    CITIZEN = 0x2E
    QUEST = 0x2F
    BOOK = 0x30
    
    # Common Actions
    REQUEST = 0x01
    ACCEPT = 0x02
    REPLY = 0x03
    AGREE = 0x04
    CREATE = 0x05
    ADD = 0x06
    PLAYER = 0x08
    REMOVE = 0x09
    TAKE = 0x0A
    USE = 0x0B
    BUY = 0x0C
    SELL = 0x0D
    OPEN = 0x0E
    CLOSE = 0x0F
    MESSAGE = 0x10
    SPEC = 0x11
    ADMIN = 0x12
    LIST = 0x13
    TELL = 0x14
