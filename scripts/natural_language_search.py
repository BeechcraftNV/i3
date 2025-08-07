#!/usr/bin/env python3
"""
Natural Language Search Enhancement for i3 Help System
Understands queries like "how do I make window bigger" and maps to appropriate keybindings
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from difflib import get_close_matches

class NaturalLanguageSearch:
    def __init__(self, dictionaries_path: Path = None):
        if dictionaries_path is None:
            dictionaries_path = Path.home() / '.config' / 'i3' / 'scripts' / 'search_dictionaries.json'
        
        self.dictionaries_path = dictionaries_path
        self.load_language_patterns()
        
        # Natural language patterns for common queries
        self.query_patterns = {
            # Window management
            r'(how.*(do|can).*)?(make|resize|change).*(window|app).*(big|large|small|size)': ['resize', 'window size'],
            r'(how.*)?(close|kill|quit|exit).*(window|app|program)': ['kill', 'close window', 'quit'],
            r'(how.*)?(move|drag|send).*(window|app).*(left|right|up|down|monitor|screen|workspace)': ['move', 'window movement'],
            r'(how.*)?(switch|change|go).*(window|app|focus)': ['focus', 'switch window'],
            r'make.*(window|app).*(full.*screen|maximize)': ['fullscreen', 'maximize'],
            r'(float|popup|detach).*(window|app)': ['floating', 'float window'],
            r'(tile|attach|dock).*(window|app)': ['tiling', 'tile window'],
            
            # Workspace management
            r'(how.*)?(switch|change|go|move).*(workspace|desktop|screen)\s*(\d+)?': ['workspace', 'switch workspace'],
            r'(create|new|add).*(workspace|desktop)': ['new workspace', 'create workspace'],
            r'(move|send|put).*(this|window|app).*(workspace|desktop|other.*screen)': ['move to workspace'],
            r'next.*(workspace|desktop|screen)': ['next workspace', 'workspace next'],
            r'(previous|prev|last).*(workspace|desktop|screen)': ['previous workspace', 'workspace prev'],
            
            # Application launching
            r'(how.*)?(open|launch|start|run).*(terminal|console|shell|cmd)': ['terminal', 'open terminal'],
            r'(how.*)?(open|launch|start).*(browser|web|internet|firefox|chrome)': ['browser', 'open browser'],
            r'(how.*)?(open|launch|start).*(file.*manager|files|folder|nautilus|thunar)': ['file manager', 'files'],
            r'(how.*)?(open|launch).*(app|application|program|menu|launcher)': ['launcher', 'dmenu', 'rofi'],
            
            # System control
            r'(how.*)?(lock|secure).*(screen|computer|system)': ['lock', 'lock screen'],
            r'(how.*)?(screenshot|capture|snap|picture).*(screen|window|area)?': ['screenshot', 'print screen'],
            r'(how.*)?(volume|sound|audio).*(up|down|increase|decrease|mute)': ['volume', 'audio control'],
            r'(how.*)?(bright|dim|backlight).*(up|down|increase|decrease)': ['brightness', 'backlight'],
            r'(reload|refresh|restart).*(config|i3|wm)': ['reload', 'restart i3'],
            r'(exit|logout|quit).*(i3|session|wm)': ['exit i3', 'logout'],
            
            # Layout management
            r'(split|divide).*(horizontal|vertical|window)': ['split', 'layout split'],
            r'(tab|stack).*(layout|window|mode)': ['tabbed', 'stacking', 'layout'],
            r'(how.*)?(arrange|organize|layout).*(window|tile)': ['layout', 'arrange windows'],
            
            # Common questions
            r'what.*(key|shortcut|binding).*(for|to)?\s*(.+)': ['keybinding for'],
            r'how.*(do|can).*(i|you)\s+(.+)': ['how to'],
            r'(show|list|display).*(all|available)?.*(key|shortcut|binding|command)': ['show all', 'list keybindings'],
            r'(help|assist|guide).*(with)?\s*(.*)': ['help with'],
            
            # Size and position
            r'(bigger|larger|increase).*(window|size)': ['resize grow', 'increase size'],
            r'(smaller|decrease|shrink).*(window|size)': ['resize shrink', 'decrease size'],
            r'(center|middle).*(window|screen)': ['center window', 'move center'],
            r'(left|right|top|bottom).*(half|side).*(screen)?': ['snap window', 'tile half'],
            
            # Multi-monitor
            r'(move|send|put).*(other|second|external).*(monitor|screen|display)': ['move to output', 'other monitor'],
            r'(switch|change).*(monitor|screen|display)': ['focus output', 'switch monitor'],
            
            # Modes
            r'(resize|resizing).*(mode|window)': ['resize mode'],
            r'(enter|exit|leave).*(mode)': ['mode', 'enter mode', 'exit mode'],
        }
        
        # Action verb mappings
        self.action_verbs = {
            'open': ['launch', 'start', 'run', 'execute', 'bring up', 'fire up'],
            'close': ['kill', 'quit', 'exit', 'terminate', 'end', 'stop'],
            'move': ['drag', 'send', 'transfer', 'relocate', 'shift', 'put'],
            'resize': ['size', 'scale', 'grow', 'shrink', 'expand', 'contract'],
            'switch': ['change', 'go to', 'navigate', 'jump', 'focus'],
            'create': ['new', 'add', 'make'],
            'delete': ['remove', 'destroy', 'kill'],
            'show': ['display', 'view', 'list', 'reveal'],
            'hide': ['minimize', 'conceal'],
            'toggle': ['switch', 'flip', 'change'],
            'lock': ['secure', 'protect'],
            'reload': ['refresh', 'restart', 'reset'],
        }
        
        # Object mappings
        self.objects = {
            'window': ['app', 'application', 'program', 'software'],
            'workspace': ['desktop', 'virtual desktop', 'screen', 'space'],
            'terminal': ['console', 'shell', 'command line', 'cmd', 'term'],
            'browser': ['web browser', 'internet', 'firefox', 'chrome', 'brave'],
            'file manager': ['files', 'folder', 'explorer', 'nautilus', 'thunar'],
            'launcher': ['menu', 'app menu', 'dmenu', 'rofi'],
            'screen': ['monitor', 'display', 'output'],
        }
        
        # Direction mappings
        self.directions = {
            'left': ['west', 'previous', 'back'],
            'right': ['east', 'next', 'forward'],
            'up': ['north', 'above', 'top'],
            'down': ['south', 'below', 'bottom'],
        }
        
        # Size modifiers
        self.size_modifiers = {
            'bigger': ['larger', 'increase', 'grow', 'expand', 'maximize'],
            'smaller': ['decrease', 'shrink', 'reduce', 'minimize'],
            'full': ['fullscreen', 'maximize', 'max'],
        }
    
    def load_language_patterns(self):
        """Load existing dictionaries and extend with NLP patterns"""
        try:
            if self.dictionaries_path.exists():
                with open(self.dictionaries_path, 'r') as f:
                    data = json.load(f)
                    self.synonyms = data.get('synonyms', {})
                    self.intents = data.get('intents', {})
            else:
                self.synonyms = {}
                self.intents = {}
        except Exception as e:
            print(f"Warning: Could not load dictionaries: {e}")
            self.synonyms = {}
            self.intents = {}
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess and normalize the query"""
        # Convert to lowercase
        query = query.lower()
        
        # Remove common filler words
        filler_words = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'been', 
                       'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                       'would', 'could', 'should', 'may', 'might', 'must',
                       'shall', 'can', 'need', 'dare', 'ought', 'i', 'you',
                       'please', 'thanks', 'thank you']
        
        # Remove question marks and excessive punctuation
        query = re.sub(r'[?!.,;]+', ' ', query)
        
        # Remove filler words but keep important ones
        words = query.split()
        filtered_words = []
        for word in words:
            if word not in filler_words or len(words) <= 3:
                filtered_words.append(word)
        
        return ' '.join(filtered_words).strip()
    
    def extract_intent(self, query: str) -> Dict[str, List[str]]:
        """Extract intent from natural language query"""
        intents = {
            'action': [],
            'object': [],
            'modifier': [],
            'direction': [],
            'search_terms': []
        }
        
        # Preprocess query
        clean_query = self.preprocess_query(query)
        
        # Check against query patterns
        for pattern, terms in self.query_patterns.items():
            if re.search(pattern, clean_query, re.IGNORECASE):
                intents['search_terms'].extend(terms)
        
        # Extract action verbs
        for base_verb, synonyms in self.action_verbs.items():
            if base_verb in clean_query or any(syn in clean_query for syn in synonyms):
                intents['action'].append(base_verb)
        
        # Extract objects
        for base_object, synonyms in self.objects.items():
            if base_object in clean_query or any(syn in clean_query for syn in synonyms):
                intents['object'].append(base_object)
        
        # Extract directions
        for direction, synonyms in self.directions.items():
            if direction in clean_query or any(syn in clean_query for syn in synonyms):
                intents['direction'].append(direction)
        
        # Extract size modifiers
        for modifier, synonyms in self.size_modifiers.items():
            if modifier in clean_query or any(syn in clean_query for syn in synonyms):
                intents['modifier'].append(modifier)
        
        # Add individual words as fallback search terms
        if not intents['search_terms']:
            intents['search_terms'] = clean_query.split()
        
        return intents
    
    def generate_search_keywords(self, query: str) -> List[str]:
        """Generate search keywords from natural language query"""
        keywords = set()
        
        # Extract intent
        intent = self.extract_intent(query)
        
        # Add all search terms
        keywords.update(intent['search_terms'])
        
        # Combine action + object
        for action in intent['action']:
            for obj in intent['object']:
                keywords.add(f"{action} {obj}")
                keywords.add(action)
                keywords.add(obj)
        
        # Add modifiers and directions
        keywords.update(intent['modifier'])
        keywords.update(intent['direction'])
        
        # Expand with synonyms
        expanded_keywords = set(keywords)
        for keyword in keywords:
            if keyword in self.synonyms:
                expanded_keywords.update(self.synonyms[keyword])
        
        # Add intent-based expansions
        for keyword in keywords:
            for intent_key, intent_values in self.intents.items():
                if keyword in intent_key.lower():
                    expanded_keywords.update(intent_values)
        
        return list(expanded_keywords)
    
    def score_binding(self, binding: Dict, keywords: List[str]) -> float:
        """Score a binding based on keyword relevance"""
        score = 0.0
        
        # Get binding text for matching
        binding_text = f"{binding.get('description', '')} {binding.get('command', '')} {binding.get('key', '')}".lower()
        binding_search = binding.get('search_text', '').lower()
        
        # Exact matches get highest score
        for keyword in keywords:
            if keyword in binding_text:
                score += 10.0
            elif keyword in binding_search:
                score += 8.0
            
            # Partial matches
            words = keyword.split()
            for word in words:
                if len(word) > 2:  # Skip very short words
                    if word in binding_text:
                        score += 3.0
                    elif word in binding_search:
                        score += 2.0
        
        # Fuzzy matching for close matches
        for keyword in keywords:
            close_matches = get_close_matches(keyword, binding_text.split(), n=1, cutoff=0.8)
            if close_matches:
                score += 5.0
        
        return score
    
    def search(self, query: str, bindings: List[Dict]) -> List[Tuple[Dict, float]]:
        """Search bindings using natural language query"""
        # Generate keywords from query
        keywords = self.generate_search_keywords(query)
        
        # Score all bindings
        results = []
        for binding in bindings:
            score = self.score_binding(binding, keywords)
            if score > 0:
                results.append((binding, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def get_query_interpretation(self, query: str) -> str:
        """Get human-readable interpretation of the query"""
        intent = self.extract_intent(query)
        keywords = self.generate_search_keywords(query)
        
        interpretation = []
        
        if intent['action']:
            interpretation.append(f"Action: {', '.join(intent['action'])}")
        if intent['object']:
            interpretation.append(f"Target: {', '.join(intent['object'])}")
        if intent['modifier']:
            interpretation.append(f"Modifier: {', '.join(intent['modifier'])}")
        if intent['direction']:
            interpretation.append(f"Direction: {', '.join(intent['direction'])}")
        
        interpretation.append(f"Search terms: {', '.join(keywords[:5])}")
        
        return " | ".join(interpretation)
    
    def get_suggestions_for_query(self, query: str) -> List[str]:
        """Get alternative query suggestions"""
        suggestions = []
        intent = self.extract_intent(query)
        
        # Suggest more specific queries
        if intent['action'] and not intent['object']:
            suggestions.append(f"Try: '{intent['action'][0]} window' or '{intent['action'][0]} workspace'")
        
        if intent['object'] and not intent['action']:
            suggestions.append(f"Try: 'open {intent['object'][0]}' or 'close {intent['object'][0]}'")
        
        # Suggest common related queries
        if 'resize' in query.lower() or 'size' in query.lower():
            suggestions.extend([
                "resize window bigger",
                "resize window smaller",
                "enter resize mode",
                "fullscreen toggle"
            ])
        
        if 'move' in query.lower():
            suggestions.extend([
                "move window to workspace",
                "move window left/right/up/down",
                "move to other monitor"
            ])
        
        if 'open' in query.lower() or 'launch' in query.lower():
            suggestions.extend([
                "open terminal",
                "open browser",
                "open file manager",
                "open application launcher"
            ])
        
        return suggestions

class NaturalLanguageHelp:
    """Integration helper for i3-help.py"""
    
    def __init__(self):
        self.nl_search = NaturalLanguageSearch()
    
    def process_query(self, query: str, bindings: List[Dict]) -> Dict:
        """Process a natural language query and return results"""
        # Get interpretation
        interpretation = self.nl_search.get_query_interpretation(query)
        
        # Search bindings
        results = self.nl_search.search(query, bindings)
        
        # Get suggestions
        suggestions = self.nl_search.get_suggestions_for_query(query)
        
        return {
            'query': query,
            'interpretation': interpretation,
            'results': results[:20],  # Top 20 results
            'suggestions': suggestions,
            'keywords': self.nl_search.generate_search_keywords(query)
        }
    
    def format_results(self, results: Dict) -> str:
        """Format results for display"""
        lines = []
        
        # Header
        lines.append("🤖 NATURAL LANGUAGE SEARCH")
        lines.append("=" * 50)
        lines.append(f"Query: '{results['query']}'")
        lines.append(f"Understanding: {results['interpretation']}")
        lines.append("")
        
        # Results
        if results['results']:
            lines.append(f"📊 Found {len(results['results'])} matching keybindings:")
            lines.append("-" * 50)
            
            for binding, score in results['results'][:10]:
                relevance = "⭐" * min(5, int(score / 10))
                lines.append(f"{relevance} [{binding['key']}] → {binding['description']}")
                if score >= 50:
                    lines.append(f"    Perfect match! (Score: {score:.1f})")
                elif score >= 30:
                    lines.append(f"    Good match (Score: {score:.1f})")
                else:
                    lines.append(f"    Possible match (Score: {score:.1f})")
        else:
            lines.append("❌ No matching keybindings found.")
        
        # Suggestions
        if results['suggestions']:
            lines.append("")
            lines.append("💡 Try these queries:")
            for suggestion in results['suggestions']:
                lines.append(f"  • {suggestion}")
        
        return '\n'.join(lines)

def test_natural_language():
    """Test the natural language search"""
    nl_help = NaturalLanguageHelp()
    
    # Test bindings (simplified)
    test_bindings = [
        {'key': '$mod+r', 'description': 'Resize mode', 'command': 'mode "resize"', 'search_text': 'resize mode window size'},
        {'key': '$mod+Shift+h', 'description': 'Move window left', 'command': 'move left', 'search_text': 'move window left direction'},
        {'key': '$mod+f', 'description': 'Toggle fullscreen', 'command': 'fullscreen toggle', 'search_text': 'fullscreen maximize window'},
        {'key': '$mod+Return', 'description': 'Open terminal', 'command': 'exec terminal', 'search_text': 'terminal console shell'},
        {'key': '$mod+Shift+q', 'description': 'Kill window', 'command': 'kill', 'search_text': 'close kill quit window'},
    ]
    
    # Test queries
    test_queries = [
        "how do I make the window bigger?",
        "resize window",
        "open terminal",
        "move this to the left",
        "make it fullscreen",
        "close this window",
        "how to switch workspace",
        "lock my screen",
        "take a screenshot"
    ]
    
    print("🧪 Testing Natural Language Search")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)
        
        results = nl_help.process_query(query, test_bindings)
        
        print(f"🧠 Interpretation: {results['interpretation']}")
        print(f"🔍 Keywords: {', '.join(results['keywords'][:5])}")
        
        if results['results']:
            print(f"✅ Found {len(results['results'])} matches:")
            for binding, score in results['results'][:3]:
                print(f"   [{binding['key']}] {binding['description']} (score: {score:.1f})")
        else:
            print("❌ No matches found")
        
        if results['suggestions']:
            print("💡 Suggestions:", ', '.join(results['suggestions'][:2]))

if __name__ == "__main__":
    test_natural_language()
