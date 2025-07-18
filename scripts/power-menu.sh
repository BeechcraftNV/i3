#!/bin/bash

# Power menu script for i3blocks
# Handles both display and click events

case $BLOCK_BUTTON in
    1) # Left click - show power menu with rofi
        choice=$(echo -e "🔒 Lock\n💤 Sleep\n🔄 Restart\n⚡ Shutdown\n🔚 Logout\n❌ Cancel" | rofi -dmenu -i -p "Power Menu:" -theme-str 'window {width: 300px; height: 300px;}')
        
        case "$choice" in
            "🔒 Lock")
                i3lock-fancy || i3lock -c 000000
                ;;
            "💤 Sleep")
                systemctl suspend
                ;;
            "🔄 Restart")
                systemctl reboot
                ;;
            "⚡ Shutdown")
                systemctl poweroff
                ;;
            "🔚 Logout")
                i3-msg exit
                ;;
            "❌ Cancel"|"")
                # Do nothing
                ;;
        esac
        ;;
    2) # Middle click - quick sleep
        systemctl suspend
        ;;
    3) # Right click - enter system mode
        i3-msg mode "$mode_system"
        ;;
esac

# Always display the power icon
echo "⏻"
echo "⏻"
echo "#ff6b6b"
