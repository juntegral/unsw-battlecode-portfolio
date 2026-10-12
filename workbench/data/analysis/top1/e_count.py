#!/usr/bin/env python3
"""How many games are in each study group (read from games.csv only)."""
from collections import Counter

import e_lib as E

gs = E.load_games()
st = E.study_games()
c = Counter()
for g in st:
    for s in "AB":
        if E.in_study(g, s) and g[s] in (E.ME,) + E.TOP3:
            c[E.NAMES[g[s]]] += 1
            if g[s] == E.ME:
                c["meow " + E.build(g)] += 1
                c["meow vs " + E.NAMES.get(g[E.other(s)], "other")] += 1
                c["meow set " + g["set"]] += 1
print("games.csv:", len(gs), "| study games (distinct):", len(st))
for k, v in sorted(c.items()):
    print("  %-40s %d" % (k, v))
