#!/bin/bash
# Run from project root

set -Eeuo pipefail

# Force sceen update if the token file has been updated more recently than the calendar was last rendered.
if [ -f token.json ] && { [ ! -f ecalendar-last-render.json ] || [ token.json -nt ecalendar-last-render.json ]; }; then
  touch ecalendar-last-render.json

  if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
  fi

  echo "Executing main with --force"
  timeout --kill-after=30s 600 python main.py --force
else
  echo "calendar rendered more recently than tokens fetched"
fi
