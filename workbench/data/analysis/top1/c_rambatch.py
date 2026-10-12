#!/usr/bin/env python3
"""c_rambatch.py [jsonl=c_out/ramlocal_1119_large.jsonl]: the ram-pearl counts of c_ramlocal.py split by bot build.

c_ramlocal.py keeps one JSON line per game with every ram between the two teams (who started it, heads of each team
within 8 path steps, and for every pearl of the two corpses who ate it and after how many rounds). This script
re-adds those lines for two groups of games: the runs of the test build with TRADE_CONTACT (battle ids tc30-test-new
and tc30-dev1b-new) and all other runs. No replay is walked.

Per group: games; rams per game and the share the team started; pearls dropped; eaten within 20 rounds by the team /
by the enemy; the same when the team started the ram and when the enemy did; by local head balance (own heads within
8 steps minus enemy heads within 8 steps); and the share of rams that happen in the team's own half is NOT here (see
c_front.py).
"""
import csv
import json
import sys
from collections import Counter, defaultdict

path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "c_out/ramlocal_1119_large.jsonl"
BATTLE = {g["game_id"]: g["battle_id"] for g in csv.DictReader(open("games.csv"))}
TC = ("tc30-test-new", "tc30-dev1b-new")
LOOK = 20
agg = defaultdict(Counter)
games = Counter()
for line in open(path):
    rec = json.loads(line)
    grp = "TRADE_CONTACT runs" if BATTLE.get(rec["gid"], "") in TC else "all other runs"
    games[grp] += 1
    s = rec["side"]
    o = "B" if s == "A" else "A"
    for ram in rec["rams"]:
        bal = ram[s + "8"] - ram[o + "8"]
        bcls = "<=-3" if bal <= -3 else "-2..-1" if bal < 0 else "0" if bal == 0 else "+1..+2" if bal <= 2 else ">=+3"
        role = "we rammed" if ram["rside"] == s else "we were rammed"
        ph = "r0-149" if ram["round"] < 150 else "r150+"
        for key in (("all", ""), ("role", role), ("balance", bcls), ("phase", ph), ("role+phase", role + " " + ph)):
            a = agg[(grp,) + key]
            a["rams"] += 1
            for cside, eater, wait in ram["pearls"]:
                a["pearls"] += 1
                if eater is None or wait > LOOK:
                    a["left"] += 1
                elif eater == s:
                    a["own"] += 1
                else:
                    a["en"] += 1
print(f"=== RAM PEARLS BY BUILD from {path}")
print("group | split | rams (per game) | pearls dropped | eaten within 20 rounds by the team % / by the enemy % / not eaten %")
bord = {"<=-3": 0, "-2..-1": 1, "0": 2, "+1..+2": 3, ">=+3": 4}
for grp in ("all other runs", "TRADE_CONTACT runs"):
    n = max(1, games[grp])
    print(f"{grp}: {games[grp]} games")
    for key in sorted((k for k in agg if k[0] == grp), key=lambda k: (["all", "role", "phase", "role+phase", "balance"].index(k[1]), bord.get(k[2], 0), k[2])):
        a = agg[key]
        p = max(1, a["pearls"])
        print(f"   {key[1]:10s} {key[2]:24s} | {a['rams']:5d} ({a['rams'] / n:5.1f}) | {a['pearls']:5d} | "
              f"team {100 * a['own'] / p:3.0f}% / enemy {100 * a['en'] / p:3.0f}% / left {100 * a['left'] / p:3.0f}%")
