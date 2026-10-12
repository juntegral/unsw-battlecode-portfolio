#!/bin/zsh
# One look at everything: restart the narrowed crash check if needed, what the waiter caught, ranked battles, rank, queue, load.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/stress17.zsh" > /dev/null || [ -f $T/stress17.done ] || { nohup zsh $T/stress17.zsh > /dev/null 2>&1 &; }
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
echo "game processes: $(pgrep -f run_game.py | wc -l | tr -d ' ')  codex: $(pgrep -f 'codex exec -m' | wc -l | tr -d ' ')"
python3 tools/team_watch.py 2>&1 | tail -n 4 | cut -c1-260
node tools/submit.js active 2>&1 | tail -1 | cut -c1-60
node tools/online.js leaderboard --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print('rank',d['us']['rank'],d['us']['elo'])"
node tools/online.js battles --limit 12 --json 2>/dev/null | python3 -c "
import json,sys
for b in json.load(sys.stdin)[:7]:
    print((b.get('at') or '')[11:16], b['id'], 'R' if b.get('ranked') else 'u', str(b.get('opponent'))[:18], b.get('opponentElo'), b.get('outcome'), ''.join('W' if r=='win' else 'L' if r=='loss' else '.' for r in (b.get('results') or [])), b.get('eloChange'))"
tail -n 1 data/online/smoke/at-q.log | cut -c1-100
ls data/codex/astra/audit-*/report.md 2>/dev/null | sed 's/.*astra\///' | tr '\n' ' '; echo
cat $T/stress17.txt 2>/dev/null | head -5
