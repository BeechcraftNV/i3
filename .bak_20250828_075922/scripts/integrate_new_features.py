#!/usr/bin/env python3
"""
Integration script to add new features to i3-help.py
This shows how to integrate:
1. Conflict Detection
2. Natural Language Search
"""

import sys
from pathlib import Path

# Add script directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import the modules
from conflict_detector import KeybindingConflictDetector
from natural_language_search import NaturalLanguageHelp

def integrate_conflict_detector(helper_instance):
    """
    Add conflict detection to I3KeybindingHelper
    
    Usage in i3-help.py:
    1. Import at top: from conflict_detector import KeybindingConflictDetector
    2. In __init__: self.conflict_detector = KeybindingConflictDetector()
    3. Add menu option for conflict check
    """
    
    # Add to action menu in show_action_menu method:
    action_menu_addition = """
    # In show_action_menu, add this to actions list:
    actions.insert(-1, "🔍 Check Conflicts")
    
    # In the action handler section:
    elif "Check Conflicts" in selected_action:
        self.show_conflict_report()
    """
    
    # Add this method to I3KeybindingHelper class:
    show_conflict_method = """
    def show_conflict_report(self):
        '''Show keybinding conflict analysis'''
        detector = KeybindingConflictDetector()
        
        if detector.parse_config():
            detector.detect_conflicts()
            report = detector.generate_report()
            
            # Show report in rofi with scrolling
            launcher = self.find_launcher()
            if launcher:
                # Modify launcher for better display
                if launcher[0] == 'rofi':
                    conflict_launcher = [
                        'rofi', '-dmenu', '-p', 'Conflicts:', 
                        '-theme-str', 'window { width: 80%; height: 80%; }',
                        '-format', 'i', '-no-custom'
                    ]
                else:
                    conflict_launcher = launcher
                
                # Show report
                process = subprocess.Popen(
                    conflict_launcher,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=report)
            
            # Also save report
            detector.export_json()
            subprocess.run([
                'notify-send', 
                'Conflict Analysis Complete', 
                'Report saved to ~/.config/i3/scripts/conflict_report.txt'
            ])
        else:
            subprocess.run(['notify-send', 'Error', 'Could not parse i3 config'])
    """
    
    return action_menu_addition, show_conflict_method

def integrate_natural_language(helper_instance):
    """
    Add natural language search to I3KeybindingHelper
    
    Usage in i3-help.py:
    1. Import at top: from natural_language_search import NaturalLanguageHelp
    2. In __init__: self.nl_help = NaturalLanguageHelp()
    3. Enhance search functionality
    """
    
    # Modify show_help method to detect natural language:
    enhanced_search = """
    def show_help(self):
        '''Display help with natural language support'''
        if not self.parse_config():
            subprocess.run(['notify-send', 'i3 Help', 'Could not read i3 config file'])
            return
        
        launcher = self.find_launcher()
        if not launcher:
            subprocess.run(['notify-send', 'i3 Help', 'No launcher found'])
            return
        
        # Add prompt for natural language
        if launcher[0] == 'rofi':
            launcher = [
                'rofi', '-dmenu', '-i', '-p', 'Search (natural language supported):', 
                '-theme-str', 'window { width: 60%; } listview { lines: 15; }',
                '-matching', 'fuzzy'
            ]
        
        # First, show search prompt
        search_process = subprocess.Popen(
            launcher,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Provide hint
        search_hint = "Type to search: 'screenshot', 'volume', or ask: 'how do I resize window?'\\n"
        search_hint += "Press Enter for full list, or type your query:\\n"
        
        stdout, stderr = search_process.communicate(input=search_hint)
        
        if search_process.returncode == 0 and stdout.strip():
            query = stdout.strip()
            
            # Check if it's a natural language query
            if self.is_natural_language_query(query):
                self.show_natural_language_results(query)
            else:
                # Traditional search
                self.show_filtered_results(query)
        else:
            # Show full list
            display_text = self.format_for_display()
            self.show_menu(display_text)
    """
    
    # Add helper methods:
    helper_methods = """
    def is_natural_language_query(self, query: str) -> bool:
        '''Detect if query is natural language'''
        # Natural language indicators
        nl_indicators = [
            'how', 'what', 'where', 'when', 'why',
            'make', 'change', 'resize', 'move',
            'open', 'close', 'launch', 'start',
            'do i', 'can i', 'to the', 'this'
        ]
        
        query_lower = query.lower()
        
        # Check for question marks or multiple words
        if '?' in query or len(query.split()) > 2:
            return True
        
        # Check for natural language indicators
        return any(indicator in query_lower for indicator in nl_indicators)
    
    def show_natural_language_results(self, query: str):
        '''Show results from natural language search'''
        # Process with NL engine
        if not hasattr(self, 'nl_help'):
            from natural_language_search import NaturalLanguageHelp
            self.nl_help = NaturalLanguageHelp()
        
        results = self.nl_help.process_query(query, self.bindings)
        
        # Format results for display
        display_lines = []
        display_lines.append(f"🤖 Understanding: {results['interpretation']}")
        display_lines.append("=" * 60)
        
        if results['results']:
            for binding, score in results['results'][:15]:
                relevance = "⭐" * min(5, int(score / 10))
                key_part = f"[{binding['key']}]".ljust(20)
                desc_part = binding['description'].ljust(35)
                display_lines.append(f"{relevance} {key_part} {desc_part}")
        else:
            display_lines.append("No matches found. Try rephrasing your query.")
        
        if results['suggestions']:
            display_lines.append("")
            display_lines.append("💡 Suggestions:")
            for suggestion in results['suggestions'][:3]:
                display_lines.append(f"  • {suggestion}")
        
        # Show results
        launcher = self.find_launcher()
        if launcher:
            if launcher[0] == 'rofi':
                result_launcher = [
                    'rofi', '-dmenu', '-p', f'Results for: {query}',
                    '-theme-str', 'window { width: 70%; }'
                ]
            else:
                result_launcher = launcher
            
            process = subprocess.Popen(
                result_launcher,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            display_text = '\\n'.join(display_lines)
            stdout, stderr = process.communicate(input=display_text)
            
            # Handle selection
            if process.returncode == 0 and stdout.strip():
                selected = stdout.strip()
                binding = self.find_binding_by_display(selected)
                if binding:
                    self.show_action_menu(binding)
    
    def show_filtered_results(self, query: str):
        '''Show traditional filtered results'''
        filtered_bindings = []
        query_lower = query.lower()
        
        for binding in self.bindings:
            if query_lower in binding['search_text'].lower() or \\
               query_lower in binding['description'].lower() or \\
               query_lower in binding['key'].lower():
                filtered_bindings.append(binding)
        
        if filtered_bindings:
            # Categorize and display filtered results
            temp_bindings = self.bindings
            self.bindings = filtered_bindings
            self.categorize_bindings()
            display_text = self.format_for_display()
            self.bindings = temp_bindings
            
            self.show_menu(display_text)
        else:
            subprocess.run(['notify-send', 'No Results', f'No bindings found for: {query}'])
    """
    
    return enhanced_search, helper_methods

def create_integration_patch():
    """
    Create a patch file that can be applied to i3-help.py
    """
    patch_content = """
# Integration Patch for i3-help.py
# Apply these changes to add conflict detection and natural language search

## 1. Add imports at the top of i3-help.py:

from conflict_detector import KeybindingConflictDetector
from natural_language_search import NaturalLanguageHelp

## 2. In __init__ method, add:

self.conflict_detector = None  # Will be initialized on demand
self.nl_help = None  # Will be initialized on demand

## 3. Add to the action menu (in show_action_menu method):

# Add before the Cancel option:
actions.insert(-1, "🔍 Check for Conflicts")
actions.insert(-1, "🤖 Natural Language Help")

# In the action handler section, add:
elif "Check for Conflicts" in selected_action:
    self.show_conflict_report()
elif "Natural Language Help" in selected_action:
    self.show_natural_language_prompt()

## 4. Add these new methods to the I3KeybindingHelper class:

def show_conflict_report(self):
    '''Show keybinding conflict analysis'''
    if not self.conflict_detector:
        self.conflict_detector = KeybindingConflictDetector()
    
    subprocess.run(['notify-send', 'Analyzing...', 'Checking for conflicts'])
    
    if self.conflict_detector.parse_config():
        self.conflict_detector.detect_conflicts()
        report = self.conflict_detector.generate_report()
        
        # Show summary notification
        total_issues = sum(len(v) for k, v in self.conflict_detector.conflicts.items() 
                          if k != 'unused_combinations')
        
        if total_issues == 0:
            subprocess.run(['notify-send', '✅ No Conflicts', 'Your keybindings are conflict-free!'])
        else:
            subprocess.run(['notify-send', f'⚠️ {total_issues} Issues Found', 
                          'Check the detailed report'])
        
        # Save reports
        self.conflict_detector.export_json()
        text_path = Path.home() / '.config' / 'i3' / 'scripts' / 'conflict_report.txt'
        with open(text_path, 'w') as f:
            f.write(report)
        
        # Open report in preferred editor or viewer
        subprocess.run(['xdg-open', str(text_path)])

def show_natural_language_prompt(self):
    '''Show natural language search interface'''
    if not self.nl_help:
        self.nl_help = NaturalLanguageHelp()
    
    launcher = self.find_launcher()
    if not launcher:
        return
    
    # Create custom prompt
    if launcher[0] == 'rofi':
        nl_launcher = [
            'rofi', '-dmenu', '-p', '🤖 Ask me anything:',
            '-theme-str', 'window { width: 50%; }',
            '-lines', '0'
        ]
    else:
        nl_launcher = launcher
    
    # Example queries
    examples = [
        "Examples:",
        "• How do I make the window bigger?",
        "• Move this to the other screen",
        "• Open a new terminal",
        "• Lock my computer",
        "• Take a screenshot",
        "",
        "Type your question:"
    ]
    
    process = subprocess.Popen(
        nl_launcher,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input='\\n'.join(examples))
    
    if process.returncode == 0 and stdout.strip():
        query = stdout.strip()
        results = self.nl_help.process_query(query, self.bindings)
        
        # Show formatted results
        display_text = self.nl_help.format_results(results)
        
        # Display in rofi
        if launcher[0] == 'rofi':
            result_launcher = [
                'rofi', '-dmenu', '-p', 'Results:',
                '-theme-str', 'window { width: 70%; } listview { lines: 20; }'
            ]
        else:
            result_launcher = launcher
        
        result_process = subprocess.Popen(
            result_launcher,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        result_stdout, _ = result_process.communicate(input=display_text)
        
        # If a binding was selected, show action menu
        if result_process.returncode == 0 and result_stdout.strip():
            selected_line = result_stdout.strip()
            # Extract key from selected line
            if '[' in selected_line and ']' in selected_line:
                binding = self.find_binding_by_display(selected_line)
                if binding:
                    self.show_action_menu(binding)

## 5. Optional: Add keybindings to i3 config:

# Check for conflicts
bindsym $mod+Alt+c exec python3 ~/.config/i3/scripts/i3-help.py --conflicts

# Natural language help
bindsym $mod+Alt+n exec python3 ~/.config/i3/scripts/i3-help.py --natural

## 6. Add command line argument handling (in main function):

if len(sys.argv) > 1:
    if '--conflicts' in sys.argv:
        helper.show_conflict_report()
        return
    elif '--natural' in sys.argv:
        helper.show_natural_language_prompt()
        return
"""
    
    # Save patch file
    patch_path = script_dir / 'integration_patch.txt'
    with open(patch_path, 'w') as f:
        f.write(patch_content)
    
    print(f"✅ Integration patch saved to: {patch_path}")
    print("\n📋 To integrate the new features:")
    print("1. Review the patch file: integration_patch.txt")
    print("2. Apply the changes to i3-help.py")
    print("3. Add the suggested keybindings to your i3 config")
    print("4. Reload i3 configuration (Super+Shift+r)")

if __name__ == "__main__":
    print("🔧 i3-help.py Integration Guide")
    print("=" * 60)
    
    print("\n📦 New Features Ready for Integration:")
    print("1. ✅ Conflict Detection - Finds duplicate, shadowed, and problematic bindings")
    print("2. ✅ Natural Language Search - Understands queries like 'how do I resize window?'")
    
    print("\n🚀 Creating integration patch...")
    create_integration_patch()
    
    print("\n💡 Quick Test Commands:")
    print("# Test conflict detection:")
    print("python3 ~/.config/i3/scripts/conflict_detector.py")
    print("\n# Test natural language search:")
    print("python3 ~/.config/i3/scripts/natural_language_search.py")
    
    print("\n✨ Features are ready to use!")
