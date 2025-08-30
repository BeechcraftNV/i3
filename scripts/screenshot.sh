#!/usr/bin/env bash
# screenshot.sh — centralized, robust screenshots for i3
# Usage: screenshot.sh [full|selection|window|gui|clipboard|config]
set -euo pipefail

CMD="${1:-selection}"
DIR="${HOME}/Pictures/screenshots"
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "${DIR}"/{full,selection,window}

have() { command -v "$1" >/dev/null 2>&1; }

notify() {
  have notify-send && notify-send "$1" "$2" || true
}

# Copy stdin PNG to clipboard (xclip)
to_clipboard() {
  xclip -selection clipboard -t image/png -i
}

# Verify clipboard contains image/png (for debug)
verify_clip() {
  xclip -selection clipboard -t TARGETS -o 2>/dev/null | grep -qi 'image/png' && return 0 || return 1
}

# Capture helpers
capture_full_active_monitor() {
  # Active monitor geometry via i3 + xrandr
  local out geom
  out="$(i3-msg -t get_workspaces | jq -r '.[] | select(.focused==true).output')"
  geom="$(xrandr --query | awk -v o="$out" '$0 ~ o" connected" { match($0, /[0-9]+x[0-9]+\+[0-9]+\+[0-9]+/, m); print m[0] }')"
  if [[ -z "$geom" ]]; then
    # fallback: full screen
    have maim && maim || exit 1
  else
    have maim && maim -g "$geom" || exit 1
  fi
}

capture_window() {
  local win
  win="$(xdotool getactivewindow 2>/dev/null || true)"
  if [[ -n "$win" ]] && have maim; then
    maim -i "$win"
  else
    # Fallback: use flameshot gui to select window
    have flameshot && flameshot gui -c && exit 0
    exit 1
  fi
}

case "$CMD" in
  full)
    # Preferred: flameshot full to clipboard & file
    if have flameshot; then
      flameshot full -c -p "${DIR}/full" && notify "Screenshot" "Fullscreen → clipboard"
    else
      # Fallback: maim (active monitor) → clipboard
      capture_full_active_monitor | to_clipboard
      notify "Screenshot" "Fullscreen (maim) → clipboard"
      # Also save file:
      capture_full_active_monitor > "${DIR}/full/${TS}.png" || true
    fi
    ;;

  window)
    if have maim && have xdotool; then
      capture_window | tee "${DIR}/window/${TS}.png" | to_clipboard
      notify "Screenshot" "Active window → clipboard"
    else
      # Fallback to flameshot GUI for manual window pick
      have flameshot && flameshot gui -c -p "${DIR}/window" && notify "Screenshot" "Window (gui) → clipboard" || {
        notify "Screenshot" "No tool available (need flameshot or maim+xdotool)"; exit 1; }
    fi
    ;;

  selection|clipboard)
    # Region to clipboard (and save)
    if have flameshot; then
      flameshot gui -c -p "${DIR}/selection" && notify "Screenshot" "Selection → clipboard"
    else
      # Fallback: maim -s to clipboard & file
      have maim || { notify "Screenshot" "maim not installed"; exit 1; }
      have slop || { notify "Screenshot" "slop not installed for selection"; exit 1; }
      maim -s | tee "${DIR}/selection/${TS}.png" | to_clipboard
      notify "Screenshot" "Selection (maim) → clipboard"
    fi
    ;;

  gui)
    # Flameshot editor GUI (clipboard + file)
    if have flameshot; then
      flameshot gui -c -p "${DIR}/selection" && notify "Screenshot" "GUI → clipboard"
    else
      notify "Screenshot" "Flameshot not installed for GUI mode"; exit 1
    fi
    ;;

  config)
    have flameshot && flameshot config || { echo "Flameshot not installed"; exit 1; }
    ;;

  *)
    cat <<EOF
Usage: $0 [full|selection|window|gui|clipboard|config]
  full       Fullscreen (active monitor) → clipboard (+ save)
  selection  Region select → clipboard (+ save)
  window     Active window → clipboard (+ save)
  gui        Flameshot GUI editor → clipboard (+ save)
  clipboard  Alias of 'selection'
  config     Open Flameshot configuration
EOF
    exit 1
    ;;
esac

# Optional: quick verification of clipboard
if verify_clip; then
  echo "Clipboard contains image/png"
else
  echo "Warning: clipboard does not show image/png"
fi
