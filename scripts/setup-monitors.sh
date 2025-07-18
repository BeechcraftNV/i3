#!/bin/bash
# Dynamic monitor setup script for i3
# Automatically detects and configures available displays

# Get list of connected displays
CONNECTED=$(xrandr | grep " connected" | cut -d" " -f1)
CONNECTED_COUNT=$(echo "$CONNECTED" | wc -l)

# Find the primary display (laptop screen or first connected)
PRIMARY=$(echo "$CONNECTED" | head -1)

echo "Found $CONNECTED_COUNT connected display(s): $CONNECTED"

if [ "$CONNECTED_COUNT" -eq 1 ]; then
    # Single display setup
    echo "Setting up single display: $PRIMARY"
    xrandr --output "$PRIMARY" --primary --auto
    
    # Turn off other displays that might be cached
    for output in $(xrandr | grep " disconnected" | cut -d" " -f1); do
        xrandr --output "$output" --off 2>/dev/null || true
    done
    
elif [ "$CONNECTED_COUNT" -eq 2 ]; then
    # Dual display setup
    DISPLAYS=($CONNECTED)
    PRIMARY_DISPLAY="${DISPLAYS[0]}"
    SECONDARY_DISPLAY="${DISPLAYS[1]}"
    
    echo "Setting up dual displays: $PRIMARY_DISPLAY (primary) + $SECONDARY_DISPLAY (secondary)"
    
    # Detect if we have a laptop (eDP) + external monitor setup
    if [[ "$PRIMARY_DISPLAY" =~ ^eDP ]]; then
        # Laptop + external monitor: external becomes primary, laptop secondary
        xrandr --output "$SECONDARY_DISPLAY" --primary --auto --output "$PRIMARY_DISPLAY" --auto --below "$SECONDARY_DISPLAY"
    else
        # Two external monitors: arrange side by side
        xrandr --output "$PRIMARY_DISPLAY" --primary --auto --output "$SECONDARY_DISPLAY" --auto --right-of "$PRIMARY_DISPLAY"
    fi
    
else
    # Multiple displays (3+) - basic setup
    echo "Setting up multiple displays"
    FIRST=true
    PREVIOUS=""
    
    for display in $CONNECTED; do
        if [ "$FIRST" = true ]; then
            xrandr --output "$display" --primary --auto
            FIRST=false
        else
            xrandr --output "$display" --auto --right-of "$PREVIOUS"
        fi
        PREVIOUS="$display"
    done
fi

# Give displays time to initialize
sleep 1

# Restart wallpaper and compositor after monitor changes
if [ -f ~/.config/i3/wallpaper.jpg ]; then
    feh --bg-scale ~/.config/i3/wallpaper.jpg 2>/dev/null || true
else
    xsetroot -solid "#2e3440"
fi

# Restart picom if it was running
if pgrep picom >/dev/null; then
    killall picom 2>/dev/null || true
    sleep 0.5
    picom -b 2>/dev/null || true
fi

echo "Monitor setup complete"

