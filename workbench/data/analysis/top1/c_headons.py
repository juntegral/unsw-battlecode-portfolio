#!/usr/bin/env python3
"""c_headons.py: for the games given, print the first head-on collisions recorded in q/<id>.json, with the two sides.

usage: python3 c_headons.py <game_id> [<game_id> ...]
A q record is [round, rammer side, rammer id, rammer length, steps used, steps required, victim side, victim id, victim length, ...].
Prints the first record of any kind, the first one between two teams, and the counts of each kind up to round 150 and over the game.
"""
import json
import sys

for gid in sys.argv[1:]:
    q = json.load(open(f"q/{gid}.json"))
    hs = q["headons"]
    cross = [h for h in hs if h[1] != h[6]]
    same = [h for h in hs if h[1] == h[6]]
    print(f"{gid}: records {len(hs)}, between the teams {len(cross)}, inside one team {len(same)}; "
          f"up to r150: between {sum(1 for h in cross if h[0] <= 150)}, inside {sum(1 for h in same if h[0] <= 150)}")
    print("   first of any kind:", hs[0][:9] if hs else None)
    print("   first between the teams:", cross[0][:9] if cross else None)
