#!/bin/sh

# Runs once every few minutes, forcing update if the force.txt file has been created by a restart or a credential update

# Make this work on mac and on the raspberry pi. Not sure why/if it needs the absolute path, but don't want to mess with it.
if [ -x "/usr/bin/python" ]; then
  PYTH="/usr/bin/python"
else
  PYTH="python"
fi

if [ -f /tmp/force.txt ]; then
  # Force re-render of the image
  rm -rf /tmp/force.txt
  echo "Executing main with --force"
  "$PYTH" main.py --force >> log.txt
fi
