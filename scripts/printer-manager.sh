#!/bin/bash

# i3 Printer Management Script
# Provides comprehensive printer management for Manjaro i3 setup

PRINTER_NAME="DCP-L2550DW"
CUPS_WEB="http://localhost:631"

show_help() {
    cat << EOF
i3 Printer Manager - Usage:
    $0 menu       - Show rofi menu with all options
    $0 test       - Print test page
    $0 status     - Show printer and queue status
    $0 queue      - Show print queue
    $0 clear      - Clear print queue
    $0 web        - Open CUPS web interface
    $0 config     - Open printer configuration
    $0 add        - Add new printer (GUI)
    $0 help       - Show this help
EOF
}

send_notification() {
    if command -v notify-send > /dev/null; then
        notify-send "Printer Manager" "$1"
    else
        echo "Printer Manager: $1"
    fi
}

print_test_page() {
    if lp -d "$PRINTER_NAME" /usr/share/cups/data/testprint 2>/dev/null; then
        send_notification "Test page sent to $PRINTER_NAME"
    else
        send_notification "Failed to send test page"
    fi
}

show_status() {
    local status=$(lpstat -p "$PRINTER_NAME" 2>/dev/null | head -1)
    local queue=$(lpq -P "$PRINTER_NAME" 2>/dev/null | tail -n +2)
    
    if [ -n "$status" ]; then
        if [ -n "$queue" ]; then
            send_notification "Printer: Ready\nQueue: $queue"
        else
            send_notification "Printer: Ready\nQueue: Empty"
        fi
    else
        send_notification "Printer: Not available"
    fi
}

show_queue() {
    local queue=$(lpq -P "$PRINTER_NAME" 2>/dev/null | tail -n +2)
    if [ -n "$queue" ]; then
        send_notification "Print Queue:\n$queue"
    else
        send_notification "Print queue is empty"
    fi
}

clear_queue() {
    if cancel -a "$PRINTER_NAME" 2>/dev/null; then
        send_notification "Print queue cleared"
    else
        send_notification "Failed to clear print queue or queue already empty"
    fi
}

open_web_interface() {
    if command -v xdg-open > /dev/null; then
        xdg-open "$CUPS_WEB"
    else
        send_notification "Cannot open web browser. Go to: $CUPS_WEB"
    fi
}

open_config() {
    if command -v system-config-printer > /dev/null; then
        system-config-printer &
    else
        send_notification "system-config-printer not installed"
    fi
}

add_printer() {
    if command -v system-config-printer > /dev/null; then
        system-config-printer --add-printer &
    else
        send_notification "system-config-printer not installed"
    fi
}

show_menu() {
    local choice=$(echo -e "Print Test Page\nPrinter Status\nPrint Queue\nClear Queue\nCUPS Web Interface\nPrinter Settings\nAdd New Printer\nHelp" | \
                  rofi -dmenu -i -p "Printer Manager:" -theme-str "window {width: 300px;}")
    
    case "$choice" in
        "Print Test Page")
            print_test_page
            ;;
        "Printer Status")
            show_status
            ;;
        "Print Queue")
            show_queue
            ;;
        "Clear Queue")
            clear_queue
            ;;
        "CUPS Web Interface")
            open_web_interface
            ;;
        "Printer Settings")
            open_config
            ;;
        "Add New Printer")
            add_printer
            ;;
        "Help")
            show_help | rofi -dmenu -i -p "Help:" -theme-str "window {width: 500px;}"
            ;;
    esac
}

# Main script logic
case "${1:-menu}" in
    menu)
        show_menu
        ;;
    test)
        print_test_page
        ;;
    status)
        show_status
        ;;
    queue)
        show_queue
        ;;
    clear)
        clear_queue
        ;;
    web)
        open_web_interface
        ;;
    config)
        open_config
        ;;
    add)
        add_printer
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
