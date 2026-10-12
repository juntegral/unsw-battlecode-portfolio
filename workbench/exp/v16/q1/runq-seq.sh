#!/bin/sh
# the v1.8 re-run (Q1.md §13): the 22-map sets first, then maps/generated (one runner at a time; exp/v16/q1/runq.js resumes finished keys)
cd "$(dirname "$0")/../../.." || exit 1
node exp/v16/q1/runq.js exp/v16/q1/spec-q18a.json --jobs 3 --cap 6 >> exp/v16/q1/runq-q18.log 2>&1
node exp/v16/q1/runq.js exp/v16/q1/spec-q18b.json --jobs 3 --cap 6 >> exp/v16/q1/runq-q18.log 2>&1
echo "$(date +%H:%M:%S) both specs done" >> exp/v16/q1/runq-q18.log
