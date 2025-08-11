# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## ✈️ Essential Commands

Quick-start commands for managing this intelligent i3 window manager configuration.

### AI-Powered Help System

```bash
# Launch interactive keybinding browser with natural language search
python3 scripts/i3-help.py

# Search for specific keybindings with AI-enhanced fuzzy matching
python3 scripts/i3-help.py --search "screenshot"
python3 scripts/i3-help.py --search "resize window"
python3 scripts/i3-help.py --search "volume up"

# Natural language query interface
python3 scripts/i3-help.py --natural
# Then ask: "How do I make this window bigger?"

# Detect keybinding conflicts and problems
python3 scripts/i3-help.py --conflicts
```

### Documentation Generation

```bash
# Generate comprehensive keybinding cheat sheets (HTML + TXT)
./scripts/generate-keybindings.sh
# Creates: keybindings.txt, keybindings.html

# Display existing keybinding documentation
./scripts/show-keybindings.sh
```

### System Management

```bash
# Dynamic multi-monitor setup (auto-detects connected displays)
./scripts/setup-monitors.sh
# Configures workspace assignments and applies wallpaper

# Advanced screenshot management
./scripts/screenshot.sh full        # Full screen (active monitor)
./scripts/screenshot.sh selection   # Interactive selection with GUI
./scripts/screenshot.sh window      # Active window
./scripts/screenshot.sh gui         # Flameshot editor
./scripts/screenshot.sh clipboard   # Quick selection to clipboard

# Printer management system
./scripts/printer-manager.sh menu     # Interactive menu
./scripts/printer-manager.sh config   # Open configuration
./scripts/printer-manager.sh test     # Test page
```

### Development & Testing

```bash
# Test the i3-help system functionality
python3 scripts/test_i3_help.py

# Watch for config changes and auto-reload
./scripts/watch-config.sh

# Generate context-aware help suggestions
python3 scripts/context_aware_help.py

# Track command usage patterns
python3 scripts/command_history_tracker.py
```

### Quick Access via Keybindings

These commands are also available via keyboard shortcuts:
- `Super+Alt+h` - Launch i3-help interactive browser
- `Super+Alt+c` - Check for keybinding conflicts
- `Super+Alt+n` - Natural language help interface
- `Super+F1` - Show keybinding documentation
- `Super+p` - Run monitor setup script

## 🧠 Architecture Overview

The AI-enhanced help system that powers intelligent keybinding discovery and management.

This i3 configuration features a sophisticated, multi-layered intelligent help system that transforms keybinding discovery through AI-powered search and self-learning capabilities.

### Core System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    i3-help.py (Main Controller)                 │
├─────────────────────────────────────────────────────────────────┤
│  Config Parser  →  Binding Registry  →  Search Engine          │
│      ↓                    ↓                    ↓               │
│  Categorizer   →  Description Gen  →  Result Ranking           │
└─────────────────────────────────────────────────────────────────┘
             ↓                         ↑
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligence Layer                           │
├─────────────────────┬─────────────────┬─────────────────────────┤
│  NLP Processor      │  Learning System │  Conflict Detector      │
│  - Intent mapping   │  - Failed search │  - Duplicate detection  │
│  - Synonym expansion│  - Auto-improve  │  - Shadow analysis       │
│  - Typo correction  │  - Pattern recog │  - Ergonomic scoring     │
└─────────────────────┴─────────────────┴─────────────────────────┘
             ↓                         ↑
┌─────────────────────────────────────────────────────────────────┐
│                    Export & Interface Layer                     │
├─────────────────────┬─────────────────┬─────────────────────────┤
│  Export Engine      │  Keyboard Layout │  Analytics Tracker      │
│  - HTML/PDF/MD      │  - Visual display│  - Usage patterns       │
│  - Professional docs│  - Key highlight │  - Learning metrics     │
└─────────────────────┴─────────────────┴─────────────────────────┘
```

### Module Breakdown

#### Core Components
- **`i3-help.py`** - Main orchestrator with UI, search, and action handling
- **`conflict_detector.py`** - Identifies keybinding conflicts, duplicates, and ergonomic issues
- **`search_learning_system.py`** - Self-improving AI that learns from failed searches
- **`natural_language_search.py`** - Processes queries like "how do I resize a window?"
- **`export_engine.py`** - Generates professional documentation in multiple formats
- **`keyboard_layout.py`** - Visual keyboard layout rendering with key highlighting

#### Data Sources
- **`search_dictionaries.json`** - Curated synonyms, intents, and typo corrections
- **`usage_analytics.json`** - Tracks which keybindings are used most frequently
- **`learning_data.json`** - Auto-generated learning insights and failed search patterns
- **`conflict_report.json/txt`** - Generated reports of keybinding issues

### Intelligence Features

#### Multi-Layer Search Engine
1. **Exact matching** - Direct key combination lookups
2. **Fuzzy matching** - Handles typos and partial matches (using rapidfuzz)
3. **Synonym expansion** - Maps "screenshot" → "capture", "grab", "snapshot"
4. **Intent mapping** - "open browser" → finds Firefox, Brave, Chrome bindings
5. **Popularity ranking** - Most-used bindings appear first in results

#### Self-Learning AI System
- **Failed Search Detection** - Automatically tracks searches that return no results
- **Pattern Analysis** - Uses difflib similarity matching to identify improvement opportunities
- **Auto-Enhancement** - High-confidence improvements (>80%) automatically update dictionaries
- **Evidence-Based Learning** - Requires multiple observations before making changes
- **Smart Cleanup** - Maintains size limits and removes outdated data

#### Conflict Detection
- **Duplicate bindings** - Same key mapped multiple times
- **Shadow detection** - Shorter bindings that prevent longer ones from working
- **Mode conflicts** - Issues between normal and mode-specific bindings
- **Ergonomic analysis** - Identifies hard-to-press key combinations
- **System conflicts** - Detects conflicts with standard desktop shortcuts

### Data Flow

1. **Config Parsing** - Extract all `bindsym` entries from i3 config
2. **Description Generation** - Create human-readable descriptions using pattern recognition
3. **Term Expansion** - Add synonyms, intents, and normalized forms to search terms
4. **Categorization** - Sort into hierarchical categories (Apps, Workspaces, Windows, etc.)
5. **Search Processing** - Handle user queries through multiple intelligence layers
6. **Result Ranking** - Prioritize based on popularity, relevance, and user patterns
7. **Action Execution** - Execute commands, copy to clipboard, or show details
8. **Learning Integration** - Track failed searches and continuously improve accuracy

## 🔗 Integration Points

How this configuration integrates with chezmoi, multi-monitor setups, and external dependencies.

### chezmoi Dotfile Management

This i3 configuration is designed to work seamlessly with chezmoi dotfile management:

```bash
# Add changes to chezmoi tracking
chezmoi add ~/.config/i3/config
chezmoi add ~/.config/i3/scripts/
chezmoi add ~/.config/i3/WARP.md

# Apply changes across machines
chezmoi apply

# View differences before applying
chezmoi diff

# Source location for templates/modifications
# ~/.local/share/chezmoi/dot_config/i3/
```

**Key Integration Features:**
- All scripts automatically gain execute permissions via chezmoi
- Configuration templates can be customized per machine
- Learning data (`learning_data.json`, `usage_analytics.json`) is machine-specific and not tracked
- Search dictionaries are synchronized across machines for consistent help experience

### Multi-Monitor Support

Intelligent workspace assignment based on available displays:

```bash
# Universal workspace layout (from config)
# Odd workspaces (1,3,5,7,9)  → Primary monitor  
# Even workspaces (2,4,6,8,10) → Secondary monitor

# Example assignments:
workspace "1:Terminal" output HDMI-1 eDP-1 DP-1 VGA-1    # Primary
workspace "2:Browser"  output HDMI-2 HDMI-1 eDP-1        # Secondary
workspace "3:Code"     output HDMI-1 eDP-1 DP-1 VGA-1    # Primary
```

**Dynamic Detection Logic:**
- `setup-monitors.sh` automatically detects connected displays
- Smart arrangement: laptop displays below external monitors
- Fallback to single monitor if only one display available
- Wallpaper and compositor restart automatically after changes

### Warp Terminal Integration

Optimized for Warp terminal environment:

```bash
# Primary terminal launchers (with fallbacks)
bindsym $mod+Return exec warp-terminal-preview || i3-sensible-terminal
bindsym $mod+Shift+Return exec --no-startup-id i3-msg 'exec warp-terminal-preview || i3-sensible-terminal; [class=".*"] move scratchpad'

# Auto-startup with workspace assignment
exec --no-startup-id sh -c "sleep 2 && i3-msg 'workspace \"1:Terminal\"; exec warp-terminal || i3-sensible-terminal'"
```

### Oh-My-Zsh Environment

The Python help scripts are shell-agnostic but optimized for zsh users:
- All shell commands use absolute paths to avoid PATH issues
- Scripts handle both `bash` and `zsh` environments
- Warp-specific features (like command completions) are preserved

### External Dependencies

The system gracefully handles optional dependencies with fallback mechanisms:

#### Required Dependencies
```bash
# Core i3 functionality
sudo pacman -S i3-wm i3blocks rofi picom feh xss-lock
# OR Ubuntu/Debian:
sudo apt install i3 i3blocks rofi picom feh xss-lock
```

#### Optional Python Dependencies
```bash
# Enhanced fuzzy matching
pip install rapidfuzz

# Professional PDF exports
pip install weasyprint

# Advanced NLP processing (optional)
pip install spacy
```

#### Fallback Detection Logic
The Python modules detect missing dependencies:

```python
# Example from i3-help.py
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    # Falls back to built-in difflib

try:
    from export_engine import ExportEngine
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    # Export features disabled gracefully
```

### Application Assignment System

Intelligent workspace assignment with multiple fallbacks:

```bash
# Browser assignment (handles multiple browsers)
assign [class="Brave-browser"] $ws2
assign [class="brave-browser"] $ws2  # Different naming schemes
assign [class="Brave"] $ws2
assign [class="Firefox"] $ws2
assign [class="Chromium"] $ws2

# Terminal assignment (multiple terminal emulators)
assign [class="Warp"] $ws1
assign [class="warp-terminal"] $ws1
assign [class="Alacritty"] $ws1
assign [class="Kitty"] $ws1
```

### Service Integration

**Pi-hole Support** (as noted in user rules):
The configuration includes Pi-hole service awareness for network management.

**System Services Integration:**
```bash
# Automatic service startup (from config)
exec --no-startup-id nm-applet           # NetworkManager
exec --no-startup-id blueman-applet      # Bluetooth
exec --no-startup-id dunst               # Notifications
exec --no-startup-id flameshot           # Screenshots
```

### Python Module Dependencies

**Core i3-help.py ecosystem:**
- `conflict_detector.py` - No external deps, uses stdlib only
- `search_learning_system.py` - Uses `difflib` from stdlib
- `natural_language_search.py` - Optional spaCy integration
- `export_engine.py` - Optional weasyprint for PDF export
- `keyboard_layout.py` - Pure Python, no deps

**Graceful degradation:** All features work without optional dependencies, but enhanced functionality is available when installed.

## 🔄 Maintenance & Extension Workflows

Cookbook-style guides for extending and maintaining the configuration.

### Adding New Keybindings

**Step-by-step process to add a keybinding and make it discoverable:**

1. **Add to i3 config:**
   ```bash
   # Edit the main config file
   vim ~/.config/i3/config
   
   # Add your keybinding (example)
   bindsym $mod+Shift+p exec --no-startup-id pavucontrol
   ```

2. **Test the keybinding:**
   ```bash
   # Reload i3 config
   i3-msg reload
   
   # Test the new keybinding works
   # Press Super+Shift+p to verify
   ```

3. **Update documentation:**
   ```bash
   # Regenerate keybinding documentation
   ./scripts/generate-keybindings.sh
   
   # This updates keybindings.txt and keybindings.html
   ```

4. **Test AI discovery:**
   ```bash
   # Test the new keybinding is searchable
   python3 scripts/i3-help.py --search "pavucontrol"
   python3 scripts/i3-help.py --search "volume control"
   
   # Should automatically categorize under "Audio & Media"
   ```

5. **Sync with chezmoi:**
   ```bash
   chezmoi add ~/.config/i3/config
   chezmoi add ~/.config/i3/keybindings.txt
   chezmoi add ~/.config/i3/keybindings.html
   ```

### Teaching the AI New Concepts

**Method 1: Manual dictionary editing (immediate effect)**

```bash
# Edit the search dictionaries
vim scripts/search_dictionaries.json

# Example addition:
{
  "synonyms": {
    "volume_control": ["audio mixer", "sound settings", "pavucontrol"],
    "screenshot": ["capture", "snap", "print", "grab"]
  },
  "intents": {
    "control audio": ["pavucontrol", "volume", "mixer", "sound"]
  },
  "typos": {
    "volme": "volume",
    "pavucontorl": "pavucontrol"
  }
}

# Test immediately
python3 scripts/i3-help.py --search "audio mixer"
```

**Method 2: AI-powered learning (automatic improvement)**

```bash
# The system learns from failed searches automatically
# Try searching for something that fails:
python3 scripts/i3-help.py --search "sound mixer"

# If no results, the AI will:
# 1. Record the failed search
# 2. Analyze similarity to existing terms
# 3. Suggest improvements in learning_data.json
# 4. Auto-apply high-confidence improvements (>80%)

# Check learning progress:
cat scripts/learning_data.json | jq '.insights[] | select(.confidence_score > 0.8)'
```

### Resolving Binding Conflicts

**Detect and resolve keybinding conflicts:**

1. **Run conflict detection:**
   ```bash
   python3 scripts/i3-help.py --conflicts
   
   # Generates detailed reports:
   # - conflict_report.txt (human-readable)
   # - conflict_report.json (machine-readable)
   ```

2. **Review conflict report:**
   ```bash
   cat scripts/conflict_report.txt
   
   # Example output:
   # DUPLICATE BINDINGS:
   # - $mod+p: Bound 2 times (lines 199, 305)
   #   Line 199: exec --no-startup-id ~/.config/i3/scripts/setup-monitors.sh
   #   Line 305: exec --no-startup-id ~/.config/i3/scripts/printer-manager.sh
   ```

3. **Resolve conflicts:**
   ```bash
   # Edit config to fix duplicates
   vim ~/.config/i3/config
   
   # Example fix: Change one binding
   # OLD: bindsym $mod+p exec printer-manager
   # NEW: bindsym $mod+Ctrl+p exec printer-manager
   ```

4. **Verify resolution:**
   ```bash
   python3 scripts/i3-help.py --conflicts
   # Should show "No conflicts detected" or fewer issues
   ```

### Monitor Layout Management

**Safely update monitor configurations:**

1. **Test monitor setup:**
   ```bash
   # Run monitor setup script manually
   ./scripts/setup-monitors.sh
   
   # Check the log for issues
   cat ~/.cache/monitor-setup.log
   ```

2. **Modify workspace assignments:**
   ```bash
   vim ~/.config/i3/config
   
   # Update workspace output assignments
   # Example for triple monitor setup:
   workspace "1:Terminal" output DP-1 HDMI-1 eDP-1
   workspace "2:Browser"  output HDMI-2 DP-1 HDMI-1
   workspace "3:Code"     output DP-2 DP-1 HDMI-1
   ```

3. **Test workspace distribution:**
   ```bash
   # Reload i3
   i3-msg reload
   
   # Test workspace switching
   i3-msg workspace "1:Terminal"
   i3-msg workspace "2:Browser"
   
   # Verify correct monitor assignment
   ```

4. **Update autostart applications:**
   ```bash
   # Modify app assignments in config if needed
   vim ~/.config/i3/config
   
   # Example: Change browser workspace
   # exec --no-startup-id sh -c "sleep 2 && i3-msg 'workspace \"2:Browser\"; exec brave'"
   ```

### Syncing with chezmoi

**Complete workflow for managing changes across machines:**

1. **Add new/modified files:**
   ```bash
   # Add all i3 configuration changes
   chezmoi add ~/.config/i3/config
   chezmoi add ~/.config/i3/scripts/
   chezmoi add ~/.config/i3/WARP.md
   
   # Note: Learning data is NOT synced (machine-specific)
   # Files like learning_data.json, usage_analytics.json stay local
   ```

2. **Review changes before committing:**
   ```bash
   # See what will be synced
   chezmoi diff
   
   # Check status
   chezmoi status
   ```

3. **Commit and push:**
   ```bash
   # Navigate to chezmoi source
   chezmoi cd
   
   # Commit changes
   git add .
   git commit -m "i3: Add new keybindings and improve help system"
   
   # Push to repository
   git push origin main
   ```

4. **Apply on other machines:**
   ```bash
   # On target machine, pull latest changes
   chezmoi update
   
   # Or more carefully:
   chezmoi diff
   chezmoi apply
   ```

### Custom Script Development

**Guidelines for adding new scripts to the ecosystem:**

1. **Script template:**
   ```bash
   #!/bin/bash
   # Description: Your script purpose
   # Usage: script.sh [options]
   
   set -euo pipefail  # Exit on error, undefined vars, pipe failures
   
   # Your script logic here
   ```

2. **Integration with i3-help:**
   ```python
   # To make your script discoverable, add appropriate entries to:
   # scripts/search_dictionaries.json
   {
     "intents": {
       "your_script_purpose": ["script-name", "related", "terms"]
     }
   }
   ```

3. **Add keybinding:**
   ```bash
   # In ~/.config/i3/config
   bindsym $mod+Alt+x exec --no-startup-id ~/.config/i3/scripts/your-script.sh
   ```

4. **Testing workflow:**
   ```bash
   # Test script directly
   ./scripts/your-script.sh
   
   # Test discoverability
   python3 scripts/i3-help.py --search "your script purpose"
   
   # Test keybinding
   i3-msg reload  # Then test keybinding
   ```

### Troubleshooting Common Issues

**Python module import errors:**
```bash
# Install missing dependencies
pip install rapidfuzz weasyprint

# Test modules individually
python3 -c "from scripts.conflict_detector import KeybindingConflictDetector"
python3 -c "from scripts.search_learning_system import SearchLearningSystem"
```

**AI learning system issues:**
```bash
# Reset learning data if corrupted
rm scripts/learning_data.json
rm scripts/usage_analytics.json

# The system will rebuild these automatically
python3 scripts/i3-help.py --search "test"
```

**Monitor setup failures:**
```bash
# Check monitor setup logs
cat ~/.cache/monitor-setup.log

# Test xrandr directly
xrandr --query

# Reset to single monitor
xrandr --auto
```

---

## Appendix

Additional reference materials and diagrams.

