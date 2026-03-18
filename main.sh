#!/bin/sh

# Make this work on mac and on the raspberry pi. Not sure why/if it needs the absolute path, but don't want to mess with it.
if [[ -x "/usr/bin/python" ]]; then
    echo "/usr/bin/python exists and is executable."
    PYTH="/usr/bin/python"
else
    echo "/usr/bin/python is not executable or does not exist. Using python on path."
    PYTH="python"
fi

if [[ -f /tmp/force.txt ]]; then
	# Force re-render of the image
	rm -rf /tmp/force.txt
	echo "Executing main with --force"
	"$PYTH" main.py --force >> log.txt
else
	echo "Executing main"
	# Allow use of cached image
	"$PYTH" main.py >> log.txt
fi
