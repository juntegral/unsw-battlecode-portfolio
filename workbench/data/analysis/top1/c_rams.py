#!/usr/bin/env python3
"""c_rams.py [size=large]: the ram exchange over all games, from q/<id>.json (no replay walking).

A ram = a head moves into an enemy head; both die. For each team group and phase (per game, means):
  made      rams started by the team; mean length of the rammer (at the start of its turn) and of the victim
  suffered  rams started by the enemy on the team's dragons; mean lengths
  seg       segments lost by the team in all rams (as rammer + as victim) and by the enemy
  pearls    pearls of ram corpses eaten by the team: from enemy corpses / from own corpses; and by the enemy
  swing     change of (own total length - enemy total length) that the rams and their pearls add up to
  share     share of all rams of the game that the team started
Groups: meow, Vibing++, SSS, forgot (opponents rated 2000+, Schooltime left out); test4 and WeHaveQuizzes in their
games against meow and in their games against the top three.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

size_want = sys.argv[1] if len(sys.argv) > 1 else "large"
GAMES = list(csv.DictReader(open("games.csv")))
TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
PH = [(0, 49), (50, 99), (100, 149), (150, 199), (200, 299), (300, 399), (400, 499)]


def phase(r):
    for i, (a, b) in enumerate(PH):
        if a <= r <= b:
            return i
    return len(PH) - 1


acc = defaultdict(lambda: defaultdict(Counter))   # group -> phase -> Counter
ngames = Counter()
for g in GAMES:
    if g["map"] == "Schooltime":
        continue
    size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
    if size != size_want:
        continue
    ids = {s: int(g[f"team{s}Id"]) for s in "AB"}
    groups = {}
    for s in "AB":
        o = "B" if s == "A" else "A"
        t, ot = ids[s], ids[o]
        try:
            oelo = float(g[f"team{o}Elo"])
        except ValueError:
            oelo = 0
        if t in TOP and oelo >= 2000:
            groups[s] = [TOP[t]]
        elif t in (19, 87):
            nm = "test4" if t == 19 else "WeHaveQuizzes"
            if ot == 1119:
                groups[s] = [nm + " vs meow"]
            elif ot in (306, 91, 264):
                groups[s] = [nm + " vs top3"]
    if not groups:
        continue
    q = json.load(open(f"q/{g['game_id']}.json"))
    for s, names in groups.items():
        o = "B" if s == "A" else "A"
        for nm in names:
            ngames[nm] += 1
            a = acc[nm]
            for h in q["headons"]:
                r, rs, rid, rlen, used, req, vs, vid, vlen = h[:9]
                if rs == vs:
                    continue
                p = phase(r)
                if rs == s:
                    a[p]["made"] += 1
                    a[p]["made_rlen"] += rlen
                    a[p]["made_vlen"] += vlen
                    a[p]["made_le"] += rlen <= vlen
                else:
                    a[p]["suf"] += 1
                    a[p]["suf_rlen"] += rlen
                    a[p]["suf_vlen"] += vlen
            for side, pre in ((s, "own"), (o, "opp")):
                for key, v in q["sides"][side]["flow"].items():
                    b, src, kind, role = key.split(":")
                    if kind != "ram":
                        continue
                    r0 = int(b) * 50
                    p = phase(r0)
                    a[p][f"{pre}_eat_{'enemy' if src == 'enemy' else 'own'}"] += v

print(f"=== RAM EXCHANGE, {size_want} maps (per game means)")
print("group (games) phase | made n (rammer len / victim len, share with rammer <= victim) | suffered n (rammer len / victim len) | "
      "segments lost own / enemy | ram-corpse pearls eaten by own team (enemy corpses / own corpses) and by the enemy (our corpses / their corpses) | "
      "swing in total length (rams + pearls) | share of rams started")
for nm in ("meow", "test4 vs meow", "WeHaveQuizzes vs meow", "test4 vs top3", "WeHaveQuizzes vs top3", "forgot", "SSS", "Vibing++"):
    n = ngames[nm]
    if not n:
        continue
    tot = Counter()
    for p in range(len(PH)):
        c = acc[nm][p]
        for k, v in c.items():
            tot[k] += v
    for p in list(range(len(PH))) + ["all"]:
        c = tot if p == "all" else acc[nm][p]
        made, suf = c["made"], c["suf"]
        own_seg = c["made_rlen"] + c["suf_vlen"]
        en_seg = c["made_vlen"] + c["suf_rlen"]
        own_p = c["own_eat_enemy"] + c["own_eat_own"]
        en_p = c["opp_eat_enemy"] + c["opp_eat_own"]
        swing = (en_seg - own_seg + own_p - en_p) / n
        label = "all    " if p == "all" else f"{PH[p][0]:3d}-{PH[p][1]:3d}"
        print(f"{nm:22s} ({n:3d}) r{label} | made {made / n:5.1f} ({c['made_rlen'] / max(1, made):4.1f} / {c['made_vlen'] / max(1, made):4.1f}, {100 * c['made_le'] / max(1, made):3.0f}%) | "
              f"suffered {suf / n:5.1f} ({c['suf_rlen'] / max(1, suf):4.1f} / {c['suf_vlen'] / max(1, suf):4.1f}) | seg {own_seg / n:6.1f} / {en_seg / n:6.1f} | "
              f"pearls own {c['own_eat_enemy'] / n:5.1f} / {c['own_eat_own'] / n:5.1f}  enemy {c['opp_eat_enemy'] / n:5.1f} / {c['opp_eat_own'] / n:5.1f} | "
              f"swing {swing:+6.1f} | {100 * made / max(1, made + suf):3.0f}%")
    print()
