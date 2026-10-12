#!/bin/zsh
# One-shot status: Discord and GitHub, the active submission, rank, recent ranked battles, tickets.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 tools/team_watch.py 2>&1 | tail -n 6 | cut -c1-300
date "+%H:%M:%S"
node tools/submit.js active 2>&1 | tail -1 | cut -c1-80
node tools/online.js leaderboard --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print('rank',d['us']['rank'],d['us']['elo'])"
node tools/online.js battles --limit 30 --json 2>/dev/null | python3 -c "
import json,sys
n=0
for b in json.load(sys.stdin):
    if b.get('ranked') and n<10:
        n+=1
        print((b.get('at') or '')[11:16], b['id'], str(b.get('opponent'))[:18], b.get('opponentElo'), b.get('outcome'), ''.join('W' if r=='win' else 'L' if r=='loss' else '.' for r in (b.get('results') or [])), b.get('eloChange'))"
tail -n 1 data/online/smoke/at-q.log | cut -c1-90
