# i3 Window Manager Configuration

This configuration has been set up for dual monitor usage with the following features:

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

