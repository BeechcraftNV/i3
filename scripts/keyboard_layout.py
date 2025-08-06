#!/usr/bin/env python3
"""
Visual keyboard layout generator for i3 keybindings.
Generates ASCII representations of keyboards with highlighted keys.
"""

from typing import Dict, List, Optional, Tuple

class KeyboardLayout:
    """Generates visual keyboard layouts with highlighted keys"""
    
    def __init__(self, layout: str = 'us'):
        self.layout = layout
        
        # US QWERTY layout definition
        self.us_layout = {
            'row1': ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
            'row2': ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            'row3': ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"],
            'row4': ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
            'row5': ['Ctrl', 'Super', 'Alt', 'Space', 'Alt', 'Super', 'Menu', 'Ctrl']
        }
        
        # Function keys
        self.function_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        
        # Special keys mapping
        self.key_mappings = {
            'Return': 'Enter',
            'BackSpace': 'Bksp',
            'space': 'Space',
            'Left': '←',
            'Right': '→', 
            'Up': '↑',
            'Down': '↓',
            'Print': 'PrtSc',
            'Prior': 'PgUp',
            'Next': 'PgDn',
            'Home': 'Home',
            'End': 'End',
            'Insert': 'Ins',
            'Delete': 'Del',
            'Escape': 'Esc'
        }
    
    def normalize_key(self, key: str) -> str:
        """Normalize key names for display"""
        # Handle modifier combinations
        if '+' in key:
            parts = key.split('+')
            return '+'.join(self.key_mappings.get(part.strip(), part.strip()) for part in parts)
        
        return self.key_mappings.get(key, key)
    
    def generate_compact_layout(self, highlighted_keys: List[str]) -> str:
        """Generate a compact keyboard layout with highlighted keys"""
        lines = []
        
        # Normalize highlighted keys
        normalized_keys = [self.normalize_key(key.lower()) for key in highlighted_keys]
        
        # Function keys row
        f_keys = []
        for fkey in self.function_keys:
            if fkey.lower() in [k.lower() for k in normalized_keys]:
                f_keys.append(f"[{fkey}]")
            else:
                f_keys.append(f" {fkey} ")
        
        lines.append("┌" + "─" * 60 + "┐")
        lines.append("│ " + " ".join(f_keys) + " │")
        lines.append("├" + "─" * 60 + "┤")
        
        # Main keyboard rows
        for row_name, keys in self.us_layout.items():
            if row_name == 'row5':  # Bottom row (spacebar row)
                continue
                
            row_display = []
            for key in keys:
                display_key = self.key_mappings.get(key, key)
                key_lower = key.lower()
                
                # Check if this key should be highlighted
                if (key_lower in [k.lower() for k in normalized_keys] or
                    any(key_lower in nk.lower() for nk in normalized_keys)):
                    if len(display_key) == 1:
                        row_display.append(f"[{display_key.upper()}]")
                    else:
                        row_display.append(f"[{display_key[:4]}]")
                else:
                    if len(display_key) == 1:
                        row_display.append(f" {display_key.upper()} ")
                    else:
                        row_display.append(f"{display_key[:4]:^4}")
            
            lines.append("│ " + " ".join(row_display).ljust(58) + " │")
        
        # Special keys row (arrows, etc.)
        special_keys = ['←', '↓', '↑', '→', 'PrtSc', 'Home', 'PgUp', 'PgDn', 'End', 'Ins', 'Del']
        special_display = []
        
        for key in special_keys:
            if any(key.lower() in nk.lower() for nk in normalized_keys):
                special_display.append(f"[{key}]")
            else:
                special_display.append(f" {key} ")
        
        lines.append("│ " + " ".join(special_display).ljust(58) + " │")
        lines.append("└" + "─" * 60 + "┘")
        
        return "\n".join(lines)
    
    def generate_focused_view(self, key_combination: str) -> str:
        """Generate a focused view of specific key combination"""
        parts = key_combination.split('+')
        
        result = []
        result.append("Key Combination Breakdown:")
        result.append("=" * 30)
        
        for i, part in enumerate(parts):
            normalized = self.normalize_key(part.strip())
            if i == 0:
                result.append(f"Primary: {normalized}")
            else:
                result.append(f"+ Modifier: {normalized}")
        
        result.append("")
        result.append("Visual Representation:")
        
        # Simple visual for the combination
        visual_parts = []
        for part in parts:
            normalized = self.normalize_key(part.strip())
            visual_parts.append(f"[{normalized}]")
        
        result.append(" + ".join(visual_parts))
        
        return "\n".join(result)
    
    def get_key_location_hint(self, key: str) -> str:
        """Get a hint about where a key is located"""
        key_lower = key.lower()
        
        # Check each row
        for row_name, keys in self.us_layout.items():
            # Check if key matches any key in this row (case insensitive)
            for k in keys:
                if k.lower() == key_lower:
                    row_descriptions = {
                        'row1': 'Number row (top)',
                        'row2': 'QWERTY row', 
                        'row3': 'Home row (ASDF)',
                        'row4': 'Bottom letter row',
                        'row5': 'Space bar row'
                    }
                    position = keys.index(k) + 1
                    return f"Located on {row_descriptions.get(row_name, row_name)}, position {position}"
        
        # Check function keys
        if key.upper() in self.function_keys:
            return f"Function key row, {key.upper()}"
        
        # Special keys and modifiers
        special_locations = {
            'print': 'Above arrow keys area',
            'home': 'Navigation cluster', 
            'end': 'Navigation cluster',
            'pageup': 'Navigation cluster',
            'pagedown': 'Navigation cluster',
            'insert': 'Navigation cluster',
            'delete': 'Navigation cluster',
            'super': 'Bottom row (Windows key)',
            'mod4': 'Bottom row (Windows key)',
            'ctrl': 'Bottom corners',
            'alt': 'Bottom row (both sides)',
            'shift': 'Left and right sides',
            'escape': 'Top-left corner',
            'return': 'Right side of home row',
            'enter': 'Right side of home row',
            'backspace': 'Top row, far right',
            'tab': 'Left side of QWERTY row'
        }
        
        return special_locations.get(key_lower, "Location unknown")

def demo():
    """Demo function showing keyboard layout capabilities"""
    layout = KeyboardLayout()
    
    # Example highlighted keys
    test_keys = ['Super+Return', 'Print', 'F4', 'Ctrl+c']
    
    print("Compact Keyboard Layout:")
    print(layout.generate_compact_layout(['Super', 'Return', 'Print', 'F4', 'Ctrl', 'c']))
    print()
    
    print("Focused View:")
    print(layout.generate_focused_view('Super+Shift+q'))
    print()
    
    print("Key Location Hints:")
    for key in ['q', 'Print', 'F1', 'Super']:
        print(f"{key}: {layout.get_key_location_hint(key)}")

if __name__ == '__main__':
    demo()
