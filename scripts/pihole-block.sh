#!/usr/bin/env bash
# i3blocks Pi-hole status block with optional click-to-toggle
# Requirements: curl, jq; optional: xdg-open for right-click
# Config (optional): ~/.config/i3/pihole.env with:
#   PIHOLE_API_URL="http://<host>/admin/api.php"
#   PIHOLE_DASHBOARD_URL="http://<host>/admin"
#   PIHOLE_API_TOKEN="<token>"   # only for toggling

set -euo pipefail

ENV_FILE="${HOME}/.config/i3/pihole.env"
[[ -f "$ENV_FILE" ]] && . "$ENV_FILE"

API_URL="${PIHOLE_API_URL:-}"
DASH_URL="${PIHOLE_DASHBOARD_URL:-${API_URL%/api.php}}"
TOKEN="${PIHOLE_API_TOKEN:-}"

green="#50fa7b"
red="#ff5555"
orange="#ffb86c"
gray="#bbbbbb"

# Helper: print i3blocks 3-line output
out() { printf "%s\n%s\n%s\n" "$1" "$1" "$2"; }

# If not configured for API, try local CLI read-only as a last resort
cli_status() {
  if command -v pihole >/dev/null 2>&1; then
    if pihole status | grep -qi 'active'; then
      echo "enabled"
    else
      echo "disabled"
    fi
  else
    echo "unknown"
  fi
}

# Handle clicks
# 1: left  -> toggle enable/disable (requires TOKEN)
# 2: middle-> (no-op)
# 3: right -> open dashboard
if [[ "${BLOCK_BUTTON:-0}" -eq 1 ]]; then
  if [[ -n "$API_URL" && -n "$TOKEN" ]]; then
    status_json=$(curl -fsSL "${API_URL%/}/summaryRaw" || true)
    curr_status=$(jq -r '.status // empty' <<<"$status_json" 2>/dev/null || true)
    if [[ "$curr_status" == "enabled" ]]; then
      curl -fsS "${API_URL%/}/api.php?disable=300&auth=${TOKEN}" >/dev/null || true
    else
      curl -fsS "${API_URL%/}/api.php?enable&auth=${TOKEN}" >/dev/null || true
    fi
    pkill -RTMIN+11 i3blocks >/dev/null 2>&1 || true
  fi
  exit 0
elif [[ "${BLOCK_BUTTON:-0}" -eq 3 ]]; then
  if command -v xdg-open >/dev/null 2>&1 && [[ -n "$DASH_URL" ]]; then
    xdg-open "$DASH_URL" >/dev/null 2>&1 || true
  fi
  exit 0
fi

# Render status
if [[ -n "$API_URL" ]]; then
  json=$(timeout 2 curl -fsSL "${API_URL%/}/summaryRaw" 2>/dev/null || true)
  if [[ -n "$json" ]]; then
    status=$(jq -r '.status // "unknown"' <<<"$json")
    ads=$(jq -r '.ads_blocked_today // 0' <<<"$json")
    queries=$(jq -r '.dns_queries_today // 0' <<<"$json")
    pct=$(jq -r '.ads_percentage_today // 0' <<<"$json")
    grav_rel=$(jq -r '.gravity_last_updated.relative // empty' <<<"$json")

    color="$green"
    [[ "$status" != "enabled" ]] && color="$red"
    if grep -Eq '([0-9]+)\s+day' <<<"${grav_rel:-}"; then
      days=$(grep -Eo '([0-9]+)\s+day' <<<"$grav_rel" | awk '{print $1}' | head -1)
      if [[ -n "$days" && "$days" -ge 7 && "$status" == "enabled" ]]; then
        color="$orange"
      fi
    fi

    text="PH:${status^^} ${pct%%%} | ${ads}/${queries}"
    [[ -n "$grav_rel" ]] && text="${text} | G:${grav_rel}"
    out "$text" "$color"
    exit 0
  fi
fi

# Fallback to CLI if API failed or not configured
status_cli=$(cli_status)
if [[ "$status_cli" == "unknown" ]]; then
  # Final fallback: test DNS directly
  if timeout 2 host google.com 192.168.29.43 >/dev/null 2>&1; then
    out "PH:DNS-OK" "$green"
    exit 0
  else
    out "PH:DNS-FAIL" "$red"
    exit 2
  fi
fi

case "$status_cli" in
  enabled) out "PH:ENABLED" "$green" ;;
  disabled) out "PH:DISABLED" "$red" ;;
  *) out "PH:UNKNOWN" "$gray" ;;
esac

