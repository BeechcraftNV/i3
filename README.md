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