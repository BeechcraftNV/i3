#!/bin/bash

# Interactive keybinding helper using rofi
CONFIG_FILE="$HOME/.config/i3/config"

# Check if rofi is available
if ! command -v rofi &> /dev/null; then
    # Fallback to dmenu
    grep "^bindsym" "$CONFIG_FILE" | \
    sed 's/bindsym //' | \
    awk '{printf "%-25s %s\n", $1, substr($0, index($0,$2))}' | \
    dmenu -i -l 20 -p "i3 Keybindings:"
    exit 0
fi

# Create temporary file with formatted keybindings
TEMP_FILE=$(mktemp)

{
    echo "🪟 WINDOW FOCUS & MOVEMENT"
    grep "^bindsym.*focus\|^bindsym.*move.*\(left\|right\|up\|down\)" "$CONFIG_FILE" | \
    sed 's/bindsym //' | awk '{printf "  %-20s │ %s\n", $1, substr($0, index($0,$2))}' | head -20
    
    echo ""
    echo "🏢 WORKSPACES"
    grep "^bindsym.*workspace" "$CONFIG_FILE" | head -15 | \
    sed 's/bindsym //' | awk '{printf "  %-20s │ %s\n", $1, substr($0, index($0,$2))}'
    
    echo ""
    echo "🚀 APPLICATIONS"
    echo "  Super+Return         │ Terminal"
    echo "  Super+d              │ App launcher (rofi/dmenu)"
    echo "  Super+Shift+b        │ Browser"
    echo "  Super+Shift+f        │ File manager"
    echo "  Super+Shift+m        │ Bluetooth manager"
    
    echo ""
    echo "📐 LAYOUT"
    echo "  Super+f              │ Fullscreen toggle"
    echo "  Super+v              │ Split vertical"
    echo "  Super+b              │ Split horizontal"
    echo "  Super+s              │ Stacking layout"
    echo "  Super+w              │ Tabbed layout"
    echo "  Super+e              │ Toggle split layout"
    echo "  Super+Shift+Space    │ Toggle floating"
    echo "  Super+Space          │ Focus floating/tiled"
    
    echo ""
    echo "⚙️ SYSTEM"
    echo "  Super+Shift+c        │ Reload config"
    echo "  Super+Shift+r        │ Restart i3"
    echo "  Super+Shift+e        │ Exit i3"
    echo "  Super+Shift+x        │ Lock screen"
    echo "  Super+Pause          │ System menu"
    echo "  Super+r              │ Resize mode"
    
    echo ""
    echo "✨ SPECIAL"
    echo "  Super+Shift+q        │ Kill window"
    echo "  Super+minus          │ Scratchpad show"
    echo "  Super+Shift+minus    │ Move to scratchpad"
    echo "  Super+m              │ Mark window"
    echo "  Super+'              │ Go to mark"
    echo "  Super+p              │ Monitor setup"
    
} > "$TEMP_FILE"

# Show in rofi with custom theme
rofi -dmenu -i -markup-rows -p "🔧 i3 Keybindings" \
     -theme-str 'window {width: 80%; height: 70%;}' \
     -theme-str 'listview {lines: 25;}' \
     -theme-str 'element {padding: 5px;}' < "$TEMP_FILE"

# Clean up
rm "$TEMP_FILE"
