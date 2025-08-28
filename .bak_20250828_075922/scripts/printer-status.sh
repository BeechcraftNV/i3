#!/bin/bash

# i3blocks Printer Status Script
# Shows printer status in the status bar

PRINTER_NAME="Brother_DCP_L2550DW_series_3c2af49f7385"

# Check if printer is available
if ! lpstat -p "$PRINTER_NAME" >/dev/null 2>&1; then
    echo "OFFLINE"
    echo "OFFLINE"
    echo "#E53935"  # Red color for offline
    exit 0
fi

# Get printer status
printer_status=$(lpstat -p "$PRINTER_NAME" 2>/dev/null | head -1)

# Check if printer is idle or printing
if echo "$printer_status" | grep -q "idle"; then
    # Check if there are jobs in queue
    queue_count=$(lpq -P "$PRINTER_NAME" 2>/dev/null | tail -n +2 | wc -l)
    
    if [ "$queue_count" -gt 0 ]; then
        echo "QUEUE($queue_count)"
        echo "QUEUE($queue_count)"  
        echo "#FFA500"  # Orange color for queued jobs
    else
        echo "READY"
        echo "READY"
        echo "#00FF00"  # Green color for ready
    fi
elif echo "$printer_status" | grep -q "printing"; then
    echo "PRINTING"
    echo "PRINTING"
    echo "#00BFFF"  # Blue color for printing
else
    echo "UNKNOWN"
    echo "UNKNOWN"
    echo "#FFFF00"  # Yellow color for unknown status
fi
