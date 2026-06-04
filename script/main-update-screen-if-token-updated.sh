#!/bin/bash
# Run from project root

set -Eeuo pipefail

# Force sceen update if the token file has been updated more recently than the calendar was last rendered.
if [ -f token.json ] && { [ ! -f ecalendar-last-render.json ] || [ token.json -nt ecalendar-last-render.json ]; }; then
  touch ecalendar-last-render.json

  # Make this work on mac and on the raspberry pi.
  if [ -x "/usr/bin/python" ]; then
    PYTH="/usr/bin/python"
  else
    PYTH="python"
  fi

  echo "Executing main with --force"
  timeout --kill-after=30s 600 "$PYTH" main.py --force
else
  echo "calendar rendered more recently than tokens fetched"
fi
