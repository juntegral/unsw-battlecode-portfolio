#!/usr/bin/env python3
"""c_front.py <ramlocal jsonl> ...: where the rams happen: nearer to the own queen spawn or to the enemy's (wrapped manhattan
distance to the two queen start cells from q/<id>.json). Input: the per-game ram lists written by c_ramlocal.py.
Per file and round phase: rams, share in the own half, share in the enemy half, share started by the own team; the
same split by who started the ram."""
import json
import sys
from collections import Counter


def man(a, b, w, h):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, w - dx) + min(dy, h - dy)


for path in sys.argv[1:]:
    c = Counter()
    for line in open(path):
        d = json.loads(line)
        q = json.load(open(f"q/{d['gid']}.json"))
        w, h = q["w"], q["h"]
        s = d["side"]
        o = "B" if s == "A" else "A"
        so, se = q["sides"][s]["start"], q["sides"][o]["start"]
        for ram in d["rams"]:
            r = ram["round"]
            ph = "r0-49" if r < 50 else "r50-99" if r < 100 else "r100-149" if r < 150 else "r150-199" if r < 200 else "r200-299" if r < 300 else "r300+"
            do, de = man(ram["cell"], so, w, h), man(ram["cell"], se, w, h)
            where = "own" if do < de else "enemy" if de < do else "mid"
            who = "we" if ram["rside"] == s else "they"
            for key in ((ph, "all"), (ph, who), ("all", "all"), ("all", who)):
                c[key + ("n",)] += 1
                c[key + (where,)] += 1
    print(f"=== FRONT {path}: where rams happen (own half = nearer to the own queen's start cell)")
    for ph in ("r0-49", "r50-99", "r100-149", "r150-199", "r200-299", "r300+", "all"):
        parts = []
        for who in ("all", "we", "they"):
            n = max(1, c[(ph, who, "n")])
            parts.append(f"{'all rams' if who == 'all' else 'rams ' + who + ' started'} {c[(ph, who, 'n')]:5d}: own half {100 * c[(ph, who, 'own')] / n:3.0f}%, enemy half {100 * c[(ph, who, 'enemy')] / n:3.0f}%")
        print(f"  {ph:9s} | " + " | ".join(parts))
