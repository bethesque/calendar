#!/bin/sh

# Runs once an hour, updating the calendar if any events have changed

# Make this work on mac and on the raspberry pi. Not sure why/if it needs the absolute path, but don't want to mess with it.
if [ -x "/usr/bin/python" ]; then
  echo "/usr/bin/python exists and is executable."
  PYTH="/usr/bin/python"
else
  echo "/usr/bin/python is not executable or does not exist. Using python on path."
  PYTH="python"
fi

echo "Executing main"
# Allow use of cached image
"$PYTH" main.py >> log.txt
