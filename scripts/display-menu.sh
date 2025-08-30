#!/bin/bash
# Interactive Display Configuration Menu for i3
# Provides GNOME-like display switching functionality

# Function to detect connected displays
get_connected_displays() {
    xrandr | grep " connected" | cut -d" " -f1
}

# Function to get current display setup
get_current_setup() {
    LAPTOP_ACTIVE=$(xrandr | grep "eDP-1 connected" | grep -v " (")
    HDMI1_ACTIVE=$(xrandr | grep "HDMI-1 connected" | grep -v " (")
    HDMI2_ACTIVE=$(xrandr | grep "HDMI-2 connected" | grep -v " (")
    
    if [[ -n "$LAPTOP_ACTIVE" && -n "$HDMI1_ACTIVE" ]]; then
        SAME_POS=$(xrandr | grep -E "(eDP-1|HDMI-1)" | grep "+0+0" | wc -l)
        if [[ $SAME_POS -eq 2 ]]; then
            echo "Currently: Mirrored Displays"
        else
            echo "Currently: Extended Desktop"
        fi
    elif [[ -n "$HDMI1_ACTIVE" && -z "$LAPTOP_ACTIVE" ]]; then
        echo "Currently: HDMI Only"
    elif [[ -n "$LAPTOP_ACTIVE" && -z "$HDMI1_ACTIVE" ]]; then
        echo "Currently: Laptop Screen Only"
    else
        echo "Currently: Unknown Configuration"
    fi
}

# Function to apply display configuration
apply_config() {
    case "$1" in
        "Laptop Screen Only")
            xrandr --output eDP-1 --auto --primary --output HDMI-1 --off --output HDMI-2 --off
            notify-send "Display" "Switched to laptop screen only" -t 2000
            ;;
        "HDMI Only")
            xrandr --output HDMI-1 --auto --primary --output eDP-1 --off --output HDMI-2 --off
            notify-send "Display" "Switched to HDMI only" -t 2000
            ;;
        "Mirror Displays")
            xrandr --output eDP-1 --mode 1920x1080 --output HDMI-1 --mode 1920x1080 --same-as eDP-1
            notify-send "Display" "Mirroring displays at 1920x1080" -t 2000
            ;;
        "Extended Desktop (HDMI Left)")
            xrandr --output HDMI-1 --auto --primary --output eDP-1 --auto --right-of HDMI-1
            notify-send "Display" "Extended desktop - HDMI left, laptop right" -t 2000
            ;;
        "Extended Desktop (HDMI Right)")
            xrandr --output eDP-1 --auto --primary --output HDMI-1 --auto --right-of eDP-1
            notify-send "Display" "Extended desktop - laptop left, HDMI right" -t 2000
            ;;
        "Auto-Detect")
            ~/.config/i3/scripts/setup-monitors.sh
            notify-send "Display" "Auto-detected display configuration" -t 2000
            ;;
    esac
    
    # Restart wallpaper after changes
    if [ -f ~/.config/i3/wallpaper.jpg ]; then
        feh --bg-scale ~/.config/i3/wallpaper.jpg 2>/dev/null || true
    else
        xsetroot -solid "#2e3440"
    fi
}

# Get connected displays
CONNECTED=$(get_connected_displays)
CONNECTED_ARRAY=($CONNECTED)
LAPTOP_CONNECTED=$(echo "$CONNECTED" | grep -c "eDP-1")
HDMI1_CONNECTED=$(echo "$CONNECTED" | grep -c "HDMI-1")
HDMI2_CONNECTED=$(echo "$CONNECTED" | grep -c "HDMI-2")

# Build menu options based on connected displays
OPTIONS=()

if [[ $LAPTOP_CONNECTED -eq 1 ]]; then
    OPTIONS+=("Laptop Screen Only")
fi

if [[ $HDMI1_CONNECTED -eq 1 ]]; then
    OPTIONS+=("HDMI Only")
fi

if [[ $LAPTOP_CONNECTED -eq 1 && $HDMI1_CONNECTED -eq 1 ]]; then
    OPTIONS+=("Mirror Displays")
    OPTIONS+=("Extended Desktop (HDMI Left)")
    OPTIONS+=("Extended Desktop (HDMI Right)")
fi

OPTIONS+=("Auto-Detect")

# Show current status
CURRENT_STATUS=$(get_current_setup)

# Create rofi menu
MENU_OPTIONS=$(printf "%s\n" "${OPTIONS[@]}")

# Show menu with rofi
CHOICE=$(echo -e "$CURRENT_STATUS\n---\n$MENU_OPTIONS" | rofi -dmenu -i -p "Display Configuration:" -theme-str 'window {width: 400px;} listview {lines: 8;}')

# Apply the chosen configuration
if [[ -n "$CHOICE" && "$CHOICE" != "$CURRENT_STATUS" && "$CHOICE" != "---" ]]; then
    apply_config "$CHOICE"
fi
