# i3 Window Manager Configuration

This configuration has been set up for dual monitor usage with the following features:

## Installation

To install this i3 configuration on a new system:

### Using SSH (recommended):
```bash
# Backup existing config if needed
mv ~/.config/i3 ~/.config/i3.bak 2>/dev/null

# Clone the repository
git clone git@github.com:BeechcraftNV/i3.git ~/.config/i3

# Make scripts executable
chmod +x ~/.config/i3/scripts/*.sh
chmod +x ~/.config/i3/switch-to-i3.sh
```

### Using HTTPS:
```bash
# Backup existing config if needed
mv ~/.config/i3 ~/.config/i3.bak 2>/dev/null

# Clone the repository
git clone https://github.com/BeechcraftNV/i3.git ~/.config/i3

# Make scripts executable
chmod +x ~/.config/i3/scripts/*.sh
chmod +x ~/.config/i3/switch-to-i3.sh
```

After installation, restart i3 with `Super+Shift+r` or log out and log back in.

## Monitor Setup
- HDMI-1: Primary monitor (left)
- HDMI-2: Secondary monitor (right)

## Workspace Assignment
- Workspace 1: Warp Terminal (HDMI-1)
- Workspace 2: Brave Browser (HDMI-2) 
- Workspaces 3,5,7,9: HDMI-1
- Workspaces 4,6,8,10: HDMI-2

## Key Bindings
- `Mod1` = Alt key (default i3 modifier)
- `Mod1+Return`: Open terminal
- `Mod1+d`: Application launcher (dmenu)
- `Mod1+Shift+q`: Close window
- `Mod1+Shift+f`: Open file manager
- `Mod1+Shift+x`: Lock screen
- `Print`: Screenshot
- `Shift+Print`: Select area screenshot
- `Mod1+1-0`: Switch to workspace 1-10
- `Mod1+Shift+1-0`: Move window to workspace 1-10

## Keybinding Documentation

This configuration includes scripts to generate comprehensive keybinding documentation:

- `scripts/generate-keybindings.sh`: Creates documentation of all keybindings in your config
- `scripts/show-keybindings.sh`: Opens the generated documentation for quick reference

Running `./scripts/generate-keybindings.sh` will create:
- `keybindings.txt`: Plain text version with categorized keybindings
- `keybindings.html`: HTML version with styled, formatted documentation

The documentation automatically categorizes bindings into:
- Window Management
- Workspace Navigation
- Application Launchers
- System Controls
- Layout Controls
- Special Functions

These files are regenerated on demand and are not tracked in version control.

## Visual Features
- Custom color scheme with focus indicators
- Window gaps and borders
- Picom compositor for visual effects
- Custom status bar with system information
- Smart borders and gaps

## Auto-started Applications
- Warp Terminal
- Brave Browser
- Picom compositor
- NetworkManager applet
- XSS lock for screen locking

## Configuration Files
- Main config: `~/.config/i3/config`
- Status bar: `~/.config/i3status/config`

## Optional Packages for Full Functionality
To install optional packages for screenshots, file manager, and wallpapers:
```bash
sudo pacman -S scrot thunar feh picom
```

## Setting a Wallpaper
Place your desired wallpaper as `~/.config/i3/wallpaper.jpg` or modify the feh command in the i3 config.

## Reloading Configuration
- `Mod1+Shift+c`: Reload i3 configuration
- `Mod1+Shift+r`: Restart i3 in place

---

## 📦 Required Applications (Full Functionality)

This configuration references several external tools that must be installed for full functionality:

| Package (Debian)         | Package (Arch)       | Purpose                                     |
|--------------------------|----------------------|---------------------------------------------|
| `i3`                     | `i3-wm`              | Tiling window manager                       |
| `i3blocks`               | `i3blocks`           | Status bar with modular blocks              |
| `feh`                    | `feh`                | Set wallpaper                               |
| `picom`                  | `picom`              | Compositor for transparency and shadows     |
| `xss-lock`               | `xss-lock`           | Lock screen on suspend                      |
| `i3lock`                 | `i3lock`             | Lock screen utility                         |
| `rofi`                   | `rofi`               | Application launcher                        |
| `dex`                    | `dex`                | Desktop autostart helper                    |
| `nm-applet`              | `network-manager-applet` | System tray network manager GUI       |
| `flameshot` or `scrot`   | `flameshot` or `scrot` | Screenshots (GUI or CLI-based)          |
| `xsetroot`               | `xorg-xsetroot`      | Set root window background color            |

> **Tip:** If you're getting an error like `status command not found (exit 127)`, it usually means `i3blocks` or another dependency is missing.

---

## 🛠️ Install All Required Apps (Debian/Ubuntu)

If you're on a Debian-based distro (e.g. LMDE or Ubuntu), install all required apps with:

```bash
sudo apt update && sudo apt install -y \
  i3 i3blocks feh picom xss-lock i3lock rofi dex \
  network-manager-gnome flameshot x11-xserver-utils
```

Or use a setup script:

```bash
#!/bin/bash
echo "Installing i3 dependencies..."
sudo apt update && sudo apt install -y \
  i3 i3blocks feh picom xss-lock i3lock rofi dex \
  network-manager-gnome flameshot x11-xserver-utils
```

Save as `setup-debian.sh` and run:

```bash
chmod +x setup-debian.sh
./setup-debian.sh
```

---

# 🚀 i3 Keybinding Help Utility

This configuration includes a powerful, interactive keybinding help system that makes discovering and using your keyboard shortcuts effortless.

![i3-help Demo](https://img.shields.io/badge/i3--help-Enhanced-blue?style=for-the-badge&logo=i3wm)

## ✨ Features

### 🔍 **Intelligent Search & Discovery**
- **Hierarchical categorization** with emojis for easy navigation
- **Enhanced fuzzy matching** with synonym expansion
- **Typo tolerance** and auto-correction
- **Intent mapping** - search "open browser" to find Firefox/Chrome bindings
- **Usage analytics** to surface your most-used shortcuts

### ⚡ **Interactive Actions**
- **Execute bindings directly** from the help interface
- **Copy commands** or key combinations to clipboard
- **Detailed binding information** with context
- **Visual key layout** showing highlighted keys on ASCII keyboard

### 🎯 **Smart Categorization**
- **🚀 Apps & Launch**: Terminals, browsers, launchers
- **🖥️ Workspaces**: Navigation, management, assignment  
- **🪟 Windows**: Focus, movement, arrangement, state control
- **📷 Screenshots**: Capture tools and utilities
- **🔊 Audio & Media**: Volume, media player controls
- **💡 System & Power**: Brightness, lock, suspend, shutdown
- **📐 Layout**: Splits, containers, resize operations
- **⚙️ i3 Control**: Configuration, session management
- **🔧 Custom**: User scripts and custom bindings

### 🎨 **Visual Enhancements**
- **ASCII keyboard layout** with highlighted keys
- **Focused key combination views** 
- **Key location hints** for learning
- **Rich rofi/dmenu integration** with custom themes

## 📦 i3-Help Installation

### Prerequisites
```bash
# Required
sudo pacman -S python3 rofi  # or dmenu

# Optional (for enhanced features)
pip install rapidfuzz  # Better fuzzy matching
sudo pacman -S xclip   # Clipboard support
```

### Setup
1. **Scripts are already in place** in `~/.config/i3/scripts/`:
   - `i3-help.py` - Main help utility
   - `keyboard_layout.py` - Visual keyboard layouts
   - `search_dictionaries.json` - Custom search terms (optional)

2. **Add keybinding to your i3 config** (if not already present):
   ```bash
   bindsym $mod+Alt+h exec python3 ~/.config/i3/scripts/i3-help.py
   ```

3. **Make scripts executable**:
   ```bash
   chmod +x ~/.config/i3/scripts/*.py
   ```

4. **Reload i3 configuration**:
   ```bash
   i3-msg reload
   ```

## 🎮 Usage

### Basic Usage
Press **`Super + Alt + H`** (or your configured key) to open the help interface.

### Navigation Examples

#### 1. **Browse by Category**
```
🚀 Apps & Launch
═══════════════════════════════════════════

  Applications
  ────────────────
  [Super+Return]     Open terminal         (Applications)
  [Super+Shift+Return] Quick terminal      (Quick Access)
  
  Launchers  
  ──────────
  [Super+d]          Application launcher   (Launchers)
```

#### 2. **Search with Keywords**
- Type "screenshot" → finds all screenshot-related bindings
- Type "volume" → finds audio controls  
- Type "browser" → finds web browser shortcuts
- Type "bright" → finds brightness controls

#### 3. **Use Synonyms & Intents**
- "capture" → finds screenshot tools
- "sound" → finds audio controls
- "web" → finds browser shortcuts
- "lock screen" → finds security bindings

### Action Menu Options

When you select a keybinding, choose from:
- **🚀 Execute Command** - Run the binding immediately
- **📋 Copy Command** - Copy full command to clipboard
- **📋 Copy Key Combination** - Copy just the key combo
- **⌨️ Show Key Layout** - Visual keyboard with highlighted keys
- **ℹ️ Show Details** - Full binding information
- **❌ Cancel** - Return to main menu

## 🔧 Advanced Features

### Custom Search Dictionaries

Create `~/.config/i3/scripts/search_dictionaries.json`:

```json
{
  "synonyms": {
    "screenshot": ["capture", "grab", "snapshot", "print"],
    "browser": ["web", "internet", "firefox", "chrome"],
    "terminal": ["term", "console", "shell"],
    "volume": ["sound", "audio", "speaker"]
  },
  "intents": {
    "open browser": ["firefox", "chrome", "brave"],
    "take screenshot": ["flameshot", "screenshot", "print"],
    "lock screen": ["i3lock", "lock"],
    "change volume": ["pactl", "volume", "audio"]
  },
  "typos": {
    "screnshoot": "screenshot",
    "broswer": "browser",
    "brightnes": "brightness"
  }
}
```

### Usage Analytics

The system automatically tracks:
- **Most used bindings** - Prioritized in search results
- **Popular search terms** - Suggested in interface
- **Usage patterns** - Stored in `usage_analytics.json`

View your analytics:
```bash
cat ~/.config/i3/scripts/usage_analytics.json
```

### Keyboard Layout Visualization

The visual keyboard layout shows:
- **Highlighted keys** for selected bindings
- **Key combination breakdowns**
- **Location hints** for learning

Example output:
```
┌────────────────────────────────────────────────────────────┐
│  F1   F2   F3   F4   F5   F6   F7   F8   F9   F10   F11   F12  │
├────────────────────────────────────────────────────────────┤
│  `   1   2   3   4   5   6   7   8   9   0   -   =         │
│ Tab   Q   W   E  [R]  T   Y   U   I   O   P   [   ]   \    │
│ Caps  A   S   D   F   G   H   J   K   L   ;   '            │
│ Shif  Z   X   C   V   B   N   M   ,   .   /                │
│  ←   ↓   ↑   →   PrtSc   Home   PgUp   PgDn   End   Ins   Del  │
└────────────────────────────────────────────────────────────┘

Key Combination Breakdown:
==============================
Primary: Super
+ Modifier: r
```

## 📋 Example Use Cases

### 1. **Learning i3 Shortcuts**
- New to i3? Browse categories to discover available shortcuts
- Use visual keyboard layout to see exactly which keys to press
- Track your usage to see which shortcuts you use most

### 2. **Quick Command Execution**
- Press `Super+Alt+H`, search "screenshot", execute immediately
- No need to remember exact key combinations
- Perfect for infrequently used shortcuts

### 3. **Customization & Scripting**
- Copy commands to modify or create new shortcuts
- View full command details for understanding
- Export configurations for sharing

### 4. **Troubleshooting**
- See exact commands bound to keys
- Verify configuration line numbers
- Check for conflicts or missing bindings

## 🐛 Troubleshooting i3-Help

### Common Issues

**1. "No launcher found" error**
```bash
# Install rofi or dmenu
sudo pacman -S rofi
# or
sudo pacman -S dmenu
```

**2. "Could not read i3 config file"**
```bash
# Check config file location
ls ~/.config/i3/config
# Ensure it's readable
chmod 644 ~/.config/i3/config
```

**3. Keyboard layout not working**
```bash
# Check if keyboard_layout.py exists
ls ~/.config/i3/scripts/keyboard_layout.py
# Test keyboard layout independently
python3 ~/.config/i3/scripts/keyboard_layout.py
```

**4. Commands not executing**
```bash
# Check notifications
# Commands execute in background - look for notification popups
# Check if commands are in PATH
which rofi
which i3-msg
```

### Debug Mode
Run with debug output:
```bash
python3 ~/.config/i3/scripts/i3-help.py 2>&1 | tee /tmp/i3-help-debug.log
```

## 📈 Analytics & Insights

The utility tracks usage patterns to improve your workflow:

- **Binding Usage Frequency** - Shows your most-used shortcuts
- **Search Term Analytics** - Common searches to optimize categories
- **Popular Bindings** - Suggests frequently accessed commands
- **Usage Trends** - Helps identify workflow patterns

Analytics are stored locally in `usage_analytics.json` and never shared.

## 🔗 i3-Help Related Files

- **Main Script**: `~/.config/i3/scripts/i3-help.py`
- **Keyboard Layout**: `~/.config/i3/scripts/keyboard_layout.py`
- **Dictionaries**: `~/.config/i3/scripts/search_dictionaries.json`
- **Analytics**: `~/.config/i3/scripts/usage_analytics.json`
- **i3 Config**: `~/.config/i3/config`

**Happy i3 productivity with intelligent keybinding help! 🎉**
