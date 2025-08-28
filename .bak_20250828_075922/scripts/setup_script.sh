#!/bin/bash

# i3 Keybinding Reference Tools
# Strategy 2 & 3 Implementation

echo "Setting up i3 keybinding reference tools..."

# Create scripts directory
mkdir -p ~/.config/i3/scripts

# ============================================================================
# STRATEGY 2: Documented Keybinding Reference
# ============================================================================

cat > ~/.config/i3/scripts/generate-keybindings.sh << 'EOF'
#!/bin/bash

# Generate a comprehensive keybinding reference from i3 config
CONFIG_FILE="$HOME/.config/i3/config"
OUTPUT_FILE="$HOME/.config/i3/keybindings.txt"
HTML_FILE="$HOME/.config/i3/keybindings.html"

echo "🔍 Extracting keybindings from i3 config..."

# Extract and format keybindings
{
    echo "==================== i3 KEYBINDING REFERENCE ===================="
    echo "Generated: $(date)"
    echo "=================================================================="
    echo ""
    
    # Window Management
    echo "🪟 WINDOW MANAGEMENT:"
    grep "^bindsym.*focus\|^bindsym.*move.*left\|^bindsym.*move.*right\|^bindsym.*move.*up\|^bindsym.*move.*down" "$CONFIG_FILE" | \
    sed 's/bindsym //' | sed 's/exec --no-startup-id //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # Workspace Navigation
    echo "🏢 WORKSPACE NAVIGATION:"
    grep "^bindsym.*workspace" "$CONFIG_FILE" | \
    sed 's/bindsym //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # Application Launchers
    echo "🚀 APPLICATION LAUNCHERS:"
    grep "^bindsym.*exec.*\(warp\|brave\|firefox\|thunar\|rofi\|dmenu\)" "$CONFIG_FILE" | \
    sed 's/bindsym //' | sed 's/exec --no-startup-id //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # System Controls
    echo "⚙️  SYSTEM CONTROLS:"
    grep "^bindsym.*\(volume\|brightness\|lock\|suspend\|reboot\|poweroff\|reload\|restart\)" "$CONFIG_FILE" | \
    sed 's/bindsym //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # Layout Controls
    echo "📐 LAYOUT CONTROLS:"
    grep "^bindsym.*\(split\|layout\|floating\|fullscreen\)" "$CONFIG_FILE" | \
    sed 's/bindsym //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # Special Functions
    echo "✨ SPECIAL FUNCTIONS:"
    grep "^bindsym.*\(scratchpad\|mark\|mode\)" "$CONFIG_FILE" | \
    sed 's/bindsym //' | \
    awk '{printf "  %-20s → %s\n", $1, substr($0, index($0,$2))}'
    echo ""
    
    # Quick Reference Card
    echo "📋 QUICK REFERENCE CARD:"
    echo "  Super+Return        → Terminal"
    echo "  Super+d             → App launcher"
    echo "  Super+Shift+q       → Kill window"
    echo "  Super+1-0           → Switch workspace"
    echo "  Super+Shift+1-0     → Move to workspace"
    echo "  Super+h/j/k/l       → Focus window"
    echo "  Super+Shift+h/j/k/l → Move window"
    echo "  Super+f             → Fullscreen"
    echo "  Super+v             → Split vertical"
    echo "  Super+b             → Split horizontal"
    echo "  Super+Shift+Space   → Toggle floating"
    echo "  Super+r             → Resize mode"
    echo "  Super+Shift+c       → Reload config"
    echo "  Super+Shift+r       → Restart i3"
    echo ""
    
} > "$OUTPUT_FILE"

# Generate HTML version for better viewing
{
    echo "<html><head><title>i3 Keybindings</title>"
    echo "<style>body{font-family:monospace;background:#2f343f;color:#f3f4f5;padding:20px;}"
    echo "h2{color:#4c7899;} .key{color:#50fa7b;font-weight:bold;}</style></head><body>"
    echo "<h1>🔧 i3 Keybinding Reference</h1>"
    echo "<p>Generated: $(date)</p>"
    
    # Convert sections to HTML
    sed 's/🪟 WINDOW MANAGEMENT:/<h2>🪟 Window Management<\/h2><pre>/g' "$OUTPUT_FILE" | \
    sed 's/🏢 WORKSPACE NAVIGATION:/<\/pre><h2>🏢 Workspace Navigation<\/h2><pre>/g' | \
    sed 's/🚀 APPLICATION LAUNCHERS:/<\/pre><h2>🚀 Application Launchers<\/h2><pre>/g' | \
    sed 's/⚙️  SYSTEM CONTROLS:/<\/pre><h2>⚙️ System Controls<\/h2><pre>/g' | \
    sed 's/📐 LAYOUT CONTROLS:/<\/pre><h2>📐 Layout Controls<\/h2><pre>/g' | \
    sed 's/✨ SPECIAL FUNCTIONS:/<\/pre><h2>✨ Special Functions<\/h2><pre>/g' | \
    sed 's/📋 QUICK REFERENCE CARD:/<\/pre><h2>📋 Quick Reference Card<\/h2><pre>/g' | \
    sed 's/Super+\([^ ]*\)/<span class="key">Super+\1<\/span>/g'
    
    echo "</pre></body></html>"
} > "$HTML_FILE"

echo "✅ Keybinding reference generated:"
echo "   Text: $OUTPUT_FILE"
echo "   HTML: $HTML_FILE"
EOF

# ============================================================================
# STRATEGY 3: Rofi Keybinding Helper
# ============================================================================

cat > ~/.config/i3/scripts/show-keybindings.sh << 'EOF'
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
EOF

# ============================================================================
# STRATEGY 2+: Auto-updating keybinding watcher
# ============================================================================

cat > ~/.config/i3/scripts/watch-config.sh << 'EOF'
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
EOF

# ============================================================================
# Make scripts executable
# ============================================================================

chmod +x ~/.config/i3/scripts/generate-keybindings.sh
chmod +x ~/.config/i3/scripts/show-keybindings.sh
chmod +x ~/.config/i3/scripts/watch-config.sh

# ============================================================================
# Generate initial reference
# ============================================================================

echo "📚 Generating initial keybinding reference..."
~/.config/i3/scripts/generate-keybindings.sh

echo ""
echo "✅ Setup complete! Here's what you can do:"
echo ""
echo "📖 View keybinding reference:"
echo "   cat ~/.config/i3/keybindings.txt"
echo "   firefox ~/.config/i3/keybindings.html"
echo ""
echo "🔍 Interactive keybinding helper:"
echo "   ~/.config/i3/scripts/show-keybindings.sh"
echo ""
echo "🔄 Auto-regenerate on config changes:"
echo "   ~/.config/i3/scripts/watch-config.sh &"
echo ""
echo "💡 Add these to your i3 config:"
echo "   # Keybinding helper (Strategy 3)"
echo "   bindsym \$mod+F1 exec --no-startup-id ~/.config/i3/scripts/show-keybindings.sh"
echo ""
echo "   # Auto-start config watcher"
echo "   exec --no-startup-id ~/.config/i3/scripts/watch-config.sh"
echo ""
echo "🎯 Your keybindings will now be consistent and easily accessible!"