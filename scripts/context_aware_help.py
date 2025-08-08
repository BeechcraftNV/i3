#!/usr/bin/env python3
"""
Context-aware help mode for i3-help.py
Shows relevant keybindings based on current window/workspace
"""

import subprocess
import json
from typing import Dict, List

class ContextAwareHelp:
    def get_current_context(self) -> Dict:
        """Get current i3 context (focused window, workspace, etc.)"""
        try:
            # Get current workspace
            ws_output = subprocess.run(
                ['i3-msg', '-t', 'get_workspaces'],
                capture_output=True, text=True
            )
            workspaces = json.loads(ws_output.stdout)
            current_ws = next((ws for ws in workspaces if ws['focused']), None)
            
            # Get focused window
            tree_output = subprocess.run(
                ['i3-msg', '-t', 'get_tree'],
                capture_output=True, text=True
            )
            tree = json.loads(tree_output.stdout)
            
            # Get window class
            window_class = self._find_focused_window_class(tree)
            
            return {
                'workspace': current_ws['name'] if current_ws else None,
                'workspace_num': current_ws['num'] if current_ws else None,
                'window_class': window_class,
                'is_floating': self._is_floating_focused(tree),
                'is_fullscreen': self._is_fullscreen_focused(tree),
                'layout': current_ws.get('layout') if current_ws else None
            }
        except Exception as e:
            return {}
    
    def _find_focused_window_class(self, node: Dict) -> str:
        """Recursively find focused window class"""
        if node.get('focused'):
            return node.get('window_properties', {}).get('class', '')
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            result = self._find_focused_window_class(child)
            if result:
                return result
        return ''
    
    def _is_floating_focused(self, node: Dict) -> bool:
        """Check if focused window is floating"""
        if node.get('focused'):
            return node.get('type') == 'floating_con'
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            if self._is_floating_focused(child):
                return True
        return False
    
    def _is_fullscreen_focused(self, node: Dict) -> bool:
        """Check if focused window is fullscreen"""
        if node.get('focused'):
            return node.get('fullscreen_mode', 0) > 0
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            if self._is_fullscreen_focused(child):
                return True
        return False
    
    def get_contextual_suggestions(self, context: Dict, all_bindings: List[Dict]) -> Dict[str, List[Dict]]:
        """Get keybinding suggestions based on context"""
        suggestions = {
            'primary': [],      # Most relevant for current context
            'secondary': [],    # Generally useful
            'workspace': [],    # Workspace-specific
            'window': []        # Window management
        }
        
        # Browser context
        if 'firefox' in context.get('window_class', '').lower() or \
           'chrome' in context.get('window_class', '').lower() or \
           'brave' in context.get('window_class', '').lower():
            suggestions['primary'] = [
                b for b in all_bindings 
                if any(x in b['description'].lower() for x in ['tab', 'bookmark', 'refresh'])
            ]
            suggestions['secondary'].append({
                'key': 'Ctrl+L', 
                'description': 'Focus address bar (browser)',
                'command': 'browser_internal'
            })
        
        # Terminal context
        elif 'terminal' in context.get('window_class', '').lower() or \
             'warp' in context.get('window_class', '').lower():
            suggestions['primary'] = [
                b for b in all_bindings
                if any(x in b['description'].lower() for x in ['split', 'pane', 'tab'])
            ]
            suggestions['secondary'].append({
                'key': 'Ctrl+Shift+C',
                'description': 'Copy (terminal)',
                'command': 'terminal_internal'
            })
        
        # Floating window context
        if context.get('is_floating'):
            suggestions['window'] = [
                b for b in all_bindings
                if 'floating' in b['command'] or 'move' in b['command']
            ]
        
        # Fullscreen context
        if context.get('is_fullscreen'):
            suggestions['window'] = [
                b for b in all_bindings
                if 'fullscreen' in b['command']
            ]
        
        # Always show workspace navigation
        current_ws = context.get('workspace_num', 1)
        suggestions['workspace'] = [
            b for b in all_bindings
            if 'workspace' in b['command'] and not 'move container' in b['command']
        ][:5]  # Top 5 workspace bindings
        
        return suggestions

    def format_contextual_help(self, context: Dict, suggestions: Dict) -> str:
        """Format context-aware help display"""
        lines = []
        
        # Header with context
        lines.append("🎯 CONTEXT-AWARE HELP")
        lines.append("=" * 50)
        lines.append(f"Window: {context.get('window_class', 'None')}")
        lines.append(f"Workspace: {context.get('workspace', 'Unknown')}")
        if context.get('is_floating'):
            lines.append("Mode: Floating")
        if context.get('is_fullscreen'):
            lines.append("Mode: Fullscreen")
        lines.append("")
        
        # Suggestions by category
        if suggestions['primary']:
            lines.append("⭐ RECOMMENDED FOR THIS APP")
            lines.append("-" * 30)
            for binding in suggestions['primary']:
                lines.append(f"  [{binding['key']}] → {binding['description']}")
            lines.append("")
        
        if suggestions['window']:
            lines.append("🪟 WINDOW CONTROLS")
            lines.append("-" * 30)
            for binding in suggestions['window']:
                lines.append(f"  [{binding['key']}] → {binding['description']}")
            lines.append("")
        
        if suggestions['workspace']:
            lines.append("🖥️ QUICK WORKSPACE NAV")
            lines.append("-" * 30)
            for binding in suggestions['workspace'][:3]:
                lines.append(f"  [{binding['key']}] → {binding['description']}")
            lines.append("")
        
        return '\n'.join(lines)

# Integration example for i3-help.py:
def show_contextual_help(self):
    """Show context-aware help (add to I3KeybindingHelper class)"""
    ctx_helper = ContextAwareHelp()
    context = ctx_helper.get_current_context()
    suggestions = ctx_helper.get_contextual_suggestions(context, self.bindings)
    display_text = ctx_helper.format_contextual_help(context, suggestions)
    
    # Show with rofi/dmenu
    launcher = self.find_launcher()
    if launcher:
        process = subprocess.Popen(
            launcher,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=display_text)
