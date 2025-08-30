#!/bin/bash
# Audio output selector for i3 – rofi menu

set -euo pipefail

# Sink mapping - friendly names to actual sink names
declare -A SINK_MAP=(
    ["USB Audio"]="alsa_output.usb-KTMicro_KT_USB_Audio_2021-06-07-0000-0000-0000--00.analog-stereo"
    ["Internal Speakers"]="alsa_output.pci-0000_00_1f.3.analog-stereo"
    ["HDMI Audio"]="alsa_output.pci-0000_00_1f.3.hdmi-stereo"
)

# Profile mappings for built-in card profile switching
declare -A PROFILE_MAP=(
    ["Internal Speakers"]="output:analog-stereo"
    ["HDMI Audio"]="output:hdmi-stereo"
)

# Card name for built-in audio
BUILTIN_CARD="alsa_card.pci-0000_00_1f.3"

# Function to detect available sinks (including potential profile-based sinks)
get_available_sinks() {
    local available_sinks=()
    
    # Always include Internal Speakers and HDMI Audio (built-in card supports both)
    available_sinks+=("Internal Speakers")
    available_sinks+=("HDMI Audio")
    
    # Check for USB Audio device
    if pactl list short sinks | grep -q "usb-KTMicro_KT_USB_Audio"; then
        available_sinks+=("USB Audio")
    fi
    
    printf '%s\n' "${available_sinks[@]}"
}

# Function to get current default sink and map to friendly label
get_current_sink() {
    local current_sink
    current_sink=$(pactl get-default-sink) || return 1
    
    for label in "${!SINK_MAP[@]}"; do
        if [[ "${SINK_MAP[$label]}" == "$current_sink" ]]; then
            echo "$label"
            return 0
        fi
    done
    
    # If no mapping found, return the sink name itself
    echo "$current_sink"
}

# Function to move all sink inputs to new sink
move_sink_inputs() {
    local target_sink="$1"
    
    pactl list short sink-inputs | while read -r id _ _ _ _; do
        pactl move-sink-input "$id" "$target_sink" 2>/dev/null || true
    done
}

# Function to handle Bluetooth connection
connect_bluetooth_device() {
    local device_name="$1"
    local device_mac=""
    
    # This is a placeholder for Bluetooth handling
    # In a real implementation, you would need to:
    # 1. Map device names to MAC addresses
    # 2. Check if device is paired but not connected
    # 3. Attempt connection with bluetoothctl
    
    # Example implementation would be:
    # if bluetoothctl info "$device_mac" | grep -q "Connected: no"; then
    #     if bluetoothctl connect "$device_mac"; then
    #         return 0
    #     else
    #         notify-send "Audio Output" "Failed to connect to $device_name" -u critical
    #         return 1
    #     fi
    # fi
    
    return 0
}

# Function to apply audio configuration
apply_audio_config() {
    local choice="$1"
    local sink_name=""
    
    # Get the actual sink name from our mapping
    if [[ -n "${SINK_MAP[$choice]:-}" ]]; then
        sink_name="${SINK_MAP[$choice]}"
    else
        notify-send "Audio Output" "Unknown audio device: $choice" -u critical
        return 1
    fi
    
    # Handle profile switching for built-in card devices
    if [[ -n "${PROFILE_MAP[$choice]:-}" ]]; then
        # Switch the card profile first
        if ! pactl set-card-profile "$BUILTIN_CARD" "${PROFILE_MAP[$choice]}"; then
            notify-send "Audio Output" "Failed to switch profile for $choice" -u critical
            return 1
        fi
        # Give the system a moment to create the sink
        sleep 0.5
    fi
    
    # Check if sink is available now
    if ! pactl list short sinks | grep -q "$sink_name"; then
        # Attempt Bluetooth connection if it's a BT device
        if [[ "$choice" == *"Bluetooth"* || "$choice" == *"BT"* ]]; then
            if ! connect_bluetooth_device "$choice"; then
                return 1
            fi
            # Wait a bit for the sink to appear after BT connection
            sleep 2
        fi
        
        # Check again if sink is available
        if ! pactl list short sinks | grep -q "$sink_name"; then
            notify-send "Audio Output" "Audio device '$choice' is not available" -u critical
            return 1
        fi
    fi
    
    # Set default sink
    if pactl set-default-sink "$sink_name"; then
        # Move all existing sink inputs to the new sink
        move_sink_inputs "$sink_name"
        
        # Send success notification
        notify-send "Audio Output" "Switched to $choice" -t 2000
        return 0
    else
        notify-send "Audio Output" "Failed to switch to $choice" -u critical
        return 1
    fi
}

# Main execution
main() {
    # Get available sinks
    local available_sinks
    if ! available_sinks=$(get_available_sinks); then
        notify-send "Audio Output" "Failed to detect audio devices" -u critical
        exit 1
    fi
    
    # Check if we have any available sinks
    if [[ -z "$available_sinks" ]]; then
        notify-send "Audio Output" "No audio devices available" -u critical
        exit 1
    fi
    
    # Get current sink
    local current_label
    if ! current_label=$(get_current_sink); then
        current_label="Unknown"
    fi
    
    # Build rofi options
    local options
    options=$(echo "$available_sinks" | sort)
    
    # Show rofi menu
    local choice
    choice=$(echo -e "Currently: $current_label\n---\n$options" | rofi -dmenu -i -p "Audio Output:" -theme-str 'window {width: 400px;} listview {lines: 6;}')
    
    # Apply the chosen configuration
    if [[ -n "$choice" && "$choice" != "Currently: $current_label" && "$choice" != "---" ]]; then
        if apply_audio_config "$choice"; then
            exit 0
        else
            exit 1
        fi
    fi
    
    # User cancelled or made no change
    exit 0
}

# Run main function
main "$@"
