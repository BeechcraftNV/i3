#!/bin/bash
set -euo pipefail

# Comprehensive Screenshot Management Script
# Usage: screenshot.sh [full|selection|window|gui|clipboard]

SCREENSHOT_DIR="$HOME/Pictures/screenshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$SCREENSHOT_DIR"/{full,selection,window}

# Ensure flameshot present
if ! command -v flameshot >/dev/null 2>&1; then
  command -v notify-send >/dev/null 2>&1 && notify-send "Screenshot" "flameshot is not installed" || true
  echo "flameshot not found" >&2
  exit 1
fi

case "${1:-full}" in
  "full")
    # Full screen screenshot - active monitor only
    if ! command -v jq >/dev/null 2>&1; then
      # Fallback to all screens
      flameshot full -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
      command -v notify-send >/dev/null 2>&1 && notify-send "Screenshot" "Full screen saved to $SCREENSHOT_DIR/full/" || true
      exit 0
    fi
    OUTPUT=$(i3-msg -t get_workspaces | jq -r '.[] | select(.focused==true).output')
    if [[ -z "${OUTPUT:-}" ]]; then
      flameshot full -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
      command -v notify-send >/dev/null 2>&1 && notify-send "Screenshot" "Full screen saved to $SCREENSHOT_DIR/full/" || true
      exit 0
    fi
    # Find monitor index for flameshot -n
    mapfile -t CONNECTED < <(xrandr | awk '/ connected/{print $1}')
    INDEX=0
    FOUND=0
    for i in "${!CONNECTED[@]}"; do
      if [[ "${CONNECTED[$i]}" == "$OUTPUT" ]]; then INDEX=$i; FOUND=1; break; fi
    done
    if [[ "$FOUND" -eq 1 ]]; then
      flameshot screen -n "$INDEX" -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
    else
      flameshot full -p "$SCREENSHOT_DIR/full/fullscreen_$TIMESTAMP.png"
    fi
    command -v notify-send >/dev/null 2>&1 && notify-send "Screenshot" "Full screen saved to $SCREENSHOT_DIR/full/" || true
    ;;

  "selection")
    # Interactive selection
    flameshot gui -p "$SCREENSHOT_DIR/selection/selection_$TIMESTAMP.png"
    ;;

  "window")
    # Active window screenshot - saves to disk AND copies to clipboard
    if command -v xdotool >/dev/null 2>&1 && command -v maim >/dev/null 2>&1; then
      WINDOW_ID=$(xdotool getactivewindow 2>/dev/null || echo "")
      if [[ -n "$WINDOW_ID" ]]; then
        FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
        maim --window="$WINDOW_ID" "$FILEPATH"
        if command -v xclip >/dev/null 2>&1; then
          xclip -selection clipboard -t image/png < "$FILEPATH"
        fi
        command -v notify-send >/dev/null 2>&1 && notify-send "Screenshot" "Window captured → saved to disk${DISPLAY:+ and copied to clipboard}" || true
      else
        FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
        flameshot gui --path="$FILEPATH" --clipboard
      fi
    else
      FILEPATH="$SCREENSHOT_DIR/window/window_$TIMESTAMP.png"
      flameshot gui --path="$FILEPATH" --clipboard
    fi
    ;;

  "gui")
    flameshot gui
    ;;

  "clipboard")
    flameshot gui --clipboard
    ;;

  "config")
    flameshot config
    ;;

  *)
    echo "Usage: $0 [full|selection|window|gui|clipboard|config]" >&2
    exit 1
    ;;
esac
