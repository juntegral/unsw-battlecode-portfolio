#!/usr/bin/env python3
"""c_endstate.py [team_id=1119]: how the team's games end, by map: is a loss an economy loss?

For the team's games against 2000+ opponents (Schooltime left out), per map and per map size:
  games, wins; losses by end type (wipe-out / queen rule / longest / total);
  losses in which the team's total length was at least the opponent's at round 300, at round 400 and at the end
  (total length per round from q/<id>.json; the end from games.csv);
  losses in which the team had at least as many units at the end;
  means over the losses that went to round 500: final units, total length, longest dragon, queen length, own / opponent.
A loss with the larger total length at the end is not lost by the economy as this file measures it.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

team = int(sys.argv[1]) if len(sys.argv) > 1 else 1119
rows = defaultdict(list)
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        if int(g[f"team{s}Id"]) != team:
            continue
        o = "B" if s == "A" else "A"
        try:
            if float(g[f"team{o}Elo"]) < 2000:
                continue
        except ValueError:
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        q = json.load(open(f"q/{g['game_id']}.json"))
        ta, tb = q["sides"][s]["per"]["total"], q["sides"][o]["per"]["total"]
        ua, ub = q["sides"][s]["per"]["units"], q["sides"][o]["per"]["units"]

        def at(v, r):
            return v[r] if r < len(v) else None

        rec = dict(gid=g["game_id"], won=g["winner"] == s, end=g["end_type"], rounds=int(g["rounds"]),
                   fu=(int(g[f"final_units_{s}"]), int(g[f"final_units_{o}"])),
                   ft=(int(g[f"final_total_length_{s}"]), int(g[f"final_total_length_{o}"])),
                   fl=(int(g[f"final_longest_length_{s}"]), int(g[f"final_longest_length_{o}"])),
                   fq=(int(g[f"final_queen_length_{s}"]), int(g[f"final_queen_length_{o}"])),
                   t300=(at(ta, 300), at(tb, 300)), t400=(at(ta, 400), at(tb, 400)),
                   u300=(at(ua, 300), at(ub, 300)), opp=int(g[f"team{o}Id"]))
        rows[(size, g["map"])].append(rec)
        rows[(size, "ALL " + size)].append(rec)

print(f"=== END STATE team {team}: games against 2000+ teams, Schooltime left out")
print("size map | games, won | losses: wipe-out / queen rule / longest / total | losses that reached round 300 with own total length >= opponent's at r300 (of those that reached it) | "
      "the same at r400 | losses at round 500 with own total >= opponent's at the end (of round-500 losses) | with own units >= opponent's at the end | "
      "round-500 losses, means own / opponent: units, total length, longest, queen length | "
      "wins that reached round 300 with own total length < opponent's at r300 (of those that reached it); wins by end type wipe-out / queen rule / longest")
order = {"large": 0, "medium": 1, "small": 2}
for key in sorted(rows, key=lambda k: (order[k[0]], k[1].startswith("ALL"), k[1])):
    rs = rows[key]
    lost = [r for r in rs if not r["won"]]
    ends = Counter(r["end"] for r in lost)
    l300 = [r for r in lost if r["t300"][0] is not None and r["t300"][1] is not None]
    l400 = [r for r in lost if r["t400"][0] is not None and r["t400"][1] is not None]
    l500 = [r for r in lost if r["rounds"] == 500 and r["end"] != "wipe-out"]
    n5 = max(1, len(l500))
    won = [r for r in rs if r["won"]]
    wends = Counter(r["end"] for r in won)
    w300 = [r for r in won if r["t300"][0] is not None and r["t300"][1] is not None]

    def mean(f):
        return sum(f(r) for r in l500) / n5

    print(f"{key[0]:6s} {key[1]:18s} | {len(rs):3d}, {sum(r['won'] for r in rs):3d} | {ends['wipe-out']:3d} / {ends['queen rule']:3d} / {ends['longest']:3d} / {ends['total']:2d} | "
          f"{sum(1 for r in l300 if r['t300'][0] >= r['t300'][1]):3d} of {len(l300):3d} | {sum(1 for r in l400 if r['t400'][0] >= r['t400'][1]):3d} of {len(l400):3d} | "
          f"{sum(1 for r in l500 if r['ft'][0] >= r['ft'][1]):3d} of {len(l500):3d} | {sum(1 for r in l500 if r['fu'][0] >= r['fu'][1]):3d} | "
          f"units {mean(lambda r: r['fu'][0]):4.1f} / {mean(lambda r: r['fu'][1]):4.1f}, total {mean(lambda r: r['ft'][0]):5.1f} / {mean(lambda r: r['ft'][1]):5.1f}, "
          f"longest {mean(lambda r: r['fl'][0]):4.1f} / {mean(lambda r: r['fl'][1]):4.1f}, queen {mean(lambda r: r['fq'][0]):4.1f} / {mean(lambda r: r['fq'][1]):4.1f} | "
          f"wins from behind {sum(1 for r in w300 if r['t300'][0] < r['t300'][1]):3d} of {len(w300):3d}; wins {wends['wipe-out']} / {wends['queen rule']} / {wends['longest']}")
if "--games" in sys.argv:
    print()
    print("losses at round 500 with own total length >= the opponent's at the end: map, game id, opponent id, end type, units, total, longest, queen (own / opponent)")
    for key in sorted(rows, key=lambda k: (order[k[0]], k[1])):
        if key[1].startswith("ALL"):
            continue
        for r in rows[key]:
            if not r["won"] and r["rounds"] == 500 and r["end"] != "wipe-out" and r["ft"][0] >= r["ft"][1]:
                print(f"  {key[1]:16s} {r['gid']} opp {r['opp']:4d} {r['end']:10s} units {r['fu'][0]} / {r['fu'][1]}, total {r['ft'][0]} / {r['ft'][1]}, "
                      f"longest {r['fl'][0]} / {r['fl'][1]}, queen {r['fq'][0]} / {r['fq'][1]}")
