#!/usr/bin/env python3
"""
Natural Language Query Processor for i3 Keybinding Help

Processes natural language queries like:
- "open browser"
- "take screenshot" 
- "change volume"
- "lock screen"
- "switch workspace"
- "make window fullscreen"

Features:
- Intent recognition and extraction
- Action verb + object noun parsing
- Context-aware command matching
- Query learning and suggestions
- Fuzzy matching for typos and variations
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass

@dataclass
class QueryIntent:
    """Represents a parsed natural language query intent"""
    action: str          # Primary action (open, take, change, etc.)
    target: str          # Target object (browser, screenshot, volume, etc.)  
    modifiers: List[str] # Additional modifiers (full, partial, up, down, etc.)
    confidence: float    # Confidence score (0.0 - 1.0)
    raw_query: str       # Original query text

class NLPQueryProcessor:
    """Processes natural language queries for i3 keybinding searches"""
    
    def __init__(self, dictionaries_path: Optional[Path] = None):
        self.dictionaries_path = dictionaries_path
        
        # Core NLP patterns and mappings
        self.action_verbs = {
            # Primary actions
            'open': ['open', 'launch', 'start', 'run', 'execute', 'fire up'],
            'close': ['close', 'kill', 'quit', 'exit', 'terminate', 'shut'],
            'take': ['take', 'capture', 'grab', 'snap', 'shoot'],
            'change': ['change', 'adjust', 'modify', 'set', 'alter'],
            'switch': ['switch', 'go to', 'move to', 'navigate to', 'jump to'],
            'move': ['move', 'send', 'transfer', 'relocate', 'shift'],
            'resize': ['resize', 'make bigger', 'make smaller', 'expand', 'shrink'],
            'toggle': ['toggle', 'flip', 'switch on', 'switch off', 'enable', 'disable'],
            'lock': ['lock', 'secure', 'protect'],
            'reload': ['reload', 'refresh', 'restart', 'reboot'],
            'show': ['show', 'display', 'view', 'see', 'list'],
            'hide': ['hide', 'minimize', 'conceal'],
            'focus': ['focus', 'select', 'activate', 'highlight'],
            'split': ['split', 'divide', 'separate'],
            'float': ['float', 'make floating', 'unfloat', 'make tiled']
        }
        
        self.target_objects = {
            # Applications and tools
            'browser': ['browser', 'web browser', 'internet', 'firefox', 'chrome', 'brave'],
            'terminal': ['terminal', 'console', 'shell', 'command line', 'cmd'],
            'launcher': ['launcher', 'menu', 'dmenu', 'rofi', 'application menu'],
            'file_manager': ['file manager', 'files', 'folder', 'directory', 'nautilus', 'thunar'],
            'editor': ['editor', 'text editor', 'code editor', 'vim', 'emacs', 'vscode'],
            
            # System functions
            'screenshot': ['screenshot', 'screen capture', 'print screen', 'screen shot'],
            'volume': ['volume', 'sound', 'audio', 'speaker', 'music'],
            'brightness': ['brightness', 'screen brightness', 'backlight', 'display'],
            'screen': ['screen', 'display', 'monitor'],
            'system': ['system', 'computer', 'machine'],
            
            # Window management
            'window': ['window', 'app', 'application', 'program'],
            'workspace': ['workspace', 'desktop', 'virtual desktop', 'screen'],
            'layout': ['layout', 'arrangement', 'organization'],
            
            # Media controls
            'media': ['media', 'music', 'player', 'playback', 'song', 'track'],
            'microphone': ['microphone', 'mic', 'recording'],
            
            # Power and security
            'lock_screen': ['lock screen', 'screen lock', 'security', 'lock'],
            'power': ['power', 'shutdown', 'restart', 'suspend', 'hibernate']
        }
        
        self.modifiers = {
            # Directions and positions
            'up': ['up', 'higher', 'increase', 'raise', 'boost'],
            'down': ['down', 'lower', 'decrease', 'reduce', 'drop'],
            'left': ['left', 'previous', 'back'],
            'right': ['right', 'next', 'forward'],
            'full': ['full', 'fullscreen', 'maximize', 'maximized'],
            'partial': ['partial', 'windowed', 'restore', 'normal'],
            'floating': ['floating', 'float', 'free'],
            'tiled': ['tiled', 'tile', 'docked', 'attached'],
            
            # Quantities and ranges  
            'all': ['all', 'everything', 'every'],
            'current': ['current', 'active', 'selected', 'this'],
            'next': ['next', 'following', 'subsequent'],
            'previous': ['previous', 'last', 'prior'],
            
            # States
            'on': ['on', 'enable', 'activate', 'turn on'],
            'off': ['off', 'disable', 'deactivate', 'turn off'],
            'mute': ['mute', 'silence', 'quiet'],
            'unmute': ['unmute', 'unsilence', 'audible']
        }
        
        # Common query patterns (regex patterns for structured parsing)
        self.query_patterns = [
            # Action + Target patterns
            (r'^(open|launch|start|run)\s+(?:the\s+)?(browser|terminal|launcher|file manager)', 'action_target'),
            (r'^(take|capture|grab)\s+(?:a\s+)?(screenshot|screen capture)', 'action_target'),
            (r'^(change|adjust|set)\s+(?:the\s+)?(volume|brightness)', 'action_target'),
            (r'^(switch|go)\s+to\s+(?:the\s+)?(workspace|desktop)\s*(\d+)?', 'action_target_param'),
            (r'^(move|send)\s+(?:window\s+)?to\s+(?:workspace\s+)?(\d+)', 'action_target_param'),
            (r'^(make|set)\s+(?:window\s+)?(fullscreen|floating|maximized)', 'action_modifier'),
            (r'^(lock|secure)\s+(?:the\s+)?(screen)', 'action_target'),
            (r'^(reload|restart|refresh)\s+(?:the\s+)?(config|configuration|i3)', 'action_target'),
            (r'^(show|display|list)\s+(?:all\s+)?(keybindings|shortcuts|bindings)', 'action_target'),
            
            # Volume specific patterns
            (r'^(turn|make)\s+(volume|sound|audio)\s+(up|down|higher|lower)', 'action_target_modifier'),
            (r'^(mute|unmute|silence)\s+(?:the\s+)?(volume|sound|audio|microphone|mic)', 'action_target'),
            
            # Window management patterns
            (r'^(close|kill|quit)\s+(?:the\s+)?(?:current\s+)?(window|app|application)', 'action_target'),
            (r'^(focus|select)\s+(?:the\s+)?(left|right|up|down)\s+(?:window)?', 'action_modifier'),
            (r'^(resize|make)\s+(?:window\s+)?(bigger|smaller|larger)', 'action_modifier'),
            (r'^(split|divide)\s+(?:window\s+)?(horizontally|vertically|horizontal|vertical)', 'action_modifier'),
            
            # Layout patterns  
            (r'^(?:change|set|use)\s+(?:to\s+)?(tabbed|stacking|split)\s+layout', 'action_target'),
            (r'^toggle\s+(fullscreen|floating|split)', 'action_target')
        ]
        
        # Intent to command mappings (will be enhanced by search dictionaries)
        self.intent_mappings = {
            # Application launches
            ('open', 'browser'): ['firefox', 'chrome', 'brave', 'browser'],
            ('open', 'terminal'): ['terminal', 'console', 'shell', 'warp-terminal', 'alacritty'],
            ('open', 'launcher'): ['dmenu', 'rofi', 'application launcher'],
            ('open', 'file_manager'): ['nautilus', 'thunar', 'file manager', 'files'],
            
            # Screenshots
            ('take', 'screenshot'): ['screenshot', 'flameshot', 'print screen', 'capture'],
            
            # Audio controls
            ('change', 'volume', 'up'): ['volume up', 'increase volume', 'raise volume'],
            ('change', 'volume', 'down'): ['volume down', 'decrease volume', 'lower volume'],
            ('toggle', 'volume'): ['mute', 'toggle mute', 'volume toggle'],
            
            # Brightness
            ('change', 'brightness', 'up'): ['brightness up', 'increase brightness'],
            ('change', 'brightness', 'down'): ['brightness down', 'decrease brightness'],
            
            # Window management
            ('close', 'window'): ['close window', 'kill window', 'quit'],
            ('toggle', 'window', 'full'): ['fullscreen', 'maximize', 'toggle fullscreen'],
            ('toggle', 'window', 'floating'): ['floating', 'toggle floating'],
            
            # Workspaces
            ('switch', 'workspace'): ['switch workspace', 'go to workspace', 'workspace'],
            ('move', 'workspace'): ['move to workspace', 'send to workspace'],
            
            # System
            ('lock', 'screen'): ['lock screen', 'screen lock', 'i3lock'],
            ('reload', 'config'): ['reload config', 'restart i3', 'reload configuration']
        }
        
        # Load additional dictionaries if available
        self.load_nlp_dictionaries()
    
    def load_nlp_dictionaries(self) -> None:
        """Load NLP-specific dictionaries from JSON file"""
        if not self.dictionaries_path or not self.dictionaries_path.exists():
            return
            
        try:
            with open(self.dictionaries_path, 'r') as f:
                data = json.load(f)
                
            # Enhance existing mappings with dictionary data
            nlp_data = data.get('nlp', {})
            
            # Add custom action verbs
            custom_actions = nlp_data.get('action_verbs', {})
            for action, variants in custom_actions.items():
                if action in self.action_verbs:
                    self.action_verbs[action].extend(variants)
                else:
                    self.action_verbs[action] = variants
            
            # Add custom target objects
            custom_targets = nlp_data.get('target_objects', {})
            for target, variants in custom_targets.items():
                if target in self.target_objects:
                    self.target_objects[target].extend(variants)
                else:
                    self.target_objects[target] = variants
            
            # Add custom intent mappings
            custom_intents = nlp_data.get('intent_mappings', {})
            for intent_key, search_terms in custom_intents.items():
                # Convert string key back to tuple if needed
                if isinstance(intent_key, str):
                    intent_tuple = tuple(intent_key.split('|'))
                    self.intent_mappings[intent_tuple] = search_terms
                    
        except Exception as e:
            print(f"Warning: Could not load NLP dictionaries: {e}")
    
    def parse_query(self, query: str) -> QueryIntent:
        """Parse a natural language query into structured intent"""
        clean_query = query.lower().strip()
        
        # Try pattern matching first
        for pattern, pattern_type in self.query_patterns:
            match = re.search(pattern, clean_query)
            if match:
                return self._parse_pattern_match(match, pattern_type, clean_query)
        
        # Fallback to word-based parsing
        return self._parse_words(clean_query)
    
    def _parse_pattern_match(self, match, pattern_type: str, query: str) -> QueryIntent:
        """Parse a regex pattern match into QueryIntent"""
        groups = match.groups()
        
        if pattern_type == 'action_target':
            action = self._normalize_action(groups[0])
            target = self._normalize_target(groups[1])
            return QueryIntent(action, target, [], 0.9, query)
            
        elif pattern_type == 'action_target_param':
            action = self._normalize_action(groups[0])
            target = self._normalize_target(groups[1])
            param = groups[2] if len(groups) > 2 and groups[2] else None
            modifiers = [param] if param else []
            return QueryIntent(action, target, modifiers, 0.9, query)
            
        elif pattern_type == 'action_modifier':
            action = self._normalize_action(groups[0])
            modifier = self._normalize_modifier(groups[1])
            return QueryIntent(action, 'window', [modifier], 0.8, query)
            
        elif pattern_type == 'action_target_modifier':
            action = self._normalize_action(groups[0])
            target = self._normalize_target(groups[1])
            modifier = self._normalize_modifier(groups[2])
            return QueryIntent(action, target, [modifier], 0.9, query)
        
        # Default fallback
        return QueryIntent('unknown', 'unknown', [], 0.1, query)
    
    def _parse_words(self, query: str) -> QueryIntent:
        """Parse query by analyzing individual words"""
        words = re.findall(r'\b\w+\b', query)
        
        # Find action verbs
        action = 'unknown'
        action_confidence = 0.0
        for word in words:
            for act, variants in self.action_verbs.items():
                if word in variants:
                    action = act
                    action_confidence = 0.7
                    break
            if action != 'unknown':
                break
        
        # Find target objects
        target = 'unknown'
        target_confidence = 0.0
        for word in words:
            for tgt, variants in self.target_objects.items():
                if word in variants or any(word in variant.split() for variant in variants):
                    target = tgt
                    target_confidence = 0.7
                    break
            if target != 'unknown':
                break
        
        # Find modifiers
        modifiers = []
        for word in words:
            for mod, variants in self.modifiers.items():
                if word in variants:
                    modifiers.append(mod)
                    break
        
        confidence = (action_confidence + target_confidence) / 2
        return QueryIntent(action, target, modifiers, confidence, query)
    
    def _normalize_action(self, action: str) -> str:
        """Normalize action to canonical form"""
        action = action.lower()
        for canonical, variants in self.action_verbs.items():
            if action in variants:
                return canonical
        return action
    
    def _normalize_target(self, target: str) -> str:
        """Normalize target to canonical form"""
        target = target.lower()
        for canonical, variants in self.target_objects.items():
            if target in variants or any(target in variant for variant in variants):
                return canonical
        return target
    
    def _normalize_modifier(self, modifier: str) -> str:
        """Normalize modifier to canonical form"""
        modifier = modifier.lower()
        for canonical, variants in self.modifiers.items():
            if modifier in variants:
                return canonical
        return modifier
    
    def get_search_terms(self, intent: QueryIntent) -> List[str]:
        """Convert parsed intent to search terms for keybinding lookup"""
        search_terms = []
        
        # Build intent key for lookup
        intent_key = (intent.action, intent.target)
        if intent.modifiers:
            intent_key = intent_key + tuple(intent.modifiers)
        
        # Look for exact intent mapping
        if intent_key in self.intent_mappings:
            search_terms.extend(self.intent_mappings[intent_key])
        
        # Try partial matches (without modifiers)
        partial_key = (intent.action, intent.target)
        if partial_key in self.intent_mappings:
            search_terms.extend(self.intent_mappings[partial_key])
        
        # Add individual components as search terms
        if intent.action != 'unknown':
            search_terms.extend(self.action_verbs.get(intent.action, [intent.action]))
        
        if intent.target != 'unknown':
            search_terms.extend(self.target_objects.get(intent.target, [intent.target]))
        
        for modifier in intent.modifiers:
            search_terms.extend(self.modifiers.get(modifier, [modifier]))
        
        # Remove duplicates and return
        return list(set(search_terms))
    
    def suggest_queries(self, partial_query: str) -> List[str]:
        """Suggest complete queries based on partial input"""
        partial = partial_query.lower().strip()
        suggestions = []
        
        # Common query suggestions based on popular intents
        common_queries = [
            "open browser",
            "open terminal", 
            "take screenshot",
            "change volume up",
            "change volume down",
            "mute volume",
            "lock screen",
            "switch workspace",
            "close window",
            "make window fullscreen",
            "toggle floating window",
            "reload config",
            "show keybindings",
            "change brightness up",
            "change brightness down",
            "open file manager",
            "open launcher"
        ]
        
        # Filter suggestions based on partial input
        for query in common_queries:
            if not partial or any(word.startswith(partial) or partial in word for word in query.split()):
                suggestions.append(query)
        
        return suggestions[:8]  # Limit to top 8 suggestions
    
    def is_natural_language_query(self, query: str) -> bool:
        """Determine if a query is natural language vs keyword search"""
        query = query.lower().strip()
        
        # Check for natural language indicators
        nl_indicators = [
            # Action verbs
            'open', 'launch', 'start', 'run', 'take', 'capture', 'grab',
            'change', 'adjust', 'set', 'switch', 'go to', 'move', 'send',
            'close', 'kill', 'quit', 'lock', 'show', 'make', 'toggle',
            
            # Articles and prepositions
            'the', 'a', 'an', 'to', 'up', 'down', 'on', 'off',
            
            # Common NL phrases
            'how to', 'how do i', 'i want to', 'i need to'
        ]
        
        # If query contains multiple words and at least one NL indicator
        words = query.split()
        if len(words) > 1:
            if any(indicator in query for indicator in nl_indicators):
                return True
        
        # Check for question patterns
        question_patterns = [
            r'^(how|what|where|when|why)\s+',
            r'^(can|could|should|would)\s+i\s+',
            r'^(is|are)\s+there\s+'
        ]
        
        for pattern in question_patterns:
            if re.match(pattern, query):
                return True
        
        return False
    
    def get_query_explanation(self, intent: QueryIntent) -> str:
        """Generate human-readable explanation of parsed intent"""
        if intent.confidence < 0.3:
            return f"I'm not sure what '{intent.raw_query}' means. Try being more specific."
        
        explanation = f"Looking for ways to {intent.action}"
        
        if intent.target != 'unknown':
            explanation += f" {intent.target}"
        
        if intent.modifiers:
            explanation += f" ({', '.join(intent.modifiers)})"
        
        explanation += f" (confidence: {intent.confidence:.0%})"
        
        return explanation

def demo():
    """Demo the NLP query processor"""
    processor = NLPQueryProcessor()
    
    test_queries = [
        "open browser",
        "take screenshot", 
        "change volume up",
        "lock screen",
        "switch to workspace 3",
        "make window fullscreen",
        "close current window",
        "mute audio",
        "show all keybindings",
        "toggle floating window"
    ]
    
    print("=== NLP Query Processor Demo ===\\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        
        # Check if it's natural language
        is_nl = processor.is_natural_language_query(query)
        print(f"Natural Language: {is_nl}")
        
        # Parse the query
        intent = processor.parse_query(query)
        print(f"Parsed Intent: {intent}")
        
        # Get search terms
        search_terms = processor.get_search_terms(intent)
        print(f"Search Terms: {search_terms}")
        
        # Get explanation
        explanation = processor.get_query_explanation(intent)
        print(f"Explanation: {explanation}")
        
        print("-" * 50)

if __name__ == '__main__':
    demo()
