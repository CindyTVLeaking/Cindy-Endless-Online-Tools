"""
Cindy Utilities
Shared utility functions for Project Cindy
"""

def format_address(addr):
    """Format memory address as hex string"""
    if isinstance(addr, int):
        return f"0x{addr:08X}"
    return str(addr)

def validate_address_range(addr, min_addr, max_addr):
    """Validate if address is in expected range"""
    return min_addr <= addr <= max_addr

def calculate_distance(x1, y1, x2, y2):
    """Calculate Manhattan distance between two points"""
    return abs(x2 - x1) + abs(y2 - y1)
