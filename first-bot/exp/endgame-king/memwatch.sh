#!/bin/bash
# Pause the endgame-king extraction, or the process matching the second argument (SIGSTOP), while system-wide free memory is below 10%; resume (SIGCONT) at 12% or more.
# Exits when the extraction runner is gone. Log lines: time, free %, action.
RUNNER_PID=$1
PATTERN=${2:-exp/endgame-king/extract.js}
stopped=0
while kill -0 "$RUNNER_PID" 2>/dev/null; do
  free=$(memory_pressure 2>/dev/null | awk -F': ' '/System-wide memory free percentage/ {gsub("%","",$2); print $2}')
  if [ -n "$free" ]; then
    if [ "$free" -lt 10 ] && [ $stopped -eq 0 ]; then pkill -STOP -f "$PATTERN"; stopped=1; echo "$(date +%H:%M:%S) free ${free}% -> paused"; fi
    if [ "$free" -ge 12 ] && [ $stopped -eq 1 ]; then pkill -CONT -f "$PATTERN"; stopped=0; echo "$(date +%H:%M:%S) free ${free}% -> resumed"; fi
  fi
  sleep 20
done
[ $stopped -eq 1 ] && pkill -CONT -f "$PATTERN"
echo "$(date +%H:%M:%S) runner gone, watch ends"
