#!/usr/bin/env python3
"""Peek at raw replay events of one game: counts per event kind, sample dragon logs, sample sonar pings.
Usage: python3 e_peek.py <game_id> [log_substring]
Read-only. Output to stdout."""
import csv
import sys
from collections import Counter

sys.dont_write_bytecode = True
sys.path.insert(0, "~/01. Project/개인 프로젝트/battlecode")
import replay as rp  # noqa: E402

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else None
g = GAMES[gid]
root = rp.load(g["replay_path"]).root()
cnt = Counter()
logs = Counter()
shown = 0
rnd = -1
son = 0
for ev in root.pointer(3):
    k = ev.u16(0)
    cnt[rp.EVENT_NAMES[k] if k < len(rp.EVENT_NAMES) else str(k)] += 1
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
    elif k in (5, 6):
        t = p.text(0) if k == 6 else (p.text(0) if p is not None else "")
        key = t.split()[0] if t.split() else ""
        logs[(k, key)] += 1
        if (want is None and shown < 15) or (want and want in t and shown < 60):
            print("r%d kind %d id %s: %s" % (rnd, k, p.i32(0) if k == 6 else "-", t[:200]))
            shown += 1
    elif k == 12 and son < 6:
        son += 1
        print("r%d sonar: dwords %d pwords %d sender %d words %s" % (
            rnd, p.dwords, p.pwords, p.i32(0), [hex(p.u64(8 * i)) for i in range(p.dwords)]))
print(g["map"], g["teamAName"], "vs", g["teamBName"], "winner", g["winner"], g["end_type"], g["battle_id"])
print(dict(cnt))
print("log keys:", logs.most_common(20))
