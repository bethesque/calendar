#!/bin/bash

set -Eeuo pipefail

echo "Checking for alarms at $(date) for $USER"

# --- CONFIG ---
if [ -z "${1:-}" ]; then
    echo "Usage: $0 <device-mac>" >&2
    exit 1
fi

DEVICE_MAC=$1

# --- ENV FIXES (critical for cron) ---
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

# --- Wait for Bluetooth service ---
sudo systemctl start bluetooth
sleep 5

# --- Connect Bluetooth device ---
for i in {1..5}; do
    echo -e "connect $DEVICE_MAC\nquit" | bluetoothctl
    sleep 2
    
    if pactl list short sinks | grep -q bluez; then
        break
    fi
done

# --- Wait for connection to settle ---
sleep 5

# --- Set PulseAudio sink ---
SINK=$(pactl list short sinks | grep bluez | awk '{print $2}' | head -n1)

if [ -n "$SINK" ]; then
    pactl set-default-sink "$SINK"
else
    echo "No Bluetooth sink found"
fi

/usr/bin/python check_for_alarms.py
