#!/bin/sh -e
# Run from project root. This script is intended to be run from a cron job to update
# the calendar screen once an hour.

# Runs once an hour, updating the calendar if any events have changed

# Make this work on mac and on the raspberry pi.
if [ -x "/usr/bin/python" ]; then
  echo "/usr/bin/python exists and is executable."
  PYTH="/usr/bin/python"
else
  echo "/usr/bin/python is not executable or does not exist. Using python on path."
  PYTH="python"
fi

echo "Executing main"
# Allow use of cached image
timeout --kill-after=30s 600 "$PYTH" main.py
