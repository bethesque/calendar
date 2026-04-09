#!/bin/bash

set -Eeuo pipefail

echo "Checking for alarms at $(date)"

# --- CONFIG ---
if [ -z "${2:-}" ]; then
    echo "Usage: $0 <device-mac> <window>" >&2
    exit 1
fi

export DEVICE_MAC="$1"
WINDOW="$2"

./script/connect_bluetooth_speaker.sh

/usr/bin/python check_for_alarms.py --window "$WINDOW"
