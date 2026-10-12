#!/bin/zsh
# Start the requeue waiter detached.
nohup zsh ~/.claude/jobs/e2109d93/tmp/requeue15.zsh > /dev/null 2>&1 &
sleep 1; pgrep -fl "requeue15" | cut -c1-90
