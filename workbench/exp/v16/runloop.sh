#!/bin/sh
# Keep a resumable queue (exp/v16/runq.js) running until it reports "all done"; log every exit (a killed node restarts and skips finished keys).
# usage: sh exp/v16/runloop.sh <spec.json> <log>
cd "$(dirname "$0")/../.."
while ! grep -q "all done" "$2" 2>/dev/null; do
  node exp/v16/runq.js "$1" --jobs 3 --cap 6 >> "$2" 2>&1
  echo "$(date +%H:%M:%S) runq exited with $?" >> "$2"
  sleep 5
done
