#!/bin/bash

# Comprehensive Screenshot Management Script
# Usage: screenshot.sh [full|selection|window|gui|clipboard]

SCREENSHOT_DIR="$HOME/Pictures/screenshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$SCREENSHOT_DIR"/{full,selection,window}

case "$1" in
    "full")
        # Full screen screenshot - active monitor only
        OUTPUT=$(i3-msg -t get_workspaces | jq -r '.[] | select(.focused==true).output')
        GEOMETRY=$(xrandr | grep "\"$OUTPUT connected\"" | grep -o '[0-9]*x[0-9]*+[0-9]*+[0-9]*')
        
        if [ -n "$GEOMETRY" ]; then
            flameshot screen -n 0 -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
            notify-send "Screenshot" "Full screen saved to $SCREENSHOT_DIR/full/"
        else
            # Fallback to all screens
            flameshot full -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
            notify-send "Screenshot" "Full screen saved to $SCREENSHOT_DIR/full/"
        fi
        ;;
    
    "selection")
        # Interactive selection
        flameshot gui -p "$SCREENSHOT_DIR/selection/selection_$TIMESTAMP.png"
        ;;
    
    "window")
        # Active window screenshot - saves to disk AND copies to clipboard
        # Check if we have xdotool and try to get active window
        if command -v xdotool >/dev/null 2>&1; then
            WINDOW_ID=$(xdotool getactivewindow 2>/dev/null)
            if [ -n "$WINDOW_ID" ]; then
                # Use maim to capture the specific window (more reliable than Flameshot for this)
                if command -v maim >/dev/null 2>&1; then
                    FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
                    # Save to disk
                    maim --window="$WINDOW_ID" "$FILEPATH"
                    # Copy to clipboard
                    cat "$FILEPATH" | xclip -selection clipboard -t image/png
                    notify-send "Screenshot" "Window captured → saved to disk and copied to clipboard"
                else
                    # Fallback to Flameshot GUI if maim not available
                    notify-send "Screenshot" "Select the active window (will save to disk and clipboard)"
                    FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
                    flameshot gui --path="$FILEPATH" --clipboard
                fi
            else
                notify-send "Screenshot" "No active window found, please select manually"
                FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
                flameshot gui --path="$FILEPATH" --clipboard
            fi
        else
            # No xdotool, fallback to manual selection  
            notify-send "Screenshot" "Select the window to capture (will save to disk and clipboard)"
            FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
            flameshot gui --path="$FILEPATH" --clipboard
        fi
        ;;
    
    "gui")
        # Flameshot GUI mode (interactive with editing)
        flameshot gui
        ;;
    
    "clipboard")
        # Quick selection to clipboard only
        flameshot gui --clipboard
        ;;
    
    "config")
        # Open Flameshot configuration
        flameshot config
        ;;
    
    *)
        echo "Usage: $0 [full|selection|window|gui|clipboard|config]"
        echo "  full      - Full screen (active monitor)"
        echo "  selection - Interactive selection with GUI"
        echo "  window    - Active window"
        echo "  gui       - Flameshot GUI with editing tools"
        echo "  clipboard - Quick selection to clipboard only"
        echo "  config    - Open Flameshot configuration"
        exit 1
        ;;
esac
