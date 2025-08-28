#!/bin/bash

# Quick Working Printer Status for i3blocks
# Temporary solution while debugging the robust version

# Direct printer discovery using lpstat
PRINTERS=$(lpstat -p 2>/dev/null | awk '{print $2}' | head -2 || echo "")

if [[ -z "$PRINTERS" ]]; then
    echo "NO PRINTER"
    echo "NO PRINTER"
    echo "#F44336"  # Red
    exit 2
fi

# Check status of discovered printers
STATUS_DISPLAY=""
OVERALL_STATUS="READY"
COLOR="#4CAF50"  # Green

while read -r printer; do
    [[ -z "$printer" ]] && continue
    
    # Get printer status
    PRINTER_STATUS=$(lpstat -p "$printer" 2>/dev/null | head -1 || echo "")
    
    if echo "$PRINTER_STATUS" | grep -q "idle"; then
        STATUS="READY"
    elif echo "$PRINTER_STATUS" | grep -q "printing"; then
        STATUS="PRINTING"
        COLOR="#2196F3"  # Blue
        OVERALL_STATUS="PRINTING"
    else
        STATUS="OFFLINE"
        COLOR="#F44336"  # Red
        OVERALL_STATUS="OFFLINE"
    fi
    
    # Abbreviate printer name
    SHORT_NAME=$(echo "$printer" | sed 's/[^A-Z0-9]//g' | cut -c1-8)
    
    if [[ -n "$STATUS_DISPLAY" ]]; then
        STATUS_DISPLAY="$STATUS_DISPLAY $SHORT_NAME:$STATUS"
    else
        STATUS_DISPLAY="$SHORT_NAME:$STATUS"
    fi
    
done <<< "$PRINTERS"

# If only one printer, show just status
PRINTER_COUNT=$(echo "$PRINTERS" | wc -l)
if [[ $PRINTER_COUNT -eq 1 ]]; then
    STATUS_DISPLAY="$OVERALL_STATUS"
fi

echo "$STATUS_DISPLAY"
echo "$STATUS_DISPLAY"
echo "$COLOR"

case "$OVERALL_STATUS" in
    "READY") exit 0 ;;
    "PRINTING") exit 0 ;;
    *) exit 2 ;;
esac
