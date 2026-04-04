#!/bin/bash

set -Eeuo pipefail

#!/bin/bash

# Path to the audio file
ALARM_FILE="alarm.mp3"

# Path to the PID file
PID_FILE="/tmp/alarm.pid"

# Start mpg123 in the background
mpg123 "$ALARM_FILE" &
PID=$!

# Give it a short moment to see if it exits immediately
sleep 0.1

# Check if the process is still running
if kill -0 $PID 2>/dev/null; then
    # Process started successfully, write PID file
    echo $PID > "$PID_FILE"
    echo "Playing $ALARM_FILE with PID $PID"
else
    # Process failed
    echo "Failed to start mpg123"
    exit 1
fi
