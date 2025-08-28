#!/usr/bin/env python3
"""
Command history tracker for i3-help
Provides intelligent suggestions based on usage patterns
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter, defaultdict

class CommandHistoryTracker:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / '.config' / 'i3' / 'scripts'
        
        self.history_file = data_dir / 'command_history.json'
        self.patterns_file = data_dir / 'usage_patterns.json'
        self.history = self.load_history()
        self.patterns = self.load_patterns()
    
    def load_history(self) -> Dict:
        """Load command history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'commands': [],  # List of {timestamp, binding_key, description, context}
            'sequences': [],  # Command sequences/workflows
            'time_patterns': defaultdict(list)  # Time-based patterns
        }
    
    def load_patterns(self) -> Dict:
        """Load learned usage patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'common_sequences': {},  # Common command sequences
            'time_based': {},  # Time-of-day patterns
            'context_based': {},  # Context-specific patterns
            'workflow_chains': []  # Multi-step workflows
        }
    
    def record_command(self, binding: Dict, context: Dict = None):
        """Record a command execution"""
        entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'binding_key': binding['key'],
            'description': binding['description'],
            'command': binding['command'],
            'category': binding.get('category', ''),
            'context': context or {}
        }
        
        self.history['commands'].append(entry)
        
        # Keep only last 1000 commands
        if len(self.history['commands']) > 1000:
            self.history['commands'] = self.history['commands'][-1000:]
        
        # Update sequences
        self.update_sequences(entry)
        
        # Update time patterns
        self.update_time_patterns(entry)
        
        # Save history
        self.save_history()
        
        # Analyze patterns periodically
        if len(self.history['commands']) % 50 == 0:
            self.analyze_patterns()
    
    def update_sequences(self, entry: Dict):
        """Track command sequences"""
        # Get last 5 commands
        recent = self.history['commands'][-5:]
        
        if len(recent) >= 2:
            # Track 2-command sequences
            seq_2 = f"{recent[-2]['binding_key']} -> {recent[-1]['binding_key']}"
            self.history['sequences'].append({
                'sequence': seq_2,
                'timestamp': entry['timestamp']
            })
        
        if len(recent) >= 3:
            # Track 3-command sequences
            seq_3 = f"{recent[-3]['binding_key']} -> {recent[-2]['binding_key']} -> {recent[-1]['binding_key']}"
            self.history['sequences'].append({
                'sequence': seq_3,
                'timestamp': entry['timestamp']
            })
    
    def update_time_patterns(self, entry: Dict):
        """Track time-based usage patterns"""
        dt = datetime.fromisoformat(entry['datetime'])
        hour = dt.hour
        day_part = self.get_day_part(hour)
        
        # Track by hour
        hour_key = f"hour_{hour}"
        if hour_key not in self.history['time_patterns']:
            self.history['time_patterns'][hour_key] = []
        self.history['time_patterns'][hour_key].append(entry['binding_key'])
        
        # Track by day part
        part_key = f"part_{day_part}"
        if part_key not in self.history['time_patterns']:
            self.history['time_patterns'][part_key] = []
        self.history['time_patterns'][part_key].append(entry['binding_key'])
    
    def get_day_part(self, hour: int) -> str:
        """Get part of day from hour"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def analyze_patterns(self):
        """Analyze usage patterns and save insights"""
        # Analyze common sequences
        if self.history['sequences']:
            seq_counter = Counter(s['sequence'] for s in self.history['sequences'])
            self.patterns['common_sequences'] = dict(seq_counter.most_common(10))
        
        # Analyze time-based patterns
        for time_key, commands in self.history['time_patterns'].items():
            if commands:
                cmd_counter = Counter(commands)
                self.patterns['time_based'][time_key] = dict(cmd_counter.most_common(5))
        
        # Identify workflow chains
        self.identify_workflows()
        
        # Save patterns
        self.save_patterns()
    
    def identify_workflows(self):
        """Identify common multi-step workflows"""
        workflows = []
        
        # Look for common patterns
        if len(self.history['commands']) >= 10:
            # Example: Terminal -> Editor -> Git workflow
            for i in range(len(self.history['commands']) - 3):
                cmds = self.history['commands'][i:i+4]
                
                # Check for common workflow patterns
                if any('terminal' in c['description'].lower() for c in cmds[:2]) and \
                   any('edit' in c['description'].lower() or 'code' in c['description'].lower() for c in cmds[1:3]):
                    workflows.append({
                        'name': 'Development Workflow',
                        'steps': [c['binding_key'] for c in cmds],
                        'frequency': 1
                    })
        
        self.patterns['workflow_chains'] = workflows
    
    def get_suggestions(self, current_context: Dict = None) -> Dict[str, List]:
        """Get intelligent suggestions based on history and context"""
        suggestions = {
            'next_likely': [],  # Most likely next commands
            'frequent_now': [],  # Frequently used at this time
            'workflow_suggestions': [],  # Workflow-based suggestions
            'recently_used': [],  # Recently used commands
            'trending': []  # Trending upward in usage
        }
        
        # Get last command
        if self.history['commands']:
            last_cmd = self.history['commands'][-1]['binding_key']
            
            # Find what usually comes next
            for seq, count in self.patterns['common_sequences'].items():
                if seq.startswith(last_cmd + " ->"):
                    next_cmd = seq.split(" -> ")[1]
                    suggestions['next_likely'].append({
                        'key': next_cmd,
                        'confidence': min(count / 10, 1.0),  # Normalize confidence
                        'reason': f"Often follows {last_cmd}"
                    })
        
        # Get time-based suggestions
        current_hour = datetime.now().hour
        day_part = self.get_day_part(current_hour)
        
        hour_key = f"hour_{current_hour}"
        if hour_key in self.patterns['time_based']:
            for cmd, count in list(self.patterns['time_based'][hour_key].items())[:3]:
                suggestions['frequent_now'].append({
                    'key': cmd,
                    'confidence': min(count / 5, 1.0),
                    'reason': f"Frequently used at {current_hour}:00"
                })
        
        # Get recently used (last 10, deduplicated)
        seen = set()
        for cmd in reversed(self.history['commands'][-20:]):
            if cmd['binding_key'] not in seen:
                suggestions['recently_used'].append({
                    'key': cmd['binding_key'],
                    'description': cmd['description']
                })
                seen.add(cmd['binding_key'])
                if len(suggestions['recently_used']) >= 5:
                    break
        
        # Identify trending commands (increasing usage)
        suggestions['trending'] = self.get_trending_commands()
        
        return suggestions
    
    def get_trending_commands(self) -> List[Dict]:
        """Identify commands with increasing usage"""
        trending = []
        
        if len(self.history['commands']) >= 20:
            # Compare last 10 vs previous 10
            recent = self.history['commands'][-10:]
            previous = self.history['commands'][-20:-10]
            
            recent_counts = Counter(c['binding_key'] for c in recent)
            previous_counts = Counter(c['binding_key'] for c in previous)
            
            for cmd, recent_count in recent_counts.items():
                prev_count = previous_counts.get(cmd, 0)
                if recent_count > prev_count:
                    trending.append({
                        'key': cmd,
                        'growth': (recent_count - prev_count) / max(prev_count, 1),
                        'reason': f"↑ {recent_count - prev_count} more uses recently"
                    })
        
        return sorted(trending, key=lambda x: x['growth'], reverse=True)[:3]
    
    def get_statistics(self) -> Dict:
        """Get usage statistics"""
        stats = {
            'total_commands': len(self.history['commands']),
            'unique_commands': len(set(c['binding_key'] for c in self.history['commands'])),
            'common_sequences': len(self.patterns['common_sequences']),
            'identified_workflows': len(self.patterns['workflow_chains'])
        }
        
        # Most used commands
        if self.history['commands']:
            cmd_counter = Counter(c['binding_key'] for c in self.history['commands'])
            stats['most_used'] = cmd_counter.most_common(5)
        
        # Usage by time
        stats['peak_hours'] = []
        for hour in range(24):
            hour_key = f"hour_{hour}"
            if hour_key in self.history['time_patterns']:
                count = len(self.history['time_patterns'][hour_key])
                if count > 0:
                    stats['peak_hours'].append((hour, count))
        
        stats['peak_hours'] = sorted(stats['peak_hours'], key=lambda x: x[1], reverse=True)[:3]
        
        return stats
    
    def save_history(self):
        """Save history to file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            history_copy = self.history.copy()
            history_copy['time_patterns'] = dict(self.history['time_patterns'])
            
            with open(self.history_file, 'w') as f:
                json.dump(history_copy, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def save_patterns(self):
        """Save patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def format_suggestions_display(self, suggestions: Dict) -> str:
        """Format suggestions for display"""
        lines = []
        lines.append("💡 INTELLIGENT SUGGESTIONS")
        lines.append("=" * 50)
        
        if suggestions['next_likely']:
            lines.append("\n🔮 Predicted Next Commands:")
            for sug in suggestions['next_likely'][:3]:
                confidence = int(sug['confidence'] * 100)
                lines.append(f"  • {sug['key']} ({confidence}% confidence)")
                lines.append(f"    {sug['reason']}")
        
        if suggestions['frequent_now']:
            lines.append("\n⏰ Frequently Used Now:")
            for sug in suggestions['frequent_now'][:3]:
                lines.append(f"  • {sug['key']}")
                lines.append(f"    {sug['reason']}")
        
        if suggestions['trending']:
            lines.append("\n📈 Trending Commands:")
            for sug in suggestions['trending'][:3]:
                lines.append(f"  • {sug['key']}")
                lines.append(f"    {sug['reason']}")
        
        if suggestions['recently_used']:
            lines.append("\n🕐 Recently Used:")
            for sug in suggestions['recently_used'][:3]:
                lines.append(f"  • {sug['key']}: {sug['description']}")
        
        return '\n'.join(lines)

# Integration with i3-help.py
def integrate_history_tracking(helper_instance):
    """Add this to I3KeybindingHelper class"""
    helper_instance.history_tracker = CommandHistoryTracker()
    
    # Override execute_binding_command to track usage
    original_execute = helper_instance.execute_binding_command
    
    def tracked_execute(command):
        # Find the binding
        binding = next((b for b in helper_instance.bindings if b['command'] == command), None)
        if binding:
            helper_instance.history_tracker.record_command(binding)
        return original_execute(command)
    
    helper_instance.execute_binding_command = tracked_execute

if __name__ == "__main__":
    # Test the tracker
    tracker = CommandHistoryTracker()
    
    # Show current statistics
    stats = tracker.get_statistics()
    print(f"📊 Command History Statistics")
    print(f"   Total commands executed: {stats['total_commands']}")
    print(f"   Unique commands used: {stats['unique_commands']}")
    
    if stats.get('most_used'):
        print(f"\n🏆 Most Used Commands:")
        for cmd, count in stats['most_used']:
            print(f"   • {cmd}: {count} times")
    
    # Get suggestions
    suggestions = tracker.get_suggestions()
    if any(suggestions.values()):
        print("\n" + tracker.format_suggestions_display(suggestions))
