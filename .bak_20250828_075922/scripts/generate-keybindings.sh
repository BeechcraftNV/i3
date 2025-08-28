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
