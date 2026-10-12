#!/usr/bin/env python3
"""c_qa.py: question a for the games of ours that were read: when does the gap open, and what happened just before?

For each of our games in the list: first round with heads in view of each other (from the c_econ.py JSON), round of the
first ram, the first round from which own units / enemy units stays below 0.8 until the end ("for good"), the same for
total length (both from q/<id>.json), and, for the 20 rounds before the unit round (or before the total-length round
when the units never fall behind for good): units own / enemy at the start of those 20 rounds, natural pearls eaten,
corpse pearls eaten, splits, own dragons rammed / ramming / boxed / other, and the same for the enemy.
Prints a markdown table.
"""
import csv
import json
import os

OURS = ["1058144", "1067904", "1068050", "1021860", "1063012", "1067905", "1068051", "1063671", "1063016", "1068055", "1067909", "1063675",
        "1063252", "1067917", "1068063", "1063024", "1067915", "1068061", "1063774", "1067906", "1068052", "1063672",
        "1067908", "1068054", "1067907", "1068053", "1059076", "1063682", "1063251", "1067916"]
GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}


def for_good(a, b, thr=0.8):
    n = min(len(a), len(b))
    last = None
    for t in range(n - 1, -1, -1):
        if b[t] > 0 and a[t] / b[t] < thr:
            last = t
        else:
            break
    return last


print("| game | map | opponent | result | heads first in view | first ram | units behind for good from | total length behind for good from | the 20 rounds before: units, own / enemy | natural eaten | corpse eaten | splits | own dragons rammed, ramming, boxed, other | enemy dragons rammed, ramming, boxed, other |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for gid in OURS:
    g = GAMES[gid]
    q = json.load(open(f"q/{gid}.json"))
    s, o = "A", "B"
    ua, ub = q["sides"][s]["per"]["units"], q["sides"][o]["per"]["units"]
    ta, tb = q["sides"][s]["per"]["total"], q["sides"][o]["per"]["total"]
    fu, ft = for_good(ua, ub), for_good(ta, tb)
    cross = [h for h in q["headons"] if h[1] != h[6]]   # head-ons inside one team are not rams
    ram = cross[0][0] if cross else None
    d = json.load(open(f"c_out/ec_{gid}_0_150.json"))
    blocks = {int(r): row for r, row in d["blocks"].items()}
    p2 = f"c_out/ec_{gid}_150_350.json"
    if os.path.exists(p2):
        for r, row in json.load(open(p2))["blocks"].items():
            if int(r) >= 150:
                blocks[int(r)] = row
    ref = fu if fu is not None else ft
    cells = ["-"] * 6
    if ref is not None and ref >= 0:
        b1 = max(0, (ref // 10) * 10 - 20)
        rs = [r for r in (b1, b1 + 10) if r in blocks]
        if rs:
            def tot(side, k):
                return sum(blocks[r][side].get(k, 0) for r in rs)
            first = blocks[rs[0]]
            cells = [f"r{b1}-{b1 + 19}: {first[s]['units']} / {first[o]['units']}", f"{tot(s, 'nat')} / {tot(o, 'nat')}",
                     f"{tot(s, 'corpse_own') + tot(s, 'corpse_enemy')} / {tot(o, 'corpse_own') + tot(o, 'corpse_enemy')}",
                     f"{tot(s, 'split')} / {tot(o, 'split')}",
                     f"{tot(s, 'rammed')}, {tot(s, 'rammer')}, {tot(s, 'boxed')}, {tot(s, 'freedeath')}",
                     f"{tot(o, 'rammed')}, {tot(o, 'rammer')}, {tot(o, 'boxed')}, {tot(o, 'freedeath')}"]
    opp = {19: "test4", 87: "WHQ"}.get(int(g["teamBId"]), g["teamBName"][:14])
    res = "win" if g["winner"] == s else "loss"
    fmt = lambda x: "never" if x is None else f"r{x}"  # noqa: E731
    fc = "after r150" if d["first_contact"] is None else f"r{d['first_contact']}"
    print(f"| {gid} | {g['map']} | {opp} | {res} | {fc} | {'none' if ram is None else f'r{ram}'} | {fmt(fu)} | {fmt(ft)} | " + " | ".join(cells) + " |")
