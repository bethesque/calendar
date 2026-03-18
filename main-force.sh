#!/bin/sh -e

# Runs once every few minutes, forcing update if the force.txt file has been created by a restart or a credential update
if [ -f /tmp/force.txt ]; then
  # Force re-render of the image
  rm -rf /tmp/force.txt

  # Make this work on mac and on the raspberry pi.
  if [ -x "/usr/bin/python" ]; then
    PYTH="/usr/bin/python"
  else
    PYTH="python"
  fi

  echo "Executing main with --force"
  "$PYTH" main.py --force >> log.txt
fi
