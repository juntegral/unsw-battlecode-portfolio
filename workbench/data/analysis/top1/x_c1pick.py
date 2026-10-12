#!/usr/bin/env python3
"""Pick cases of candidate 1 to look at by eye: the first untaken in-view chance of each 'flip' game, a random
sample of other untaken chances of ours, some chances whose path leaves the view. Output: x_out/c1_eye.json"""
import json, random
import x_load as X
random.seed(7)
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME) and X.in_study(g, X.side_of(g, X.ME))]
FLIPS = [990232, 1029017, 1029030, 1053784, 1067909, 1068679, 1044523, 1045197, 1053380, 1063010, 1067904, 1067913, 1068054]
picks = []
pool = []
for g, side in mine:
    ch = [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3 and c.get("dS") is not None]
    un = [c for c in ch if not c["taken"]]
    if g["gid"] in FLIPS and un:
        c = un[0]
        picks.append([g["gid"], c["r"], c["a"], "FLIP game: first untaken chance, attacker L%d, her queen L%d, path %d" % (c["L"], c["qL"], c["dS"])])
    for c in un:
        pool.append((g["gid"], c))
rest = [p for p in pool if p[0] not in FLIPS]
random.shuffle(rest)
seen = set()
for gid, c in rest:
    k = "s" if c["L"] <= 3 else "m" if c["L"] <= 9 else "l"
    if sum(1 for s in seen if s[0] == k) >= 4 or gid in {s[1] for s in seen}:
        continue
    seen.add((k, gid))
    picks.append([gid, c["r"], c["a"], "random untaken: attacker L%d, her queen L%d, path %d, own heads in view %d, enemy heads %d" % (c["L"], c["qL"], c["dS"], c["own_h"], c["en_h"])])
n = 0
for gid, c in pool:
    if c["dV"] is None and n < 3:
        picks.append([gid, c["r"], c["a"], "path leaves the view: attacker L%d, strict path %d" % (c["L"], c["dS"])]); n += 1
json.dump(picks, open("x_out/c1_eye.json", "w"))
print(len(picks))
