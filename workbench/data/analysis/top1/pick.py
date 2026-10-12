#!/usr/bin/env python3
"""Candidate games for the close read: protagonist (306) games with a short tag line each. Reads q/*.json."""
import glob
import json
import sys

TEAM = int(sys.argv[1]) if len(sys.argv) > 1 else 306
rows = []
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != TEAM or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        me, op = d["sides"][s], d["sides"][o]
        qd, oqd = me["qdeath"], op["qdeath"]

        def fate(x):
            if not x:
                return "alive"
            k = x["killer"]
            return f"r{x['round']} {x['reason']}" + (f" by L{k['len']} {k['steps_used']}st" if k and k["team"] != None else "")
        c = d["w"] * d["h"]
        rows.append((("small" if c <= 700 else "medium" if c <= 1500 else "large"), d["map"], d["game_id"], s,
                     "W" if d["winner"] == s else "L", d["end_type"], op["name"][:12], int(op["elo"]),
                     f"final own {me['final']['units']}u/{me['final']['total']}t/{me['final']['longest']}L/q{me['final']['queen']}",
                     f"opp {op['final']['units']}u/{op['final']['total']}t/{op['final']['longest']}L/q{op['final']['queen']}",
                     "ownQ " + fate(qd), "oppQ " + fate(oqd), d["rounds"]))
rows.sort()
for r in rows:
    print(" | ".join(str(x) for x in r))
