#!/usr/bin/env python3
"""d_f.py: found and survived (sub-session A4, question f).  Reads d_out/life/*.json, q/*.json, games.csv.

1. Seen episodes.  An episode = consecutive rounds (gaps of up to two rounds joined) with an enemy head inside the
   queen's 7x7 view.  Per group: queens that were ever seen, episodes per game and per 100 queen-rounds, rounds per
   episode, share that ended with her rammed (during it or within two rounds), dead another way, alive; the same
   for episodes in which an enemy head came within 3 path steps.
2. Small intruders.  From q/*.json `episodes` (an enemy head came within 6 path steps of the living queen; closed
   when it is more than 9 away or dead).  Kept: intruders 4 or shorter that came within 4 steps.  Outcome: it
   rammed the queen / it rammed another dragon of her team / a defender rammed it / the queen rammed it / it died
   another way / it left / the queen died of something else / game end.
3. Circling.  A queen is "on a loop" in a round if her head used 4 or fewer different cells in the 12 rounds ending
   there (a 2x2 loop has period 4), and "on a small patch" with 8 or fewer in 16 rounds.  Per group: share of
   queen-rounds on a loop / small patch, queens with a loop of 20+ rounds, and what happened to loop-mode queens
   when an enemy head came into view: rounds seen while on a loop, rammed within 3 rounds.
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
GROUPS = ["meow", "meow live", "meow live rules on", "meow live rules off", "opp", "opp test4", "opp WHQ", "forgot", "SSS", "Vibing++"]


def main():
    ep = defaultdict(Counter)
    intr = defaultdict(Counter)
    loop = defaultdict(Counter)
    loops_list = []
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        p = os.path.join(HERE, "d_out", "life", g["game_id"] + ".json")
        if not os.path.exists(p):
            continue
        life = q = None
        for s in "AB":
            o = "B" if s == "A" else "A"
            team, opp = g[f"team{s}Id"], g[f"team{o}Id"]
            elo_o, elo_s = float(g[f"team{o}Elo"] or 0), float(g[f"team{s}Elo"] or 0)
            groups = []
            if team in TOP and elo_o >= 2000:
                groups.append(TOP[team])
            if team == "1119" and elo_o >= 2000:
                groups.append("meow")
                if g["battle_id"] in LIVE:
                    groups += ["meow live", "meow live rules on" if int(g["cells"]) > 600 else "meow live rules off"]
            if opp == "1119" and elo_s >= 2000:
                groups.append("opp")
                if team == "19":
                    groups.append("opp test4")
                if team == "87":
                    groups.append("opp WHQ")
            if not groups:
                continue
            if life is None:
                life = json.load(open(p))
                q = json.load(open(os.path.join(HERE, "q", g["game_id"] + ".json")))
            ls, qs = life["sides"][s], q["sides"][s]
            pos, qlen = ls["pos"], ls["qlen"]
            alive_rounds = sum(1 for c in pos if c)
            qd = ls["qdeath"]
            seen_rounds = {}
            for a, b, n, mind, L, oc in ls["seen"]:
                for r in range(a, b + 1):
                    seen_rounds[r] = oc
            # loop detection
            on_loop = [False] * len(pos)
            on_patch = [False] * len(pos)
            for r in range(len(pos)):
                if not pos[r]:
                    continue
                if r >= 11 and all(pos[r - 11:r + 1]):
                    on_loop[r] = len({tuple(c) for c in pos[r - 11:r + 1]}) <= 4
                if r >= 15 and all(pos[r - 15:r + 1]):
                    on_patch[r] = len({tuple(c) for c in pos[r - 15:r + 1]}) <= 8
            run = best = 0
            for v in on_loop:
                run = run + 1 if v else 0
                best = max(best, run)
            seen_on_loop = sum(1 for r in seen_rounds if r < len(on_loop) and on_loop[r])
            ram_on_loop = bool(qd and qd[1] == "rammed" and any(on_loop[max(0, qd[0] - 3):qd[0] + 1]))
            if best >= 20:
                loops_list.append((g["game_id"], g["map"], s, g[f"team{s}Name"][:12], best, sum(on_loop), seen_on_loop, qd))
            for grp in groups:
                c = ep[grp]
                c["games"] += 1
                c["rounds"] += alive_rounds
                c["ever seen"] += bool(ls["seen"])
                c["alive at end"] += qd is None
                c["ever seen and alive at end"] += bool(ls["seen"]) and qd is None
                c["never seen"] += not ls["seen"]
                c["never seen and alive at end"] += (not ls["seen"]) and qd is None
                for a, b, n, mind, L, oc in ls["seen"]:
                    c["episodes"] += 1
                    c["episode rounds"] += b - a + 1
                    c["ep " + oc] += 1
                    if mind <= 3:
                        c["close episodes"] += 1
                        c["close " + oc] += 1
                    if L <= 3:
                        c["episodes L2-3"] += 1
                        c["L2-3 " + oc] += 1
                for e in qs["episodes"]:
                    if e["len"] <= 4 and e["min"] <= 4:
                        i = intr[grp]
                        i["n"] += 1
                        oc = e["outcome"]
                        if oc == "it_rammed":
                            oc = "it rammed the queen" if e.get("victim_queen") else "it rammed another of her dragons"
                        elif oc.startswith("died_"):
                            oc = "it died another way"
                        i[oc] += 1
                        if (e.get("a6") or 0) >= 3:
                            i["n, 3+ own heads within 6"] += 1
                            i["3+: " + oc] += 1
                lp = loop[grp]
                lp["rounds"] += alive_rounds
                lp["loop rounds"] += sum(on_loop)
                lp["patch rounds"] += sum(on_patch)
                lp["queens with a 20+ round loop"] += best >= 20
                lp["queens with a 50+ round loop"] += best >= 50
                lp["loop rounds with an enemy head in view"] += seen_on_loop
                lp["rammed within 3 rounds of being on a loop"] += ram_on_loop
                lp["games"] += 1
    print("=== 1. seen episodes")
    print("group | games | queens ever seen | alive at the end: ever seen / never seen | episodes per game | per 100 queen-rounds | rounds per episode | "
          "ended rammed / dead another way / alive | close episodes (enemy within 3 steps) | of those rammed / dead another way / alive | episodes with her 2-3 long: rammed / other / alive")
    for g in GROUPS:
        c = ep[g]
        if not c["games"]:
            continue
        n = max(1, c["episodes"])
        print(f"{g} | {c['games']} | {c['ever seen']} ({100 * c['ever seen'] // c['games']}%) | {c['ever seen and alive at end']} of {c['ever seen']} / {c['never seen and alive at end']} of {c['never seen']} | "
              f"{c['episodes'] / c['games']:.1f} | {100 * c['episodes'] / c['rounds']:.2f} | {c['episode rounds'] / n:.1f} | "
              f"{100 * c['ep rammed'] / n:.1f}% / {100 * c['ep died'] / n:.1f}% / {100 * c['ep lived'] / n:.1f}% | {c['close episodes']} | "
              f"{100 * c['close rammed'] / max(1, c['close episodes']):.0f}% / {100 * c['close died'] / max(1, c['close episodes']):.0f}% / {100 * c['close lived'] / max(1, c['close episodes']):.0f}% | "
              f"{c['L2-3 rammed']} / {c['L2-3 died']} / {c['L2-3 lived']} of {c['episodes L2-3']}")
    print("\n=== 2. small intruders (4 or shorter, came within 4 path steps of the living queen)")
    keys = ["it rammed the queen", "it rammed another of her dragons", "rammed_by_defender", "rammed_by_queen", "it died another way", "left", "queen_dead", "game_end"]
    print("group | intruders | per game | " + " | ".join(keys) + " | with 3+ own heads within 6 steps: n, rammed the queen, rammed by a defender")
    for g in GROUPS:
        i = intr[g]
        if not i["n"]:
            continue
        print(f"{g} | {i['n']} | {i['n'] / ep[g]['games']:.1f} | " + " | ".join(f"{i[k]} ({100 * i[k] / i['n']:.1f}%)" for k in keys)
              + f" | {i['n, 3+ own heads within 6']}, {100 * i['3+: it rammed the queen'] / max(1, i['n, 3+ own heads within 6']):.1f}%, {100 * i['3+: rammed_by_defender'] / max(1, i['n, 3+ own heads within 6']):.1f}%")
    print("\n=== 3. circling")
    print("group | queen-rounds | on a loop (4 or fewer cells in 12 rounds) | on a small patch (8 or fewer cells in 16 rounds) | queens with a loop of 20+ rounds | of 50+ rounds | "
          "loop rounds with an enemy head in view | queens rammed within 3 rounds of being on a loop")
    for g in GROUPS:
        lp = loop[g]
        if not lp["rounds"]:
            continue
        print(f"{g} | {lp['rounds']} | {100 * lp['loop rounds'] / lp['rounds']:.1f}% | {100 * lp['patch rounds'] / lp['rounds']:.1f}% | {lp['queens with a 20+ round loop']} of {lp['games']} | "
              f"{lp['queens with a 50+ round loop']} | {lp['loop rounds with an enemy head in view']} | {lp['rammed within 3 rounds of being on a loop']}")
    print("\nqueens with a loop of 20+ rounds: game, map, side, team, longest loop run, loop rounds, loop rounds with an enemy head in view, queen death")
    by_team = Counter(x[3] for x in loops_list)
    print("  by team:", dict(by_team.most_common(12)))
    for x in sorted(loops_list, key=lambda x: -x[4])[:40]:
        print("  ", *x)


if __name__ == "__main__":
    main()
