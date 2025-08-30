#!/usr/bin/env python3
"""
i3 Keybinding Help - Enhanced conceptual search with synonyms and intents

Features:
- Synonym expansion (screenshot → snapshot, capture, grab, etc.)
- Intent mapping (open browser → firefox, brave, chrome, etc.) 
- Typo tolerance and fuzzy matching
- Hierarchical categorization with sub-categories
- Rich contextual descriptions
- External dictionaries for user customization

Usage: python3 i3-help.py
Add to i3 config: bindsym $mod+Alt+h exec python3 ~/.config/i3/scripts/i3-help.py

Dependencies (optional): rapidfuzz for enhanced fuzzy matching
Dictionaries: search_dictionaries.json for synonyms and intents
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# Import keyboard layout functionality
try:
    from keyboard_layout import KeyboardLayout
    KEYBOARD_LAYOUT_AVAILABLE = True
except ImportError:
    KEYBOARD_LAYOUT_AVAILABLE = False
    KeyboardLayout = None

# Import NLP query processor
try:
    from nlp_query_processor import NLPQueryProcessor
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    NLPQueryProcessor = None

# Import export engine
try:
    from export_engine import ExportEngine, ExportOptions
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    ExportEngine = None
    ExportOptions = None

# Import self-learning system
try:
    from search_learning_system import SearchLearningSystem
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    SearchLearningSystem = None

# Try to import rapidfuzz for enhanced fuzzy matching
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

class I3KeybindingHelper:
    def __init__(self):
        self.config_path = Path.home() / '.config' / 'i3' / 'config'
        # Get script directory - handle both __file__ and when run directly
        try:
            script_dir = Path(__file__).parent
        except NameError:
            script_dir = Path.cwd()
        self.dictionaries_path = script_dir / 'search_dictionaries.json'
        self.analytics_path = script_dir / 'usage_analytics.json'
        self.mod_key = 'Mod4'  # Default to Super key
        self.bindings = []
        self.analytics = self.load_analytics()
        
        # Initialize learning system
        self.learning_system = None
        if LEARNING_AVAILABLE:
            try:
                self.learning_system = SearchLearningSystem(script_dir)
            except Exception as e:
                print(f"Warning: Could not initialize learning system: {e}", file=sys.stderr)
        
        # Enhanced hierarchical categories with sub-categories
        self.categories = {
            '🚀 Apps & Launch': {
                'Applications': [],
                'Launchers': [],
                'Quick Access': []
            },
            '🖥️ Workspaces': {
                'Navigation': [],
                'Management': [],
                'Assignment': []
            },
            '🪟 Windows': {
                'Focus & Movement': [],
                'Arrangement': [],
                'State Control': []
            },
            '📷 Screenshots': {
                'Capture': [],
                'Tools': []
            },
            '🔊 Audio & Media': {
                'Volume Control': [],
                'Media Players': [],
                'System Audio': []
            },
            '💡 System & Power': {
                'Power Management': [],
                'Display Control': [],
                'Security': []
            },
            '📐 Layout': {
                'Split & Arrange': [],
                'Container Modes': [],
                'Resize & Adjust': []
            },
            '⚙️ i3 Control': {
                'Configuration': [],
                'Session Management': [],
                'Debug & Info': []
            },
            '🔧 Custom': {
                'Scripts': [],
                'User Defined': []
            }
        }
        
        # Load search dictionaries
        self.synonyms = {}
        self.intents = {}
        self.typos = {}
        self.load_dictionaries()
        
        # Initialize NLP processor if available
        self.nlp_processor = None
        if NLP_AVAILABLE:
            self.nlp_processor = NLPQueryProcessor(self.dictionaries_path)
    
    def load_dictionaries(self) -> None:
        """Load synonym, intent, and typo dictionaries from JSON file"""
        try:
            if self.dictionaries_path.exists():
                with open(self.dictionaries_path, 'r') as f:
                    data = json.load(f)
                    self.synonyms = data.get('synonyms', {})
                    self.intents = data.get('intents', {})
                    self.typos = data.get('typos', {})
            else:
                # Fallback to minimal built-in dictionaries
                self.synonyms = {
                    'screenshot': ['snapshot', 'capture', 'grab'],
                    'volume': ['sound', 'audio'],
                    'brightness': ['bright', 'dim'],
                    'browser': ['web', 'internet']
                }
        except Exception as e:
            print(f"Warning: Could not load dictionaries: {e}", file=sys.stderr)
    
    def load_analytics(self) -> Dict:
        """Load usage analytics from JSON file"""
        try:
            if self.analytics_path.exists():
                with open(self.analytics_path, 'r') as f:
                    return json.load(f)
            else:
                # Initialize empty analytics
                return {
                    'binding_usage': {},  # key -> count
                    'search_terms': {},   # term -> count
                    'popular_bindings': [],
                    'last_updated': None
                }
        except Exception as e:
            print(f"Warning: Could not load analytics: {e}", file=sys.stderr)
            return {'binding_usage': {}, 'search_terms': {}, 'popular_bindings': [], 'last_updated': None}
    
    def save_analytics(self) -> None:
        """Save analytics to JSON file"""
        try:
            import time
            self.analytics['last_updated'] = time.time()
            
            # Update popular bindings list (top 10)
            sorted_bindings = sorted(self.analytics['binding_usage'].items(), 
                                   key=lambda x: x[1], reverse=True)
            self.analytics['popular_bindings'] = [key for key, count in sorted_bindings[:10]]
            
            with open(self.analytics_path, 'w') as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save analytics: {e}", file=sys.stderr)
    
    def track_binding_usage(self, binding: Dict) -> None:
        """Track that a binding was used"""
        key_id = f"{binding['key']}:{binding['description']}"
        self.analytics['binding_usage'][key_id] = self.analytics['binding_usage'].get(key_id, 0) + 1
        self.save_analytics()
    
    def track_search_term(self, term: str, result_count: int = 0, selected_binding: str = None) -> None:
        """Track search terms used and learn from failures"""
        clean_term = term.lower().strip()
        if clean_term:  # Only track non-empty terms
            self.analytics['search_terms'][clean_term] = self.analytics['search_terms'].get(clean_term, 0) + 1
            self.save_analytics()
            
            # Record failed searches for learning
            if self.learning_system and result_count == 0:
                # Get potential matches for analysis
                all_descriptions = [binding['description'] for binding in self.bindings]
                suggested_matches = self.learning_system.suggest_closest_matches(clean_term, all_descriptions)
                
                self.learning_system.record_failed_search(
                    query=clean_term,
                    result_count=result_count,
                    suggested_matches=suggested_matches
                )
            
            # Record user selection for learning
            if self.learning_system and selected_binding:
                self.learning_system.record_user_selection(clean_term, selected_binding)
    
    def get_popular_suggestions(self, limit: int = 5) -> List[str]:
        """Get popular binding suggestions based on usage"""
        suggestions = []
        
        # Get top search terms
        top_searches = sorted(self.analytics['search_terms'].items(), 
                            key=lambda x: x[1], reverse=True)[:limit]
        
        for term, count in top_searches:
            if count > 1:  # Only suggest terms used more than once
                suggestions.append(f"{term} (searched {count}x)")
        
        return suggestions
    
    def rank_bindings_by_popularity(self, bindings: List[Dict]) -> List[Dict]:
        """Sort bindings by usage frequency"""
        def get_popularity_score(binding):
            key_id = f"{binding['key']}:{binding['description']}"
            return self.analytics['binding_usage'].get(key_id, 0)
        
        return sorted(bindings, key=get_popularity_score, reverse=True)
    
    def normalize_text(self, text: str) -> List[str]:
        """Normalize text for search - handle plurals, lowercase, etc."""
        words = re.findall(r'\b\w+\b', text.lower())
        normalized = []
        
        for word in words:
            # Add original word
            normalized.append(word)
            
            # Handle plurals -> singular
            if word.endswith('s') and len(word) > 3:
                normalized.append(word[:-1])
            
            # Handle common variations
            if word.endswith('ing'):
                normalized.append(word[:-3])  # running -> run
            elif word.endswith('ed'):
                normalized.append(word[:-2])  # moved -> move
                
        return list(set(normalized))  # Remove duplicates
    
    def expand_synonyms(self, words: List[str]) -> Set[str]:
        """Expand words using synonym dictionary"""
        expanded = set(words)
        
        for word in words:
            # Direct synonym lookup
            if word in self.synonyms:
                expanded.update(self.synonyms[word])
            
            # Reverse lookup - if word is a synonym, add the key
            for key, synonyms in self.synonyms.items():
                if word in synonyms:
                    expanded.add(key)
                    expanded.update(synonyms)
        
        return expanded
    
    def map_intents(self, command: str, description: str) -> List[str]:
        """Map command/description to high-level intents"""
        intents = []
        combined_text = f"{command} {description}".lower()
        
        for intent, patterns in self.intents.items():
            if any(pattern.lower() in combined_text for pattern in patterns):
                intents.append(intent)
        
        return intents
    
    def correct_typos(self, text: str) -> str:
        """Correct common typos in search text"""
        words = text.split()
        corrected = []
        
        for word in words:
            corrected_word = self.typos.get(word.lower(), word)
            corrected.append(corrected_word)
        
        return ' '.join(corrected)
    
    def generate_search_terms(self, binding: Dict) -> str:
        """Generate comprehensive search terms for a binding"""
        terms = set()
        
        # Base terms
        base_words = self.normalize_text(f"{binding['description']} {binding['key']} {binding['command']}")
        terms.update(base_words)
        
        # Add category context
        category = self.get_binding_category(binding)
        if category:
            terms.update(self.normalize_text(category))
        
        # Expand with synonyms
        expanded = self.expand_synonyms(list(terms))
        terms.update(expanded)
        
        # Add intent mappings
        intents = self.map_intents(binding['command'], binding['description'])
        for intent in intents:
            terms.update(self.normalize_text(intent))
        
        # Add simplified tokens for typo tolerance
        simplified_terms = set()
        for term in terms:
            # Remove vowels for fuzzy matching
            consonants = ''.join(c for c in term if c not in 'aeiou')
            if len(consonants) > 2:
                simplified_terms.add(consonants)
        
        terms.update(simplified_terms)
        
        return ' '.join(sorted(terms))
    
    def get_binding_category(self, binding: Dict) -> Optional[str]:
        """Get the category name for a binding"""
        cmd = binding['command'].lower()
        desc = binding['description'].lower()
        
        if any(x in cmd or x in desc for x in ['screenshot', 'flameshot', 'print']):
            return 'Screenshots Capture'
        elif any(x in cmd or x in desc for x in ['dmenu', 'rofi', 'terminal', 'browser']):
            return 'Apps Launch Applications'
        elif 'workspace' in cmd or 'workspace' in desc:
            return 'Workspaces Navigation'
        elif any(x in cmd for x in ['focus', 'move', 'resize']):
            return 'Windows Focus Movement'
        elif any(x in cmd for x in ['kill', 'fullscreen', 'floating']):
            return 'Windows State Control'
        elif any(x in cmd for x in ['volume', 'audio', 'pactl', 'mute']):
            return 'Audio Volume Control'
        elif any(x in cmd for x in ['media', 'playerctl', 'play', 'pause']):
            return 'Audio Media Players'
        elif any(x in cmd for x in ['brightness', 'light']):
            return 'System Display Control'
        elif any(x in cmd for x in ['lock', 'suspend', 'reboot', 'shutdown']):
            return 'System Power Management'
        elif any(x in cmd for x in ['layout', 'split', 'tabbed', 'stacking']):
            return 'Layout Split Arrange'
        elif any(x in cmd for x in ['i3-msg', 'reload', 'restart']):
            return 'i3 Configuration'
        
        return 'Custom Scripts'

    def find_launcher(self):
        """Find available launcher (rofi, dmenu, etc.)"""
        launchers = [
            ['rofi', '-dmenu', '-i', '-p', 'i3 Help:', '-theme-str', 
             'window { width: 60%; } listview { lines: 15; }'],
            ['dmenu', '-i', '-p', 'i3 Help:', '-l', '15'],
            ['fzf', '--prompt=i3 Help: ']
        ]
        
        for launcher in launchers:
            if subprocess.run(['which', launcher[0]], 
                            capture_output=True, text=True).returncode == 0:
                return launcher
        
        return None

    def parse_config(self):
        """Parse i3 config file"""
        if not self.config_path.exists():
            return False
            
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
        except Exception as e:
            return False

        # Find mod key
        mod_match = re.search(r'set\s+\$mod\s+(\w+)', content)
        if mod_match:
            self.mod_key = mod_match.group(1)

        # Parse bindings
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Parse bindsym
            bind_match = re.match(r'^bindsym\s+(.*?)\s+(.+)$', line)
            if bind_match and 'mode ' not in line:
                key, command = bind_match.groups()
                
                # Clean up key combination
                display_key = key.replace('$mod', self.get_mod_display())
                
                binding = {
                    'key': display_key,
                    'command': command,
                    'description': self.generate_description(command, display_key),
                    'line': i + 1,
                    'search_text': '',  # Will be set later
                    'category': '',     # Will be set later
                    'subcategory': ''   # Will be set later
                }
                
                self.bindings.append(binding)
        
        # Generate enhanced search terms for all bindings
        for binding in self.bindings:
            binding['search_text'] = self.generate_search_terms(binding)

        self.categorize_bindings()
        return True

    def get_mod_display(self):
        """Convert mod key to display format"""
        mod_map = {
            'Mod1': 'Alt',
            'Mod4': 'Super',
            'Control': 'Ctrl',
            'Shift': 'Shift'
        }
        return mod_map.get(self.mod_key, self.mod_key)

    def generate_description(self, command, key_combo=''):
        """Generate human-readable description"""
        cmd = command.replace('exec --no-startup-id ', '').replace('exec ', '').strip()
        
        # Direct mappings
        mappings = {
            'i3-msg exit': 'Exit i3',
            'i3lock': 'Lock screen',
            'i3-msg reload': 'Reload config',
            'i3-msg restart': 'Restart i3',
            'kill': 'Close window',
            'fullscreen toggle': 'Toggle fullscreen',
            'floating toggle': 'Toggle floating',
            'focus left': 'Focus left',
            'focus right': 'Focus right', 
            'focus up': 'Focus up',
            'focus down': 'Focus down',
            'split h': 'Split horizontal',
            'split v': 'Split vertical',
            'layout tabbed': 'Tabbed layout',
            'layout stacking': 'Stacking layout',
            'layout toggle split': 'Toggle split layout',
        }
        
        if cmd in mappings:
            return mappings[cmd]
        
        # Key-based detection for special cases
        if key_combo:
            # Screenshot detection by key combinations
            if 'Print' in key_combo or 'print' in key_combo.lower():
                if 'screenshot.sh full' in cmd:
                    return 'Screenshot - Full screen'
                elif 'screenshot.sh gui' in cmd:
                    return 'Screenshot - Interactive selection'
                elif 'screenshot.sh window' in cmd:
                    return 'Screenshot - Active window'
                elif 'screenshot.sh clipboard' in cmd:
                    return 'Screenshot - Quick selection to clipboard'
                elif 'screenshot.sh config' in cmd:
                    return 'Screenshot - Open Flameshot config'
                elif 'screenshot.sh' in cmd:
                    return 'Screenshot utility'
            
            # Function key detection
            if key_combo.startswith('XF86Audio'):
                if 'RaiseVolume' in key_combo: return 'Volume up'
                elif 'LowerVolume' in key_combo: return 'Volume down'
                elif 'Mute' in key_combo: return 'Toggle mute'
                elif 'MicMute' in key_combo: return 'Toggle microphone mute'
                elif 'Play' in key_combo: return 'Play/Pause media'
                elif 'Next' in key_combo: return 'Next track'
                elif 'Prev' in key_combo: return 'Previous track'
            
            if 'MonBrightness' in key_combo:
                if 'Up' in key_combo: return 'Brightness up'
                elif 'Down' in key_combo: return 'Brightness down'
        
        # Pattern matching for scripts and complex commands
        script_patterns = {
            r'screenshot\.sh': 'Screenshot utility',
            r'setup-monitors\.sh': 'Configure monitors',
            r'printer-manager\.sh': 'Printer management',
            r'i3-help\.py': 'Show keybinding help',
            r'show-keybindings\.sh': 'Show keybindings',
            r'watch-config\.sh': 'Config file watcher',
        }
        
        for pattern, desc in script_patterns.items():
            if re.search(pattern, cmd):
                return desc
        
        # Workspace detection
        if 'workspace' in cmd:
            if 'move container' in cmd:
                ws = re.search(r'workspace\s+(.+)', cmd)
                return f"Move to workspace {ws.group(1) if ws else '?'}"
            else:
                ws = re.search(r'workspace\s+(.+)', cmd)
                return f"Switch to workspace {ws.group(1) if ws else '?'}"
        
        # Audio controls
        if 'pactl' in cmd and 'volume' in cmd:
            if '+' in cmd: return 'Volume up'
            if '-' in cmd: return 'Volume down'
            if 'toggle' in cmd: return 'Mute toggle'
        
        # Brightness controls
        if 'brightnessctl' in cmd or 'light' in cmd or 'xbacklight' in cmd:
            if '+' in cmd or 'inc' in cmd or '-A' in cmd: return 'Brightness up'
            if '-' in cmd or 'dec' in cmd or '-U' in cmd: return 'Brightness down'
        
        # Media player controls
        if 'playerctl' in cmd:
            if 'play-pause' in cmd: return 'Play/Pause media'
            elif 'next' in cmd: return 'Next track'
            elif 'previous' in cmd: return 'Previous track'
        
        # System controls
        if 'systemctl' in cmd:
            if 'suspend' in cmd: return 'Suspend system'
            elif 'hibernate' in cmd: return 'Hibernate system'
            elif 'reboot' in cmd: return 'Reboot system'
            elif 'poweroff' in cmd: return 'Shutdown system'
        
        # Lock commands
        if 'i3lock' in cmd:
            return 'Lock screen'
        
        # Application detection
        app_patterns = {
            r'(firefox|chrome|chromium|brave)': 'Launch browser',
            r'(warp-terminal|terminal|alacritty|gnome-terminal|kitty|urxvt)': 'Open terminal',
            r'(dmenu|rofi)': 'Application launcher',
            r'(nautilus|thunar|pcmanfm)': 'File manager',
            r'(code|vim|emacs|nano)': 'Text editor',
            r'blueman-manager': 'Bluetooth manager',
            r'i3-nagbar': 'System confirmation dialog',
            r'i3-input': 'Input prompt',
            r'i3-save-tree': 'Save workspace layout',
        }
        
        for pattern, desc in app_patterns.items():
            if re.search(pattern, cmd.lower()):
                return desc
        
        # Fallback: use first word or truncate
        first_word = cmd.split()[0] if cmd.split() else cmd
        return first_word if len(first_word) <= 30 else first_word[:27] + '...'

    def categorize_bindings(self):
        """Sort bindings into hierarchical categories and sub-categories"""
        for binding in self.bindings:
            cmd = binding['command'].lower()
            desc = binding['description'].lower()
            
            # Screenshots
            if any(x in cmd or x in desc for x in ['screenshot', 'flameshot', 'print']):
                if 'config' in cmd:
                    subcategory = 'Tools'
                else:
                    subcategory = 'Capture'
                self.categories['📷 Screenshots'][subcategory].append(binding)
                binding['category'] = '📷 Screenshots'
                binding['subcategory'] = subcategory
            
            # Apps & Launch
            elif any(x in cmd or x in desc for x in ['dmenu', 'rofi']):
                self.categories['🚀 Apps & Launch']['Launchers'].append(binding)
                binding['category'] = '🚀 Apps & Launch'
                binding['subcategory'] = 'Launchers'
            elif any(x in cmd or x in desc for x in ['terminal', 'browser', 'firefox', 'chrome', 'brave']):
                if any(x in desc.lower() for x in ['quick', 'shift']):
                    subcategory = 'Quick Access'
                else:
                    subcategory = 'Applications'
                self.categories['🚀 Apps & Launch'][subcategory].append(binding)
                binding['category'] = '🚀 Apps & Launch'
                binding['subcategory'] = subcategory
            
            # Workspaces
            elif 'workspace' in cmd or 'workspace' in desc:
                if 'move container' in cmd:
                    subcategory = 'Assignment'
                elif any(x in cmd for x in ['next', 'prev', 'tab']):
                    subcategory = 'Navigation'
                elif re.search(r'workspace \d', cmd):
                    subcategory = 'Navigation'
                else:
                    subcategory = 'Management'
                self.categories['🖥️ Workspaces'][subcategory].append(binding)
                binding['category'] = '🖥️ Workspaces'
                binding['subcategory'] = subcategory
            
            # Windows
            elif any(x in cmd for x in ['focus', 'move']):
                self.categories['🪟 Windows']['Focus & Movement'].append(binding)
                binding['category'] = '🪟 Windows'
                binding['subcategory'] = 'Focus & Movement'
            elif any(x in cmd for x in ['resize']):
                self.categories['🪟 Windows']['Arrangement'].append(binding)
                binding['category'] = '🪟 Windows'
                binding['subcategory'] = 'Arrangement'
            elif any(x in cmd for x in ['kill', 'fullscreen', 'floating']):
                self.categories['🪟 Windows']['State Control'].append(binding)
                binding['category'] = '🪟 Windows'
                binding['subcategory'] = 'State Control'
            
            # Audio & Media
            elif any(x in cmd for x in ['volume', 'pactl', 'mute', 'XF86Audio']):
                if any(x in cmd for x in ['volume', 'mute']):
                    subcategory = 'Volume Control'
                else:
                    subcategory = 'System Audio'
                self.categories['🔊 Audio & Media'][subcategory].append(binding)
                binding['category'] = '🔊 Audio & Media'
                binding['subcategory'] = subcategory
            elif any(x in cmd for x in ['playerctl', 'media', 'play', 'pause', 'next', 'prev']):
                self.categories['🔊 Audio & Media']['Media Players'].append(binding)
                binding['category'] = '🔊 Audio & Media'
                binding['subcategory'] = 'Media Players'
            
            # System & Power
            elif any(x in cmd for x in ['brightness', 'light', 'MonBrightness']):
                self.categories['💡 System & Power']['Display Control'].append(binding)
                binding['category'] = '💡 System & Power'
                binding['subcategory'] = 'Display Control'
            elif any(x in cmd for x in ['lock', 'suspend', 'reboot', 'shutdown', 'hibernate']):
                if 'lock' in cmd:
                    subcategory = 'Security'
                else:
                    subcategory = 'Power Management'
                self.categories['💡 System & Power'][subcategory].append(binding)
                binding['category'] = '💡 System & Power'
                binding['subcategory'] = subcategory
            
            # Layout
            elif any(x in cmd for x in ['split']):
                self.categories['📐 Layout']['Split & Arrange'].append(binding)
                binding['category'] = '📐 Layout'
                binding['subcategory'] = 'Split & Arrange'
            elif any(x in cmd for x in ['layout', 'tabbed', 'stacking']):
                self.categories['📐 Layout']['Container Modes'].append(binding)
                binding['category'] = '📐 Layout'
                binding['subcategory'] = 'Container Modes'
            elif any(x in cmd for x in ['resize']):
                self.categories['📐 Layout']['Resize & Adjust'].append(binding)
                binding['category'] = '📐 Layout'
                binding['subcategory'] = 'Resize & Adjust'
            
            # i3 Control
            elif any(x in cmd for x in ['i3-msg', 'reload', 'restart']):
                if any(x in cmd for x in ['reload', 'restart']):
                    subcategory = 'Configuration'
                elif 'exit' in cmd:
                    subcategory = 'Session Management'
                else:
                    subcategory = 'Debug & Info'
                self.categories['⚙️ i3 Control'][subcategory].append(binding)
                binding['category'] = '⚙️ i3 Control'
                binding['subcategory'] = subcategory
            
            # Custom/Scripts
            else:
                if any(x in cmd for x in ['.sh', '.py']):
                    subcategory = 'Scripts'
                else:
                    subcategory = 'User Defined'
                self.categories['🔧 Custom'][subcategory].append(binding)
                binding['category'] = '🔧 Custom'
                binding['subcategory'] = subcategory

    def format_for_display(self):
        """Format bindings for launcher display with hierarchical sub-categories"""
        lines = []
        
        for category_name, subcategories in self.categories.items():
            # Check if this category has any bindings
            has_bindings = any(len(bindings) > 0 for bindings in subcategories.values())
            
            if has_bindings:
                lines.append(f"\n{category_name}")
                lines.append("═" * 60)
                
                for subcategory_name, bindings in subcategories.items():
                    if bindings:
                        lines.append(f"\n  {subcategory_name}")
                        lines.append("  " + "─" * (len(subcategory_name) + 2))
                        
                        for binding in sorted(bindings, key=lambda x: x['description']):
                            key_part = f"[{binding['key']}]".ljust(18)
                            # Add category context to make search more informative
                            category_hint = f"({subcategory_name})".ljust(15)
                            lines.append(f"  {key_part} {binding['description']} {category_hint}")
        
        return '\n'.join(lines)

    def execute_binding_command(self, command: str) -> bool:
        """Execute a binding command safely"""
        try:
            # Clean the command
            clean_cmd = command.replace('exec --no-startup-id ', '').replace('exec ', '').strip()
            
            # Skip certain dangerous commands
            dangerous_patterns = ['rm ', 'del ', 'shutdown', 'reboot', 'poweroff']
            if any(pattern in clean_cmd.lower() for pattern in dangerous_patterns):
                subprocess.run(['notify-send', 'i3 Help', f'Skipped potentially dangerous command: {clean_cmd}'])
                return False
            
            # Execute the command
            subprocess.Popen(clean_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['notify-send', 'i3 Help', f'Executed: {clean_cmd[:50]}...'])
            return True
            
        except Exception as e:
            subprocess.run(['notify-send', 'i3 Help Error', f'Failed to execute: {str(e)}'])
            return False
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard using available tools"""
        clipboard_tools = ['xclip', 'xsel', 'wl-copy']
        
        for tool in clipboard_tools:
            if subprocess.run(['which', tool], capture_output=True).returncode == 0:
                try:
                    if tool == 'xclip':
                        subprocess.run([tool, '-selection', 'clipboard'], input=text, text=True)
                    elif tool == 'xsel':
                        subprocess.run([tool, '--clipboard', '--input'], input=text, text=True)
                    elif tool == 'wl-copy':
                        subprocess.run([tool], input=text, text=True)
                    
                    subprocess.run(['notify-send', 'i3 Help', f'Copied to clipboard: {text[:30]}...'])
                    return True
                except Exception:
                    continue
        
        subprocess.run(['notify-send', 'i3 Help', 'No clipboard tool found (xclip/xsel/wl-copy)'])
        return False
    
    def show_binding_details(self, binding: Dict) -> None:
        """Show detailed information about a binding"""
        details = [
            f"Key: {binding['key']}",
            f"Description: {binding['description']}",
            f"Command: {binding['command']}",
            f"Category: {binding.get('category', 'Unknown')}",
            f"Subcategory: {binding.get('subcategory', 'Unknown')}",
            f"Config line: {binding['line']}"
        ]
        
        detail_text = '\n'.join(details)
        
        # Try to show in rofi or fallback to notify-send
        try:
            if subprocess.run(['which', 'rofi'], capture_output=True).returncode == 0:
                subprocess.run([
                    'rofi', '-e', detail_text, 
                    '-theme-str', 'window { width: 50%; }'
                ])
            else:
                subprocess.run(['notify-send', 'Binding Details', detail_text])
        except Exception:
            subprocess.run(['notify-send', 'Binding Details', detail_text])
    
    def show_keyboard_layout(self, binding: Dict) -> None:
        """Show visual keyboard layout with highlighted key"""
        if not KEYBOARD_LAYOUT_AVAILABLE:
            subprocess.run(['notify-send', 'i3 Help', 'Keyboard layout not available'])
            return
        
        try:
            layout = KeyboardLayout()
            
            # Extract individual keys from the binding
            key_parts = binding['key'].replace('+', ' ').split()
            
            # Generate visual layout
            layout_text = layout.generate_focused_view(binding['key'])
            
            # Try to show in rofi or fallback to notify-send
            if subprocess.run(['which', 'rofi'], capture_output=True).returncode == 0:
                subprocess.run([
                    'rofi', '-e', layout_text,
                    '-theme-str', 'window { width: 70%; } textbox { font: "monospace 10"; }'
                ])
            else:
                subprocess.run(['notify-send', 'Key Layout', layout_text])
                
        except Exception as e:
            subprocess.run(['notify-send', 'Keyboard Layout Error', str(e)])
    
    def show_export_menu(self) -> None:
        """Show export format selection menu and perform export"""
        if not EXPORT_AVAILABLE:
            subprocess.run(['notify-send', 'i3 Help', 'Export functionality not available'])
            return
        
        try:
            # Available export formats
            formats = [
                "📄 PDF - Printable documentation",
                "🌐 HTML - Interactive web page", 
                "📝 Markdown - Text with formatting",
                "📋 Plain Text - Simple text format",
                "🔧 JSON - Machine readable data",
                "❌ Cancel"
            ]
            
            launcher = self.find_launcher()
            if not launcher:
                subprocess.run(['notify-send', 'i3 Help', 'No launcher found'])
                return
            
            # Modify launcher for format selection
            if launcher[0] == 'rofi':
                format_launcher = ['rofi', '-dmenu', '-p', 'Export Format:', '-theme-str', 'window { width: 50%; }']
            else:
                format_launcher = launcher
            
            process = subprocess.Popen(
                format_launcher,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input='\n'.join(formats))
            
            if process.returncode == 0 and stdout.strip() and "Cancel" not in stdout.strip():
                selected_format = stdout.strip()
                
                # Extract format type from selection
                format_map = {
                    "PDF": "pdf",
                    "HTML": "html", 
                    "Markdown": "markdown",
                    "Plain Text": "text",
                    "JSON": "json"
                }
                
                export_format = None
                for key, value in format_map.items():
                    if key in selected_format:
                        export_format = value
                        break
                
                if export_format:
                    self.perform_export(export_format)
                    
        except Exception as e:
            subprocess.run(['notify-send', 'i3 Help Error', f'Export menu failed: {str(e)}'])
    
    def perform_export(self, format_type: str) -> None:
        """Perform the actual export operation"""
        try:
            # Create export engine instance
            engine = ExportEngine()
            
            # Generate default filename
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"i3-keybindings_{timestamp}.{format_type}"
            
            # Set output path (default to user's Documents or home directory)
            output_dir = Path.home() / 'Documents'
            if not output_dir.exists():
                output_dir = Path.home()
            
            output_path = str(output_dir / filename)
            
            # Create export options
            options = ExportOptions(
                format=format_type,
                output_path=output_path,
                include_categories=True,
                include_descriptions=True,
                include_commands=True,
                sort_by="category"
            )
            
            # Perform export - use the correct method signature
            success = engine.export(self.bindings, self.analytics, options)
            
            if success:
                subprocess.run([
                    'notify-send', 
                    'Export Successful', 
                    f'Keybindings exported to:\n{options.output_path}'
                ])
                
                # Optionally open the exported file
                self.offer_to_open_export(options.output_path)
            else:
                subprocess.run([
                    'notify-send', 
                    'Export Failed', 
                    f'Could not export keybindings as {format_type.upper()}'
                ])
                
        except Exception as e:
            subprocess.run([
                'notify-send', 
                'Export Error', 
                f'Export failed: {str(e)}'
            ])
    
    def offer_to_open_export(self, file_path: str) -> None:
        """Offer to open the exported file"""
        try:
            launcher = self.find_launcher()
            if not launcher:
                return
            
            options = [
                "📂 Open file",
                "📁 Open containing folder", 
                "❌ Close"
            ]
            
            if launcher[0] == 'rofi':
                open_launcher = ['rofi', '-dmenu', '-p', 'Open exported file?', '-theme-str', 'window { width: 40%; }']
            else:
                open_launcher = launcher
            
            process = subprocess.Popen(
                open_launcher,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input='\n'.join(options))
            
            if process.returncode == 0 and stdout.strip():
                selected = stdout.strip()
                
                if "Open file" in selected:
                    # Try to open with default application
                    subprocess.run(['xdg-open', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif "Open containing folder" in selected:
                    # Open the containing directory
                    directory = str(Path(file_path).parent)
                    subprocess.run(['xdg-open', directory], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
        except Exception as e:
            # Silently ignore errors in opening files
            pass
    
    def show_learning_stats(self) -> None:
        """Show learning system statistics and suggestions"""
        if not self.learning_system:
            subprocess.run(['notify-send', 'i3 Help', 'Learning system not available'])
            return
        
        try:
            stats = self.learning_system.get_learning_stats()
            suggestions = self.learning_system.get_improvement_suggestions()
            
            # Build stats display
            stats_lines = [
                "🧠 Self-Learning System Statistics",
                "═" * 45,
                "",
                "📊 Data Collection:",
                f"  • Failed searches tracked: {stats['total_failed_searches']}",
                f"  • Recent failures (24h): {stats['recent_failed_searches']}",
                f"  • Learning insights: {stats['total_insights']}",
                f"  • High confidence insights: {stats['high_confidence_insights']}",
                f"  • User confirmed insights: {stats['user_confirmed_insights']}",
                "",
                "🎯 Pattern Analysis:",
                f"  • Typo corrections: {stats['pattern_breakdown']['typo']}",
                f"  • Synonym mappings: {stats['pattern_breakdown']['synonym']}",
                f"  • Intent patterns: {stats['pattern_breakdown']['intent']}",
                "",
                "📖 Dictionary Growth:",
                f"  • Synonyms: {stats['dictionary_sizes']['synonyms']} entries",
                f"  • Intents: {stats['dictionary_sizes']['intents']} entries",
                f"  • Typo fixes: {stats['dictionary_sizes']['typos']} entries",
            ]
            
            # Add suggestions if available
            if suggestions['high_confidence']:
                stats_lines.extend([
                    "",
                    "💡 Ready to Apply (High Confidence):"
                ])
                for suggestion in suggestions['high_confidence'][:3]:
                    stats_lines.append(
                        f"  • '{suggestion['original']}' → '{suggestion['suggestion']}' ({suggestion['confidence']:.1%})"
                    )
            
            # Add pending suggestions
            pending_count = len(suggestions['typos']) + len(suggestions['synonyms']) + len(suggestions['intents'])
            if pending_count > 0:
                stats_lines.extend([
                    "",
                    f"⏳ Pending suggestions: {pending_count} (need more evidence)"
                ])
            
            stats_text = '\n'.join(stats_lines)
            
            # Show learning maintenance options
            maintenance_options = [
                "🔄 Apply High-Confidence Improvements",
                "🧹 Clean Up Old Data",
                "📋 View All Suggestions",
                "❌ Close"
            ]
            
            # First show stats, then options
            if subprocess.run(['which', 'rofi'], capture_output=True).returncode == 0:
                # Show stats display
                subprocess.run([
                    'rofi', '-e', stats_text,
                    '-theme-str', 'window { width: 60%; } textbox { font: "monospace 9"; }'
                ])
                
                # Then show maintenance options
                launcher = ['rofi', '-dmenu', '-p', 'Learning Maintenance:', '-theme-str', 'window { width: 50%; }']
                
                process = subprocess.Popen(
                    launcher,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input='\n'.join(maintenance_options))
                
                if process.returncode == 0 and stdout.strip():
                    selected_option = stdout.strip()
                    
                    if "Apply High-Confidence" in selected_option:
                        applied = self.learning_system.apply_high_confidence_suggestions()
                        subprocess.run([
                            'notify-send',
                            'Learning System',
                            f'Applied {applied} high-confidence improvements!'
                        ])
                        
                    elif "Clean Up Old Data" in selected_option:
                        cleaned = self.learning_system.cleanup_old_data()
                        subprocess.run([
                            'notify-send',
                            'Learning System', 
                            f'Cleaned up {cleaned} old data entries'
                        ])
                        
                    elif "View All Suggestions" in selected_option:
                        self._show_all_suggestions(suggestions)
            else:
                # Fallback to notify-send
                subprocess.run(['notify-send', 'Learning Stats', stats_text[:500]])
                
        except Exception as e:
            subprocess.run(['notify-send', 'Learning Stats Error', str(e)])
    
    def _show_all_suggestions(self, suggestions: Dict) -> None:
        """Show detailed view of all learning suggestions"""
        suggestion_lines = [
            "💡 All Learning Suggestions",
            "═" * 35,
            ""
        ]
        
        categories = {
            'typos': '🔤 Typo Corrections',
            'synonyms': '🔄 Synonym Mappings', 
            'intents': '🎯 Intent Patterns'
        }
        
        for category, title in categories.items():
            if suggestions[category]:
                suggestion_lines.extend([
                    title,
                    "─" * len(title)
                ])
                
                for suggestion in suggestions[category][:5]:
                    confidence = f"{suggestion['confidence']:.1%}"
                    evidence = f"({suggestion['evidence_count']} evidence)"
                    suggestion_lines.append(
                        f"  • '{suggestion['original']}' → '{suggestion['suggestion']}' {confidence} {evidence}"
                    )
                
                suggestion_lines.append("")
        
        suggestions_text = '\n'.join(suggestion_lines)
        
        if subprocess.run(['which', 'rofi'], capture_output=True).returncode == 0:
            subprocess.run([
                'rofi', '-e', suggestions_text,
                '-theme-str', 'window { width: 70%; } textbox { font: "monospace 9"; }'
            ])
        else:
            subprocess.run(['notify-send', 'All Suggestions', suggestions_text[:500]])
    
    def show_action_menu(self, binding: Dict) -> None:
        """Show action menu for selected binding"""
        actions = [
            "🚀 Execute Command",
            "📋 Copy Command", 
            "📋 Copy Key Combination",
            "ℹ️  Show Details",
            "❌ Cancel"
        ]
        
        # Add keyboard layout option if available
        if KEYBOARD_LAYOUT_AVAILABLE:
            actions.insert(-1, "⌨️  Show Key Layout")
        
        # Add export option if available
        if EXPORT_AVAILABLE:
            actions.insert(-1, "📄 Export Keybindings")
        
        # Add learning stats option if available
        if LEARNING_AVAILABLE and self.learning_system:
            actions.insert(-1, "🧠 Learning Stats")
        
        try:
            launcher = self.find_launcher()
            if not launcher:
                return
            
            # Modify launcher for action menu
            if launcher[0] == 'rofi':
                action_launcher = ['rofi', '-dmenu', '-p', 'Action:', '-theme-str', 'window { width: 40%; }']
            else:
                action_launcher = launcher
            
            process = subprocess.Popen(
                action_launcher,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input='\n'.join(actions))
            
            if process.returncode == 0 and stdout.strip():
                selected_action = stdout.strip()
                
                if "Execute Command" in selected_action:
                    self.track_binding_usage(binding)
                    self.execute_binding_command(binding['command'])
                elif "Copy Command" in selected_action:
                    self.track_binding_usage(binding)
                    self.copy_to_clipboard(binding['command'])
                elif "Copy Key" in selected_action:
                    self.track_binding_usage(binding)
                    self.copy_to_clipboard(binding['key'])
                elif "Show Details" in selected_action:
                    self.track_binding_usage(binding)
                    self.show_binding_details(binding)
                elif "Show Key Layout" in selected_action:
                    self.track_binding_usage(binding)
                    self.show_keyboard_layout(binding)
                elif "Export Keybindings" in selected_action:
                    self.show_export_menu()
                elif "Learning Stats" in selected_action:
                    self.show_learning_stats()
                    
        except Exception as e:
            subprocess.run(['notify-send', 'i3 Help Error', f'Action menu failed: {str(e)}'])
    
    def find_binding_by_display(self, display_line: str) -> Optional[Dict]:
        """Find binding object from display line"""
        # Extract key combination from display line
        if '[' in display_line and ']' in display_line:
            key_part = display_line[display_line.find('[') + 1:display_line.find(']')]
            
            # Find matching binding
            for binding in self.bindings:
                if binding['key'] == key_part:
                    return binding
        
        return None

    def show_help(self):
        """Display help using available launcher with action execution"""
        if not self.parse_config():
            subprocess.run(['notify-send', 'i3 Help', 'Could not read i3 config file'])
            return
        
        # Apply any high-confidence learning improvements
        if self.learning_system:
            try:
                applied_count = self.learning_system.apply_high_confidence_suggestions()
                if applied_count > 0:
                    # Reload dictionaries if improvements were applied
                    self.load_dictionaries()
                    # Regenerate search terms with updated dictionaries
                    for binding in self.bindings:
                        binding['search_text'] = self.generate_search_terms(binding)
            except Exception as e:
                print(f"Warning: Could not apply learning improvements: {e}", file=sys.stderr)
        
        launcher = self.find_launcher()
        if not launcher:
            subprocess.run(['notify-send', 'i3 Help', 'No launcher found (rofi/dmenu/fzf)'])
            return
        
        display_text = self.format_for_display()
        
        try:
            # Show the menu
            process = subprocess.Popen(
                launcher,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=display_text)
            
            if process.returncode == 0 and stdout.strip():
                selected = stdout.strip()
                
                # Find the corresponding binding
                binding = self.find_binding_by_display(selected)
                if binding:
                    # Record successful selection for learning
                    if self.learning_system:
                        # This helps learn from successful interactions
                        search_query = getattr(self, '_last_search_query', '')
                        if search_query:
                            self.learning_system.record_user_selection(search_query, binding['description'])
                    
                    self.show_action_menu(binding)
                
        except Exception as e:
            subprocess.run(['notify-send', 'i3 Help Error', str(e)])

def main():
    helper = I3KeybindingHelper()
    helper.show_help()

if __name__ == '__main__':
    main()
