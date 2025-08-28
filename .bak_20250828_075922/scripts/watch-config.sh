#!/bin/bash

# Watch i3 config file and auto-regenerate keybinding reference
CONFIG_FILE="$HOME/.config/i3/config"
SCRIPT_DIR="$HOME/.config/i3/scripts"

if command -v inotifywait &> /dev/null; then
    echo "👀 Watching i3 config for changes..."
    while inotifywait -e modify "$CONFIG_FILE" 2>/dev/null; do
        echo "🔄 Config changed, regenerating keybinding reference..."
        "$SCRIPT_DIR/generate-keybindings.sh"
        sleep 2
    done
else
    echo "⚠️  inotify-tools not installed. Install with: sudo pacman -S inotify-tools"
    echo "   For now, manually run generate-keybindings.sh after config changes"
fi
