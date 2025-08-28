#!/bin/bash

# Robust Printer Status Monitor for i3blocks
# Provides intelligent multi-printer status with fallback mechanisms
# Exit codes: 0=OK, 1=warning (queue/partial), 2=error (offline)

set -eo pipefail

# === CONFIGURATION ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")"
DISCOVERY_MODULE="$SCRIPT_DIR/lib/printer_discovery.sh"
CONFIG_FILE="$CONFIG_DIR/printers.conf"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/i3-printer"
STATUS_CACHE="$CACHE_DIR/status_cache"
LOG_FILE="${LOG_FILE:-$HOME/.cache/i3-printer.log}"

# Ensure directories exist
mkdir -p "$CACHE_DIR"

# === LOGGING FUNCTIONS ===
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$LOG_FILE" 2>/dev/null || true
}

debug() { [[ "${debug_mode:-false}" == "true" ]] && log "DEBUG" "$@"; }
info() { log "INFO" "$@"; }
warn() { log "WARN" "$@"; }
error() { log "ERROR" "$@"; }

# === CONFIGURATION LOADER ===
load_config() {
    # Set defaults for status display
    default_printer=""
    single_printer_format="{status}"
    multi_printer_format="{short}:{status}"
    max_printer_name_length="8"
    show_job_details="true"
    enable_network_ping="true"
    ping_timeout="2"
    
    # Color defaults (i3blocks format)
    color_ready="#4CAF50"
    color_printing="#2196F3" 
    color_queue="#FF9800"
    color_offline="#F44336"
    color_unknown="#FFC107"
    color_multi="#9C27B0"
    
    # Load config file if available
    if [[ -f "$CONFIG_FILE" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ "$line" =~ ^[[:space:]]*$ ]] && continue
            
            if [[ "$line" =~ ^[[:space:]]*([^=]+)=[[:space:]]*\"?([^\"#]*)\"?[[:space:]]*(#.*)?$ ]]; then
                key="${BASH_REMATCH[1]}"
                value="${BASH_REMATCH[2]}"
                value=$(echo "$value" | sed 's/[[:space:]]*$//')
                declare -g "$key"="$value"
            fi
        done < "$CONFIG_FILE"
        debug "Loaded configuration from $CONFIG_FILE"
    fi
}

# === CACHE MANAGEMENT ===
save_status_cache() {
    local status_data="$1"
    echo "$status_data" > "$STATUS_CACHE" 2>/dev/null || warn "Failed to save status cache"
    debug "Saved status to cache"
}

load_status_cache() {
    if [[ -f "$STATUS_CACHE" ]]; then
        # Check if cache is recent (within last 30 seconds)
        local cache_age=$(( $(date +%s) - $(stat -c %Y "$STATUS_CACHE" 2>/dev/null || echo 0) ))
        if [[ $cache_age -lt 30 ]]; then
            cat "$STATUS_CACHE" 2>/dev/null || true
            debug "Loaded status from cache"
            return 0
        fi
    fi
    return 1
}

# === PRINTER STATUS FUNCTIONS ===

get_printer_status() {
    local printer_name="$1"
    local status=""
    local queue_count=0
    local is_online=true
    
    # Try CUPS status first
    local cups_status=$(lpstat -p "$printer_name" 2>/dev/null | head -1 || echo "")
    
    if [[ -n "$cups_status" ]]; then
        if echo "$cups_status" | grep -q "idle"; then
            status="READY"
        elif echo "$cups_status" | grep -q "printing"; then
            status="PRINTING"
        elif echo "$cups_status" | grep -q "disabled\|stopped"; then
            status="OFFLINE"
            is_online=false
        else
            status="UNKNOWN"
        fi
        
        # Check queue if printer seems online
        if [[ "$is_online" == "true" ]] && [[ "$show_job_details" == "true" ]]; then
            # Get queue count (skip header, count only job lines)
            local queue_output=$(lpq -P "$printer_name" 2>/dev/null || echo "")
            if echo "$queue_output" | grep -q "no entries"; then
                queue_count=0
            else
                queue_count=$(echo "$queue_output" | tail -n +2 | grep -c '^[0-9]' || echo 0)
            fi
            if [[ $queue_count -gt 0 ]] && [[ "$status" == "READY" ]]; then
                status="QUEUE"
            fi
        fi
    else
        # CUPS failed, try network ping for network printers
        if [[ "$enable_network_ping" == "true" ]]; then
            local printer_uri=$(lpstat -v "$printer_name" 2>/dev/null | grep -oP 'device for \S+: \K.*' || echo "")
            
            if [[ "$printer_uri" =~ ipp://([^/:]+) ]]; then
                local hostname="${BASH_REMATCH[1]}"
                if timeout "$ping_timeout" ping -c 1 "$hostname" >/dev/null 2>&1; then
                    status="UNKNOWN"
                    debug "Printer $printer_name: CUPS failed but network ping successful"
                else
                    status="OFFLINE"
                    is_online=false
                    debug "Printer $printer_name: Network ping failed"
                fi
            else
                status="OFFLINE"
                is_online=false
            fi
        else
            status="OFFLINE" 
            is_online=false
        fi
    fi
    
    echo "${printer_name}|${status}|${queue_count}|${is_online}"
}

# === STATUS FORMATTING ===

get_printer_short_name() {
    local name="$1"
    local max_len="$max_printer_name_length"
    
    # Try to create meaningful abbreviation
    if [[ ${#name} -le $max_len ]]; then
        echo "$name"
    elif [[ "$name" =~ ^([A-Z]+) ]]; then
        # Extract capital letters (e.g., "Brother_L2550DW" -> "BL2550")
        echo "$name" | sed 's/[^A-Z0-9]//g' | cut -c1-$max_len
    else
        # Just truncate
        echo "${name:0:$max_len}"
    fi
}

format_status_display() {
    local printer_data="$1"
    local printer_count=$(echo "$printer_data" | wc -l)
    local format=""
    local output=""
    local exit_code=0
    local color=""
    
    if [[ $printer_count -eq 1 ]]; then
        # Single printer display
        format="$single_printer_format"
        IFS='|' read -r name status queue_count is_online <<< "$printer_data"
        
        local short_name=$(get_printer_short_name "$name")
        local status_text="$status"
        
        if [[ "$status" == "QUEUE" ]] && [[ $queue_count -gt 0 ]]; then
            status_text="QUEUE($queue_count)"
            exit_code=1  # Warning
        elif [[ "$status" == "PRINTING" ]] && [[ $queue_count -gt 0 ]]; then
            status_text="PRINTING($queue_count)"
        elif [[ "$status" == "OFFLINE" ]]; then
            exit_code=2  # Error
        fi
        
        # Apply format template
        output="$format"
        output="${output//\{name\}/$name}"
        output="${output//\{short\}/$short_name}"
        output="${output//\{status\}/$status_text}"
        output="${output//\{queue\}/$queue_count}"
        
        # Select color
        case "$status" in
            "READY") color="$color_ready" ;;
            "PRINTING") color="$color_printing" ;;
            "QUEUE") color="$color_queue" ;;
            "OFFLINE") color="$color_offline" ;;
            *) color="$color_unknown" ;;
        esac
        
    else
        # Multi-printer display
        format="$multi_printer_format"
        local printer_statuses=()
        local overall_exit_code=0
        
        while IFS='|' read -r name status queue_count is_online; do
            [[ -z "$name" ]] && continue
            
            local short_name=$(get_printer_short_name "$name")
            local status_text="$status"
            
            if [[ "$status" == "QUEUE" ]] && [[ $queue_count -gt 0 ]]; then
                status_text="QUEUE($queue_count)"
                [[ $overall_exit_code -eq 0 ]] && overall_exit_code=1
            elif [[ "$status" == "PRINTING" ]] && [[ $queue_count -gt 0 ]]; then
                status_text="PRINTING($queue_count)"
            elif [[ "$status" == "OFFLINE" ]]; then
                overall_exit_code=2
            fi
            
            # Apply format for this printer
            local printer_output="$format"
            printer_output="${printer_output//\{name\}/$name}"
            printer_output="${printer_output//\{short\}/$short_name}"
            printer_output="${printer_output//\{status\}/$status_text}"
            printer_output="${printer_output//\{queue\}/$queue_count}"
            
            printer_statuses+=("$printer_output")
        done <<< "$printer_data"
        
        # Join all printer statuses
        output=$(IFS=' '; echo "${printer_statuses[*]}")
        exit_code=$overall_exit_code
        color="$color_multi"
    fi
    
    echo "$output"
    echo "$output"  # i3blocks format: line 1 = full, line 2 = short
    echo "$color"
    
    debug "Status display: $output (exit code: $exit_code)"
    return $exit_code
}

# === PRINTER SELECTION LOGIC ===

select_printer() {
    # Get available printers using discovery module
    if [[ ! -f "$DISCOVERY_MODULE" ]]; then
        error "Discovery module not found: $DISCOVERY_MODULE"
        return 1
    fi
    
    local available_printers=$("$DISCOVERY_MODULE" --format simple 2>/dev/null || echo "")
    
    if [[ -z "$available_printers" ]]; then
        warn "No printers discovered"
        return 1
    fi
    
    debug "Available printers: $available_printers"
    
    # Apply selection logic
    if [[ -n "$default_printer" ]] && echo "$available_printers" | grep -q "^$default_printer$"; then
        echo "$default_printer"
    else
        # Use first available printer
        echo "$available_printers" | head -1
    fi
}

# === MAIN EXECUTION ===
main() {
    load_config
    
    # Try to load from cache first
    local cached_status=$(load_status_cache || echo "")
    if [[ -n "$cached_status" ]]; then
        echo "$cached_status"
        debug "Using cached status"
        return 0
    fi
    
    # Get printer(s) to monitor
    local selected_printers=""
    if [[ -n "${force_single_printer:-}" ]]; then
        selected_printers="$force_single_printer"
        debug "Forced single printer: $selected_printers"
    elif [[ -n "$default_printer" ]]; then
        selected_printers="$default_printer"
        debug "Using configured default: $selected_printers"
    else
        # Auto-select: use first available, or all if multiple
        local available=$("$DISCOVERY_MODULE" --format simple 2>/dev/null || echo "")
        local count=$(echo "$available" | grep -c '^[^[:space:]]*$' 2>/dev/null || echo 0)
        
        if [[ $count -eq 1 ]]; then
            selected_printers="$available"
            debug "Single printer auto-selected: $selected_printers"
        elif [[ $count -gt 1 ]]; then
            selected_printers="$available"
            debug "Multiple printers found: monitoring all"
        else
            error "No printers available"
            echo "NO PRINTER"
            echo "NO PRINTER"
            echo "$color_offline"
            return 2
        fi
    fi
    
    # Get status for selected printer(s)
    local status_results=""
    while read -r printer; do
        [[ -z "$printer" ]] && continue
        local printer_status=$(get_printer_status "$printer")
        status_results+="$printer_status"$'\n'
    done <<< "$selected_printers"
    
    # Remove trailing newline
    status_results=$(echo "$status_results" | grep -v '^$')
    
    if [[ -z "$status_results" ]]; then
        error "Failed to get printer status"
        echo "ERROR"
        echo "ERROR"
        echo "$color_offline"
        return 2
    fi
    
    # Format and display results
    format_status_display "$status_results"
    local format_exit_code=$?
    
    # Save to cache (capture the output for caching)
    local formatted_output=$(format_status_display "$status_results" 2>/dev/null)
    save_status_cache "$formatted_output"
    
    return $format_exit_code
}

# Handle click events from i3blocks
case "${BLOCK_BUTTON:-}" in
    1)  # Left click - open printer manager
        if command -v "$SCRIPT_DIR/printer-manager-robust.sh" >/dev/null 2>&1; then
            "$SCRIPT_DIR/printer-manager-robust.sh" menu &
        fi
        ;;
    2)  # Middle click - refresh status
        rm -f "$STATUS_CACHE"
        ;;
    3)  # Right click - open CUPS web interface
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "http://localhost:631" >/dev/null 2>&1 &
        fi
        ;;
esac

# Run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
