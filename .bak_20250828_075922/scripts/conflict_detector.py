#!/usr/bin/env python3
"""
Keybinding Conflict Detector for i3
Finds duplicate, overlapping, and potentially conflicting keybindings
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import subprocess

class KeybindingConflictDetector:
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path.home() / '.config' / 'i3' / 'config'
        
        self.config_path = config_path
        self.bindings = []
        self.modes = {}
        self.conflicts = {
            'duplicates': [],
            'shadows': [],
            'similar': [],
            'mode_conflicts': [],
            'system_conflicts': [],
            'ergonomic_issues': [],
            'unused_combinations': []
        }
        
        # Common system shortcuts that might conflict
        self.system_shortcuts = {
            'Alt+Tab': 'System window switcher',
            'Alt+F4': 'Close application',
            'Ctrl+Alt+Delete': 'System menu',
            'Ctrl+Alt+F1-F7': 'TTY switching',
            'Print': 'System screenshot',
            'Super+L': 'System lock (some distros)',
        }
        
        # Ergonomic difficulty scores
        self.difficulty_scores = {
            'easy': ['$mod+a-z', '$mod+1-9', '$mod+Return', '$mod+space'],
            'medium': ['$mod+Shift+a-z', '$mod+Ctrl+a-z', '$mod+F1-F12'],
            'hard': ['$mod+Shift+Ctrl+a-z', '$mod+Alt+Shift+a-z'],
            'very_hard': ['$mod+Shift+Ctrl+Alt+a-z']
        }
    
    def parse_config(self) -> bool:
        """Parse i3 config file for all keybindings"""
        if not self.config_path.exists():
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading config: {e}")
            return False
        
        current_mode = None
        mode_depth = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Detect mode blocks
            if line.startswith('mode '):
                mode_match = re.match(r'mode\s+"([^"]+)"', line)
                if mode_match:
                    current_mode = mode_match.group(1)
                    mode_depth = 1
                    if current_mode not in self.modes:
                        self.modes[current_mode] = []
                continue
            
            # Track mode depth
            if '{' in line:
                mode_depth += line.count('{')
            if '}' in line:
                mode_depth -= line.count('}')
                if mode_depth <= 0:
                    current_mode = None
                    mode_depth = 0
            
            # Parse bindsym and bindcode
            bind_match = re.match(r'^(bindsym|bindcode)\s+(--\S+\s+)*(.+?)\s+(.+)$', line)
            if bind_match:
                bind_type = bind_match.group(1)
                modifiers = bind_match.group(2) or ''
                key_combo = bind_match.group(3)
                command = bind_match.group(4)
                
                # Normalize key combination
                normalized_key = self.normalize_key(key_combo)
                
                binding = {
                    'type': bind_type,
                    'key': key_combo,
                    'normalized_key': normalized_key,
                    'command': command,
                    'line': line_num,
                    'mode': current_mode,
                    'modifiers': modifiers.strip(),
                    'original_line': line
                }
                
                self.bindings.append(binding)
                
                if current_mode:
                    self.modes[current_mode].append(binding)
        
        return True
    
    def normalize_key(self, key: str) -> str:
        """Normalize key combination for comparison"""
        # Replace $mod with Mod4 (or actual mod key)
        normalized = key.replace('$mod', 'Mod4')
        
        # Sort modifiers for consistent comparison
        parts = normalized.split('+')
        if len(parts) > 1:
            *modifiers, key_part = parts
            modifiers.sort()
            normalized = '+'.join(modifiers + [key_part])
        
        return normalized.lower()
    
    def detect_conflicts(self):
        """Detect all types of conflicts"""
        self.detect_duplicates()
        self.detect_shadows()
        self.detect_similar_bindings()
        self.detect_mode_conflicts()
        self.detect_system_conflicts()
        self.detect_ergonomic_issues()
        self.suggest_unused_combinations()
    
    def detect_duplicates(self):
        """Find exact duplicate keybindings"""
        seen = defaultdict(list)
        
        for binding in self.bindings:
            key = (binding['normalized_key'], binding['mode'])
            seen[key].append(binding)
        
        for key, bindings in seen.items():
            if len(bindings) > 1:
                self.conflicts['duplicates'].append({
                    'key': bindings[0]['key'],
                    'mode': bindings[0]['mode'] or 'default',
                    'bindings': bindings,
                    'severity': 'high',
                    'description': f"Key '{bindings[0]['key']}' is bound {len(bindings)} times"
                })
    
    def detect_shadows(self):
        """Find bindings that might shadow each other"""
        # Check for prefix shadows (e.g., $mod+w shadows $mod+w+a)
        for i, binding1 in enumerate(self.bindings):
            for binding2 in self.bindings[i+1:]:
                if binding1['mode'] == binding2['mode']:
                    if binding2['normalized_key'].startswith(binding1['normalized_key'] + '+'):
                        self.conflicts['shadows'].append({
                            'shadower': binding1,
                            'shadowed': binding2,
                            'severity': 'medium',
                            'description': f"'{binding1['key']}' may prevent '{binding2['key']}' from working"
                        })
    
    def detect_similar_bindings(self):
        """Find visually or functionally similar bindings that might confuse users"""
        similar_keys = [
            ('l', '1'), ('O', '0'), ('I', 'l'),
            ('b', 'd'), ('p', 'q'), ('m', 'n')
        ]
        
        for binding1 in self.bindings:
            for binding2 in self.bindings:
                if binding1 != binding2 and binding1['mode'] == binding2['mode']:
                    # Check for similar looking keys
                    for pair in similar_keys:
                        if pair[0] in binding1['key'] and pair[1] in binding2['key']:
                            key1_with_sub = binding1['key'].replace(pair[0], pair[1])
                            if key1_with_sub == binding2['key']:
                                self.conflicts['similar'].append({
                                    'binding1': binding1,
                                    'binding2': binding2,
                                    'severity': 'low',
                                    'description': f"'{binding1['key']}' and '{binding2['key']}' are visually similar"
                                })
                                break
    
    def detect_mode_conflicts(self):
        """Check for conflicts between modes and default bindings"""
        default_bindings = [b for b in self.bindings if b['mode'] is None]
        
        for mode_name, mode_bindings in self.modes.items():
            for mode_binding in mode_bindings:
                for default_binding in default_bindings:
                    if mode_binding['normalized_key'] == default_binding['normalized_key']:
                        self.conflicts['mode_conflicts'].append({
                            'mode': mode_name,
                            'mode_binding': mode_binding,
                            'default_binding': default_binding,
                            'severity': 'medium',
                            'description': f"Mode '{mode_name}' overrides default binding '{default_binding['key']}'"
                        })
    
    def detect_system_conflicts(self):
        """Check for conflicts with common system shortcuts"""
        for binding in self.bindings:
            for sys_key, sys_desc in self.system_shortcuts.items():
                if self.normalize_key(sys_key) == binding['normalized_key']:
                    self.conflicts['system_conflicts'].append({
                        'binding': binding,
                        'system_key': sys_key,
                        'system_function': sys_desc,
                        'severity': 'medium',
                        'description': f"'{binding['key']}' conflicts with system shortcut for {sys_desc}"
                    })
    
    def detect_ergonomic_issues(self):
        """Detect ergonomically difficult key combinations"""
        # Patterns that are hard to press
        difficult_patterns = [
            (r'.*Shift.*Ctrl.*Alt.*', 'Too many modifiers (4+)'),
            (r'.*[zxcv].*Shift.*[plo\[\]].*', 'Requires hand stretching'),
            (r'.*Shift.*[1234567890].*', 'Shift+number keys are error-prone'),
        ]
        
        for binding in self.bindings:
            # Check against difficult patterns
            for pattern, reason in difficult_patterns:
                if re.match(pattern, binding['key'], re.IGNORECASE):
                    self.conflicts['ergonomic_issues'].append({
                        'binding': binding,
                        'reason': reason,
                        'severity': 'low',
                        'description': f"'{binding['key']}' is ergonomically difficult: {reason}",
                        'suggestion': self.suggest_alternative(binding['key'])
                    })
                    break
            
            # Check for frequently used commands with difficult bindings
            if any(common in binding['command'].lower() for common in ['terminal', 'browser', 'close']):
                if '+Shift+Ctrl' in binding['key'] or '+Ctrl+Alt' in binding['key']:
                    self.conflicts['ergonomic_issues'].append({
                        'binding': binding,
                        'reason': 'Common command with complex binding',
                        'severity': 'medium',
                        'description': f"Frequently used '{binding['command']}' has complex binding '{binding['key']}'",
                        'suggestion': self.suggest_alternative(binding['key'])
                    })
    
    def suggest_alternative(self, current_key: str) -> str:
        """Suggest an ergonomic alternative for a key binding"""
        # Extract the base key
        parts = current_key.split('+')
        base_key = parts[-1]
        
        # Suggest simpler modifier combinations
        if '+Shift+Ctrl+' in current_key:
            return current_key.replace('+Shift+Ctrl+', '+Alt+')
        elif '+Ctrl+Alt+' in current_key:
            return current_key.replace('+Ctrl+Alt+', '+Shift+')
        elif len(parts) > 3:
            # Too many modifiers, suggest using just $mod+Shift
            return f"$mod+Shift+{base_key}"
        
        return f"$mod+Alt+{base_key}"
    
    def suggest_unused_combinations(self):
        """Suggest good unused key combinations"""
        # Common keys that are good for bindings
        good_keys = list('asdfghjklqwertyuiopzxcvbnm') + \
                   ['Return', 'space', 'Tab', 'Escape'] + \
                   [f'F{i}' for i in range(1, 13)]
        
        # Modifier combinations ordered by ergonomics
        modifier_combos = [
            '$mod+',
            '$mod+Shift+',
            '$mod+Alt+',
            '$mod+Ctrl+'
        ]
        
        used_keys = set(b['key'] for b in self.bindings)
        unused = []
        
        for modifier in modifier_combos:
            for key in good_keys:
                combo = modifier + key
                if combo not in used_keys and len(unused) < 20:
                    unused.append({
                        'key': combo,
                        'ergonomic_score': self.get_ergonomic_score(combo),
                        'suggestion': self.suggest_use_for_key(combo)
                    })
        
        # Sort by ergonomic score
        unused.sort(key=lambda x: x['ergonomic_score'], reverse=True)
        self.conflicts['unused_combinations'] = unused[:10]
    
    def get_ergonomic_score(self, key_combo: str) -> int:
        """Rate ergonomic ease of a key combination (0-100)"""
        score = 100
        
        # Penalty for multiple modifiers
        modifier_count = key_combo.count('+') 
        score -= (modifier_count - 1) * 15
        
        # Penalty for Ctrl+Alt combination
        if 'Ctrl' in key_combo and 'Alt' in key_combo:
            score -= 20
        
        # Bonus for home row keys
        home_row = 'asdfghjkl'
        if any(k in key_combo.lower() for k in home_row):
            score += 10
        
        # Penalty for number keys with Shift
        if 'Shift' in key_combo and any(str(i) in key_combo for i in range(10)):
            score -= 15
        
        return max(0, min(100, score))
    
    def suggest_use_for_key(self, key_combo: str) -> str:
        """Suggest what a key combination could be used for"""
        suggestions = {
            'a': 'applications/all',
            'b': 'browser/bookmarks',
            'c': 'copy/close/config',
            'd': 'desktop/dmenu',
            'e': 'editor/exit',
            'f': 'files/find/fullscreen',
            'g': 'go to/grep',
            'h': 'help/left',
            'i': 'insert/info',
            'j': 'down/jump',
            'k': 'up/kill',
            'l': 'right/lock/list',
            'm': 'minimize/mark/music',
            'n': 'new/next',
            'o': 'open',
            'p': 'paste/previous/print',
            'q': 'quit',
            'r': 'reload/refresh/resize',
            's': 'save/search/screenshot',
            't': 'terminal/tab',
            'u': 'undo',
            'v': 'paste/vertical/volume',
            'w': 'window/workspace',
            'x': 'cut/execute',
            'y': 'yank/yes',
            'z': 'undo/zoom',
            'Return': 'confirm/terminal',
            'space': 'launcher/toggle',
            'Tab': 'switch/cycle',
            'Escape': 'cancel/exit mode'
        }
        
        base_key = key_combo.split('+')[-1].lower()
        return suggestions.get(base_key, 'custom action')
    
    def generate_report(self) -> str:
        """Generate a detailed conflict report"""
        lines = []
        lines.append("=" * 70)
        lines.append("🔍 I3 KEYBINDING CONFLICT ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append(f"\n📊 Summary:")
        lines.append(f"  Total bindings analyzed: {len(self.bindings)}")
        lines.append(f"  Modes detected: {len(self.modes)}")
        
        total_issues = sum(len(v) for k, v in self.conflicts.items() if k != 'unused_combinations')
        lines.append(f"  Total issues found: {total_issues}")
        
        # Duplicates
        if self.conflicts['duplicates']:
            lines.append(f"\n🔴 DUPLICATE BINDINGS ({len(self.conflicts['duplicates'])} found):")
            lines.append("-" * 50)
            for conflict in self.conflicts['duplicates']:
                lines.append(f"\n  ❌ Key: {conflict['key']} (Mode: {conflict['mode']})")
                for binding in conflict['bindings']:
                    lines.append(f"     Line {binding['line']}: {binding['command'][:50]}...")
                lines.append(f"  💡 Fix: Remove or change duplicate bindings")
        
        # Shadows
        if self.conflicts['shadows']:
            lines.append(f"\n🟡 SHADOWED BINDINGS ({len(self.conflicts['shadows'])} found):")
            lines.append("-" * 50)
            for conflict in self.conflicts['shadows'][:5]:  # Show first 5
                lines.append(f"\n  ⚠️  '{conflict['shadower']['key']}' shadows '{conflict['shadowed']['key']}'")
                lines.append(f"     {conflict['description']}")
                lines.append(f"  💡 Fix: Consider using different key combinations")
        
        # System conflicts
        if self.conflicts['system_conflicts']:
            lines.append(f"\n🟠 SYSTEM CONFLICTS ({len(self.conflicts['system_conflicts'])} found):")
            lines.append("-" * 50)
            for conflict in self.conflicts['system_conflicts']:
                lines.append(f"\n  ⚠️  '{conflict['binding']['key']}' conflicts with {conflict['system_function']}")
                lines.append(f"     Line {conflict['binding']['line']}: {conflict['binding']['command'][:40]}...")
                lines.append(f"  💡 Fix: Consider using a different binding")
        
        # Mode conflicts
        if self.conflicts['mode_conflicts']:
            lines.append(f"\n🟡 MODE CONFLICTS ({len(self.conflicts['mode_conflicts'])} found):")
            lines.append("-" * 50)
            for conflict in self.conflicts['mode_conflicts'][:5]:
                lines.append(f"\n  ⚠️  Mode '{conflict['mode']}' overrides '{conflict['default_binding']['key']}'")
                lines.append(f"     Default: {conflict['default_binding']['command'][:30]}...")
                lines.append(f"     Mode: {conflict['mode_binding']['command'][:30]}...")
        
        # Ergonomic issues
        if self.conflicts['ergonomic_issues']:
            lines.append(f"\n🟢 ERGONOMIC ISSUES ({len(self.conflicts['ergonomic_issues'])} found):")
            lines.append("-" * 50)
            for issue in self.conflicts['ergonomic_issues'][:5]:
                lines.append(f"\n  😰 '{issue['binding']['key']}': {issue['reason']}")
                lines.append(f"     Command: {issue['binding']['command'][:40]}...")
                lines.append(f"  💡 Suggestion: {issue['suggestion']}")
        
        # Similar bindings
        if self.conflicts['similar']:
            lines.append(f"\n🔵 SIMILAR BINDINGS ({len(self.conflicts['similar'])} found):")
            lines.append("-" * 50)
            shown = set()
            count = 0
            for conflict in self.conflicts['similar']:
                key_pair = tuple(sorted([conflict['binding1']['key'], conflict['binding2']['key']]))
                if key_pair not in shown and count < 5:
                    lines.append(f"\n  👀 '{conflict['binding1']['key']}' ↔ '{conflict['binding2']['key']}'")
                    lines.append(f"     {conflict['description']}")
                    shown.add(key_pair)
                    count += 1
        
        # Unused suggestions
        if self.conflicts['unused_combinations']:
            lines.append(f"\n💚 SUGGESTED UNUSED COMBINATIONS (top 10):")
            lines.append("-" * 50)
            for unused in self.conflicts['unused_combinations'][:10]:
                score_bar = '▰' * (unused['ergonomic_score'] // 10) + '▱' * (10 - unused['ergonomic_score'] // 10)
                lines.append(f"  ✅ {unused['key']:20} {score_bar} Score: {unused['ergonomic_score']}/100")
                lines.append(f"     Suggested use: {unused['suggestion']}")
        
        # Recommendations
        lines.append("\n" + "=" * 70)
        lines.append("📋 RECOMMENDATIONS:")
        lines.append("-" * 50)
        
        if total_issues == 0:
            lines.append("  🎉 Excellent! No conflicts detected.")
        else:
            if self.conflicts['duplicates']:
                lines.append("  1. Fix duplicate bindings immediately (high priority)")
            if self.conflicts['system_conflicts']:
                lines.append("  2. Review system conflicts to avoid unexpected behavior")
            if self.conflicts['shadows']:
                lines.append("  3. Consider resolving shadow conflicts for clarity")
            if self.conflicts['ergonomic_issues']:
                lines.append("  4. Improve ergonomics for frequently used commands")
            lines.append("  5. Consider using some of the suggested unused combinations")
        
        lines.append("\n" + "=" * 70)
        return '\n'.join(lines)
    
    def export_json(self, output_path: Path = None):
        """Export conflicts to JSON for programmatic use"""
        if output_path is None:
            output_path = Path.home() / '.config' / 'i3' / 'scripts' / 'conflict_report.json'
        
        export_data = {
            'summary': {
                'total_bindings': len(self.bindings),
                'total_modes': len(self.modes),
                'conflicts': {k: len(v) for k, v in self.conflicts.items()}
            },
            'conflicts': self.conflicts,
            'bindings': self.bindings
        }
        
        # Convert to JSON-serializable format
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            else:
                return obj
        
        with open(output_path, 'w') as f:
            json.dump(make_serializable(export_data), f, indent=2)
        
        return output_path
    
    def fix_conflicts_interactive(self):
        """Interactive conflict resolution (future enhancement)"""
        # This could be expanded to actually modify the config file
        pass

def main():
    """Run conflict detection and generate report"""
    print("🔍 Analyzing i3 configuration for conflicts...")
    
    detector = KeybindingConflictDetector()
    
    if not detector.parse_config():
        print("❌ Failed to parse i3 config file")
        return
    
    detector.detect_conflicts()
    
    # Generate and print report
    report = detector.generate_report()
    print(report)
    
    # Save JSON report
    json_path = detector.export_json()
    print(f"\n📄 Detailed JSON report saved to: {json_path}")
    
    # Save text report
    text_path = Path.home() / '.config' / 'i3' / 'scripts' / 'conflict_report.txt'
    with open(text_path, 'w') as f:
        f.write(report)
    print(f"📄 Text report saved to: {text_path}")

if __name__ == "__main__":
    main()
