#!/bin/bash
# Run from project root. This script is intended to be run from a cron job to play the morning announcements.

set -Eeuo pipefail

echo "Morning announcements at $(date)"

# --- CONFIG ---
if [ -z "${1:-}" ]; then
    echo "Usage: $0 <device-mac>" >&2
    exit 1
fi

export DEVICE_MAC="$1"
export PATH="/home/$(id -u)/.local/bin:${PATH}"

./script/connect_bluetooth_speaker.sh

ecal-announce
