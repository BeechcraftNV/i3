# Printer Setup Guide for Manjaro i3

## Current Status ✅
Your printer setup is **COMPLETE** and ready to use!

### What's Configured:
- **Brother DCP-L2550DW** printer installed and configured
- **CUPS** printing service running
- **Avahi** daemon for network printer discovery
- **i3 key bindings** for printer management
- **Status bar widget** showing printer status
- **GUI and CLI** printer management tools

## Key Bindings

| Shortcut | Action |
|----------|--------|
| `$mod+Ctrl+p` | Open printer management menu (rofi) |
| `$mod+Shift+Ctrl+p` | Open printer configuration GUI |
| `$mod+Alt+p` | Print test page quickly |

## Printer Management Script Usage

The script `/home/steven/.config/i3/scripts/printer-manager.sh` provides:

```bash
# Show interactive menu
~/.config/i3/scripts/printer-manager.sh menu

# Quick commands
~/.config/i3/scripts/printer-manager.sh test      # Print test page
~/.config/i3/scripts/printer-manager.sh status   # Show status
~/.config/i3/scripts/printer-manager.sh queue    # Show print queue
~/.config/i3/scripts/printer-manager.sh clear    # Clear print queue
~/.config/i3/scripts/printer-manager.sh web      # Open CUPS web interface
~/.config/i3/scripts/printer-manager.sh config   # Open printer settings
~/.config/i3/scripts/printer-manager.sh add      # Add new printer
```

## Status Bar Integration

The status bar shows printer status:
- 🖨️ **READY** (Green) - Printer ready
- 🖨️ **PRINTING** (Blue) - Currently printing
- 🖨️ **QUEUE(n)** (Orange) - Jobs waiting in queue
- 🖨️ **OFFLINE** (Red) - Printer unavailable

## Useful Commands

```bash
# Print any file
lp -d DCP-L2550DW filename.pdf

# Check printer status
lpstat -p DCP-L2550DW

# View print queue
lpq -P DCP-L2550DW

# Cancel all print jobs
cancel -a DCP-L2550DW

# Open CUPS web interface
xdg-open http://localhost:631
```

## Adding New Printers

1. **GUI Method**: Press `$mod+Shift+Ctrl+p` to open system-config-printer
2. **Command Line**: `~/.config/i3/scripts/printer-manager.sh add`
3. **Web Interface**: Go to http://localhost:631 and click "Add Printer"

## Network Printer Discovery

**Avahi** is configured for automatic network printer discovery:
- Printers on the same network will be automatically discovered
- mDNS (multicast DNS) allows finding printers by name
- UFW firewall allows mDNS traffic (UDP port 5353)

## Troubleshooting

### Printer Not Found
```bash
# Restart CUPS service
sudo systemctl restart cups

# Restart Avahi for network discovery
sudo systemctl restart avahi-daemon

# Check if printer is powered on and connected to network
```

### Print Jobs Stuck
```bash
# Clear all jobs
cancel -a DCP-L2550DW

# Restart printer and try again
```

### Configuration Files
- **CUPS config**: `/etc/cups/`
- **Printer drivers**: `/usr/share/cups/`
- **i3 printer scripts**: `~/.config/i3/scripts/printer-*.sh`

## Integration Notes

This setup integrates seamlessly with your existing i3 configuration:
- **Rofi menus** match your existing style
- **Notifications** use dunst (already configured)
- **Status bar** uses your existing i3blocks theme
- **Floating windows** for printer dialogs are pre-configured
- **Workspace assignments** keep printer dialogs organized
