#!/bin/bash
# Open the preferred web browser with sensible fallbacks.
# Prefers warp-preview if available, then brave, firefox, chromium, or xdg-open.
# Usage: open-browser.sh [URL]

set -euo pipefail

url="${1:-about:blank}"

if command -v warp-preview >/dev/null 2>&1; then
  exec warp-preview "$url"
elif command -v brave >/dev/null 2>&1; then
  exec brave "$url"
elif command -v firefox >/dev/null 2>&1; then
  exec firefox "$url"
elif command -v chromium >/dev/null 2>&1; then
  exec chromium "$url"
elif command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "$url"
else
  # Best-effort notification if available
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "No browser found" "Tried warp-preview, brave, firefox, chromium, xdg-open"
  fi
  exit 127
fi

