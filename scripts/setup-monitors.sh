#!/bin/bash
# Dynamic monitor setup script for i3
# Automatically detects and configures available displays

set -euo pipefail

# Configuration
WALLPAPER_PATH="${HOME}/.config/i3/wallpaper.jpg"
FALLBACK_BG_COLOR="#2e3440"
LOG_FILE="${HOME}/.cache/monitor-setup.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create cache directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting monitor setup..."

# Get list of connected displays
CONNECTED=$(xrandr | grep " connected" | cut -d" " -f1)
CONNECTED_COUNT=$(echo "$CONNECTED" | wc -l)

# Validate we have at least one display
if [ "$CONNECTED_COUNT" -eq 0 ]; then
    log "ERROR: No connected displays found!"
    exit 1
fi

log "Found $CONNECTED_COUNT connected display(s): $(echo "$CONNECTED" | tr '\n' ' ')"

# Function to turn off disconnected displays
cleanup_disconnected() {
    log "Cleaning up disconnected displays..."
    for output in $(xrandr | grep " disconnected" | cut -d" " -f1); do
        if xrandr --output "$output" --off 2>/dev/null; then
            log "Turned off disconnected display: $output"
        fi
    done
}

# Function to get display resolution and refresh rate
get_display_info() {
    local display="$1"
    xrandr | grep -A1 "^$display connected" | tail -1 | awk '{print $1, $2}' | tr -d '+'
}

# Function to restart wallpaper
setup_wallpaper() {
    log "Setting up wallpaper..."
    if [ -f "$WALLPAPER_PATH" ]; then
        if feh --bg-scale "$WALLPAPER_PATH" 2>/dev/null; then
            log "Wallpaper applied successfully"
        else
            log "Failed to apply wallpaper, using solid color"
            xsetroot -solid "$FALLBACK_BG_COLOR"
        fi
    else
        log "Wallpaper not found, using solid color background"
        xsetroot -solid "$FALLBACK_BG_COLOR"
    fi
}

# Function to restart compositor
restart_compositor() {
    log "Managing compositor..."
    if pgrep picom >/dev/null; then
        log "Restarting picom..."
        killall picom 2>/dev/null || true
        sleep 0.5
        if picom -b 2>/dev/null; then
            log "Picom restarted successfully"
        else
            log "Failed to restart picom"
        fi
    else
        log "Picom not running, attempting to start..."
        picom -b 2>/dev/null && log "Picom started" || log "Failed to start picom"
    fi
}

# Main display configuration logic
case "$CONNECTED_COUNT" in
    1)
        # Single display setup
        PRIMARY=$(echo "$CONNECTED" | head -1)
        log "Setting up single display: $PRIMARY"
        
        if xrandr --output "$PRIMARY" --primary --auto; then
            log "Successfully configured single display: $PRIMARY"
            log "Display info: $(get_display_info "$PRIMARY")"
        else
            log "ERROR: Failed to configure display: $PRIMARY"
            exit 1
        fi
        
        cleanup_disconnected
        ;;
        
    2)
        # Dual display setup
        DISPLAYS=($CONNECTED)
        DISPLAY1="${DISPLAYS[0]}"
        DISPLAY2="${DISPLAYS[1]}"
        
        log "Setting up dual displays: $DISPLAY1 + $DISPLAY2"
        
        # Smart arrangement based on display types
        if [[ "$DISPLAY1" =~ ^eDP ]] || [[ "$DISPLAY1" =~ ^LVDS ]]; then
            # Laptop display + external monitor
            log "Detected laptop + external monitor setup"
            if xrandr --output "$DISPLAY2" --primary --auto --output "$DISPLAY1" --auto --below "$DISPLAY2"; then
                log "Configured: $DISPLAY2 (primary, top) + $DISPLAY1 (laptop, bottom)"
            else
                log "ERROR: Failed to configure dual display setup"
                exit 1
            fi
        elif [[ "$DISPLAY2" =~ ^eDP ]] || [[ "$DISPLAY2" =~ ^LVDS ]]; then
            # External monitor + laptop display
            log "Detected external monitor + laptop setup"
            if xrandr --output "$DISPLAY1" --primary --auto --output "$DISPLAY2" --auto --below "$DISPLAY1"; then
                log "Configured: $DISPLAY1 (primary, top) + $DISPLAY2 (laptop, bottom)"
            else
                log "ERROR: Failed to configure dual display setup"
                exit 1
            fi
        else
            # Two external monitors
            log "Detected two external monitors"
            if xrandr --output "$DISPLAY1" --primary --auto --output "$DISPLAY2" --auto --right-of "$DISPLAY1"; then
                log "Configured: $DISPLAY1 (primary, left) + $DISPLAY2 (right)"
            else
                log "ERROR: Failed to configure dual display setup"
                exit 1
            fi
        fi
        
        log "Display 1 info: $(get_display_info "$DISPLAY1")"
        log "Display 2 info: $(get_display_info "$DISPLAY2")"
        ;;
        
    *)
        # Multiple displays (3+)
        log "Setting up $CONNECTED_COUNT displays"
        
        FIRST=true
        PREVIOUS=""
        
        for display in $CONNECTED; do
            if [ "$FIRST" = true ]; then
                if xrandr --output "$display" --primary --auto; then
                    log "Set primary display: $display"
                    FIRST=false
                else
                    log "ERROR: Failed to set primary display: $display"
                    exit 1
                fi
            else
                if xrandr --output "$display" --auto --right-of "$PREVIOUS"; then
                    log "Added display: $display (right of $PREVIOUS)"
                else
                    log "ERROR: Failed to add display: $display"
                    exit 1
                fi
            fi
            PREVIOUS="$display"
        done
        ;;
esac

# Give displays time to initialize
log "Waiting for displays to initialize..."
sleep 2

# Apply wallpaper and restart compositor
setup_wallpaper
restart_compositor

# Notify i3 to refresh (if available)
if command -v i3-msg >/dev/null 2>&1; then
    i3-msg reload 2>/dev/null && log "i3 configuration reloaded" || log "Failed to reload i3"
fi

log "Monitor setup complete!"

# Optional: Save current configuration for debugging
xrandr --query > "${HOME}/.cache/xrandr-current.txt" 2>/dev/null || true