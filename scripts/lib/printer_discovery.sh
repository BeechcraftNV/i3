#!/bin/bash

# Robust Printer Discovery Module for i3 Printer Management
# Provides auto-discovery of available printers using multiple backends
# with intelligent fallback and caching mechanisms

set -euo pipefail

# === CONFIGURATION ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$CONFIG_DIR/printers.conf"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/i3-printer"
CACHE_FILE="$CACHE_DIR/discovery_cache"
LOG_FILE="${LOG_FILE:-$HOME/.cache/i3-printer.log}"

# Ensure cache directory exists
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
    # Set defaults
    use_cups_discovery="true"
    use_avahi_discovery="false"
    use_ipp_probe="false"
    cache_duration="30"
    debug_mode="false"
    fallback_to_system_printer="true"
    
    # Load config file if it exists
    if [[ -f "$CONFIG_FILE" ]]; then
        # Source config with error handling
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ "$line" =~ ^[[:space:]]*$ ]] && continue
            
            # Extract key=value pairs (handle inline comments)
            if [[ "$line" =~ ^[[:space:]]*([^=]+)=[[:space:]]*\"?([^\"#]*)\"?[[:space:]]*(#.*)?$ ]]; then
                key="${BASH_REMATCH[1]}"
                value="${BASH_REMATCH[2]}"
                # Trim trailing whitespace from value
                value=$(echo "$value" | sed 's/[[:space:]]*$//')
                declare -g "$key"="$value"
            fi
        done < "$CONFIG_FILE"
        debug "Loaded configuration from $CONFIG_FILE"
    else
        warn "Configuration file not found: $CONFIG_FILE, using defaults"
    fi
}

# === CACHE MANAGEMENT ===
is_cache_valid() {
    local cache_file="$1"
    local max_age="$2"
    
    if [[ ! -f "$cache_file" ]]; then
        return 1
    fi
    
    local cache_age=$(( $(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0) ))
    [[ $cache_age -lt $max_age ]]
}

save_to_cache() {
    local data="$1"
    echo "$data" > "$CACHE_FILE" 2>/dev/null || warn "Failed to save cache"
    debug "Saved discovery results to cache"
}

load_from_cache() {
    if is_cache_valid "$CACHE_FILE" "$cache_duration"; then
        cat "$CACHE_FILE" 2>/dev/null || true
        debug "Loaded results from cache"
        return 0
    fi
    return 1
}

# === PRINTER DISCOVERY BACKENDS ===

discover_cups_printers() {
    debug "Starting CUPS printer discovery"
    local printers=""
    
    # Get printer list from CUPS
    while IFS= read -r line; do
        if [[ "$line" =~ ^printer[[:space:]]+([^[:space:]]+)[[:space:]]+is[[:space:]]+(.+) ]]; then
            local name="${BASH_REMATCH[1]}"
            local status="${BASH_REMATCH[2]}"
            
            # Get detailed info
            local uri=$(lpstat -v "$name" 2>/dev/null | grep -oP 'device for \S+: \K.*' || echo "unknown")
            local description=$(lpstat -l -p "$name" 2>/dev/null | grep -oP 'Description: \K.*' || echo "$name")
            
            # Determine if this is the default printer
            local is_default="false"
            local system_default=$(lpstat -d 2>/dev/null | grep -oP 'system default destination: \K\S+' || echo "")
            [[ "$system_default" == "$name" ]] && is_default="true"
            
            # Add to results
            printers+="$name|$description|$uri|$status|$is_default"$'\n'
            debug "Found CUPS printer: $name ($status)"
        fi
    done < <(lpstat -p 2>/dev/null || true)
    
    echo -n "$printers"
}

discover_avahi_printers() {
    debug "Starting Avahi/mDNS printer discovery"
    local printers=""
    
    if ! command -v avahi-browse >/dev/null 2>&1; then
        debug "Avahi-browse not available, skipping mDNS discovery"
        return 0
    fi
    
    # Scan for IPP printers on network
    timeout 5 avahi-browse -rt _ipp._tcp 2>/dev/null | while read -r line; do
        if [[ "$line" =~ ^=[[:space:]]*[^[:space:]]*[[:space:]]*IPv4[[:space:]]*([^[:space:]]*)[[:space:]]*_ipp._tcp[[:space:]]*local$ ]]; then
            local service_name="${BASH_REMATCH[1]}"
            # Skip if we already know about this printer from CUPS
            if ! echo "$CUPS_RESULTS" | grep -q "$service_name"; then
                printers+="$service_name|Network IPP Printer|ipp://$service_name.local/|discovered|false"$'\n'
                debug "Found Avahi printer: $service_name"
            fi
        fi
    done 2>/dev/null || true
    
    echo -n "$printers"
}

discover_ipp_probe() {
    debug "Starting IPP network probe discovery"
    local printers=""
    
    if ! command -v ippfind >/dev/null 2>&1; then
        debug "ippfind not available, skipping IPP probe"
        return 0
    fi
    
    # Use ippfind to discover IPP printers on local network
    timeout 10 ippfind 2>/dev/null | while read -r uri; do
        if [[ "$uri" =~ ipp://([^/]*)(.*) ]]; then
            local hostname="${BASH_REMATCH[1]}"
            local service_name=$(echo "$hostname" | cut -d. -f1)
            
            # Skip if we already found this
            if ! echo "${CUPS_RESULTS}${AVAHI_RESULTS}" | grep -q "$service_name"; then
                printers+="$service_name|IPP Network Printer|$uri|discovered|false"$'\n'
                debug "Found IPP printer: $service_name at $uri"
            fi
        fi
    done 2>/dev/null || true
    
    echo -n "$printers"
}

# === MAIN DISCOVERY FUNCTION ===
discover_all_printers() {
    local all_printers=""
    
    # Always try CUPS first (most reliable)
    if [[ "$use_cups_discovery" == "true" ]]; then
        local cups_results=$(discover_cups_printers)
        all_printers+="$cups_results"
        export CUPS_RESULTS="$cups_results"  # For other backends to reference
        info "CUPS discovery found $(echo "$cups_results" | grep -c '^[^[:space:]]*|' || echo 0) printer(s)"
    fi
    
    # Optional: Avahi/mDNS discovery
    if [[ "$use_avahi_discovery" == "true" ]]; then
        local avahi_results=$(discover_avahi_printers)
        all_printers+="$avahi_results"
        export AVAHI_RESULTS="$avahi_results"
        info "Avahi discovery found $(echo "$avahi_results" | grep -c '^[^[:space:]]*|' || echo 0) additional printer(s)"
    fi
    
    # Optional: IPP probe
    if [[ "$use_ipp_probe" == "true" ]]; then
        local ipp_results=$(discover_ipp_probe)
        all_printers+="$ipp_results"
        info "IPP probe found $(echo "$ipp_results" | grep -c '^[^[:space:]]*|' || echo 0) additional printer(s)"
    fi
    
    # Deduplicate and sort
    echo "$all_printers" | grep -v '^$' | sort -u || true
}

# === OUTPUT FORMATTERS ===
format_table() {
    local data="$1"
    printf "%-20s %-30s %-15s %-10s\n" "NAME" "DESCRIPTION" "STATUS" "DEFAULT"
    printf "%-20s %-30s %-15s %-10s\n" "----" "-----------" "------" "-------"
    
    while IFS='|' read -r name desc uri status is_default; do
        [[ -z "$name" ]] && continue
        # Truncate long descriptions
        desc=$(echo "$desc" | cut -c1-28)
        [[ "${#desc}" -gt 28 ]] && desc="${desc}..."
        
        printf "%-20s %-30s %-15s %-10s\n" "$name" "$desc" "$status" "$is_default"
    done <<< "$data"
}

format_json() {
    local data="$1"
    echo "{"
    echo '  "printers": ['
    
    local first=true
    while IFS='|' read -r name desc uri status is_default; do
        [[ -z "$name" ]] && continue
        
        [[ "$first" == "false" ]] && echo "    ,"
        echo "    {"
        echo "      \"name\": \"$name\","
        echo "      \"description\": \"$desc\","
        echo "      \"uri\": \"$uri\","
        echo "      \"status\": \"$status\","
        echo "      \"is_default\": $is_default"
        echo -n "    }"
        first=false
    done <<< "$data"
    
    echo
    echo "  ],"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"discovery_methods\": ["
    [[ "$use_cups_discovery" == "true" ]] && echo "    \"cups\","
    [[ "$use_avahi_discovery" == "true" ]] && echo "    \"avahi\","
    [[ "$use_ipp_probe" == "true" ]] && echo "    \"ipp\""
    echo "  ]"
    echo "}"
}

format_simple() {
    local data="$1"
    while IFS='|' read -r name desc uri status is_default; do
        [[ -z "$name" ]] && continue
        echo "$name"
    done <<< "$data"
}

# === CLI INTERFACE ===
show_help() {
    cat << 'EOF'
Printer Discovery Module - Usage:

    printer_discovery.sh [OPTIONS]

OPTIONS:
    --format FORMAT    Output format: table (default), json, simple, raw
    --no-cache        Force fresh discovery, ignore cache
    --cache-only      Only return cached results, don't discover
    --help            Show this help message

EXAMPLES:
    # Basic discovery with table output
    printer_discovery.sh

    # JSON output for scripts
    printer_discovery.sh --format json

    # Force fresh scan
    printer_discovery.sh --no-cache

    # Just printer names
    printer_discovery.sh --format simple

EOF
}

# === MAIN EXECUTION ===
main() {
    local format="table"
    local use_cache=true
    local cache_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --format)
                format="$2"
                shift 2
                ;;
            --no-cache)
                use_cache=false
                shift
                ;;
            --cache-only)
                cache_only=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Load configuration
    load_config
    
    # Try cache first if enabled
    local printer_data=""
    if [[ "$use_cache" == "true" ]] && [[ "$cache_only" == "false" ]]; then
        printer_data=$(load_from_cache || true)
    fi
    
    # If cache failed or disabled, do fresh discovery
    if [[ -z "$printer_data" ]] && [[ "$cache_only" == "false" ]]; then
        info "Starting printer discovery"
        printer_data=$(discover_all_printers)
        
        # Save to cache
        if [[ "$use_cache" == "true" ]] && [[ -n "$printer_data" ]]; then
            save_to_cache "$printer_data"
        fi
    elif [[ "$cache_only" == "true" ]] && [[ -z "$printer_data" ]]; then
        warn "No cached results available and cache-only mode enabled"
        exit 1
    fi
    
    # Output results in requested format
    case "$format" in
        table)
            format_table "$printer_data"
            ;;
        json)
            format_json "$printer_data"
            ;;
        simple)
            format_simple "$printer_data"
            ;;
        raw)
            echo "$printer_data"
            ;;
        *)
            error "Unknown format: $format"
            exit 1
            ;;
    esac
    
    # Log summary
    local count=$(echo "$printer_data" | grep -c '^[^[:space:]]*|' 2>/dev/null || echo 0)
    info "Discovery complete: $count printer(s) found"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
