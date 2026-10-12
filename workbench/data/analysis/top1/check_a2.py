#!/usr/bin/env python3
"""Lead's recount of four all-games claims made by sub-session A2 (opp elo >= 2000, Schooltime excluded)."""
import glob
import json
from collections import defaultdict

TEAMS = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
cuts = defaultdict(lambda: [0, 0, 0])
ch = defaultdict(lambda: [0, 0])
dead100 = defaultdict(lambda: [0, 0])
both = defaultdict(lambda: [0, 0])
q8 = defaultdict(lambda: [0, 0])
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] == "Schooltime":
        continue
    c = d["w"] * d["h"]
    sz = "small" if c <= 700 else "medium" if c <= 1500 else "large"
    d3 = None
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        if t not in TEAMS or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        name = TEAMS[t]
        sd = d["sides"][s]
        n = sum(1 for r, before, plen, clen in sd["qsplits"] if before >= 8 and plen <= 3)
        cuts[name][0] += n
        cuts[name][1] += n > 0
        cuts[name][2] += 1
        if d3 is None:
            d3 = json.load(open(f"q3v2/{d['game_id']}.json"))
        for x in d3["chances"]:
            if x[1] == s and x[9] and x[3] <= 3:
                k = (name, "r<100" if x[0] < 100 else "r100+")
                ch[k][0] += 1
                ch[k][1] += x[5]
        qd = sd["qdeath"]
        dead100[(name, sz)][0] += 1
        dead100[(name, sz)][1] += bool(qd and qd["round"] < 100)
        if d["end_type"] != "wipe-out" and sd["final"]["queen"] and d["sides"][o]["final"]["queen"]:
            both[name][0] += 1
            both[name][1] += d["winner"] == s
        q = sd["per"]["q"]
        if d["end_type"] != "wipe-out" and len(q) > 300 and q[300]:
            q8[name][0] += 1
            q8[name][1] += any(x and x[2] >= 8 for x in q[:301])
for name in TEAMS.values():
    print(name, "| queen cuts (8+ -> 2-3):", cuts[name][0], "in", cuts[name][1], "of", cuts[name][2], "games",
          "| in-view chances of 2-3-long taken r<100:", ch[(name, 'r<100')][1], "/", ch[(name, 'r<100')][0],
          " r100+:", ch[(name, 'r100+')][1], "/", ch[(name, 'r100+')][0],
          "| queen dead before r100 large/medium/small:",
          " ".join(f"{dead100[(name, z)][1]}/{dead100[(name, z)][0]}" for z in ("large", "medium", "small")),
          "| both queens alive at r500, won:", both[name][1], "/", both[name][0],
          "| r500 games with queen alive at r300: 8+ long by r300:", q8[name][1], "/", q8[name][0])
