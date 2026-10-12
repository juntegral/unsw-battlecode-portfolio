#!/usr/bin/env python3
"""d_games.py: the table of games read closely, generated from the classification (sub-session A4, report section 3).

Writes d_out/md_games.md: one row per game read (our 40 games, then the top-team games read next to them), with
map, cells, run, our side's start cell, opponent, result, the kind of our queen's end and its round, and the same
for the opponent's queen in that game.
"""
import json
import os

import d_tab

HERE = os.path.dirname(os.path.abspath(__file__))
OURS = ["980372", "1053773", "1045200", "1053020", "1044202", "1052762", "1063018",
        "1023823", "1045382", "1052754", "1045377", "1044201",
        "1052760", "1044510", "1053021", "1052761", "1053778", "1027975",
        "1045195", "1052766", "1053379", "1045388",
        "1053032", "1045387", "1045380", "1044207", "1053380", "1045196", "990346",
        "1023828", "1044208", "1045203", "1023830",
        "1053777", "1053772", "993428",
        "1045201", "1044521", "1044205", "1045381"]
TOPS = [("1046537", "B"), ("1055129", "B"), ("1054798", "B"), ("1046528", "B"), ("1046526", "B"), ("1051826", "A"), ("1046534", "B"),
        ("1046539", "B"), ("1046535", "B"), ("1054786", "B"), ("1046991", "A"), ("1054774", "B"), ("1051825", "A"), ("1062234", "A"),
        ("1046531", "B"), ("1046988", "A"), ("1064308", "A"), ("1046541", "B")]
SHORT = {"ram: stepped in": "rammed: stepped in", "ram: stayed in": "rammed: stayed in", "ram: cornered": "rammed: cornered",
         "ram: unseen": "rammed: unseen", "boxed: terrain dead end": "boxed in: terrain dead end", "boxed: ally body": "boxed in by a team-mate",
         "boxed: enemy body": "boxed in by an enemy body", "boxed: ally+enemy": "boxed in by both", "own ram": "own ram", "alive": "alive"}


def fate(x):
    if x["kind"] == "alive":
        d = json.load(open(os.path.join(HERE, "q", x["gid"] + ".json")))
        return f"alive, {d['sides'][x['side']]['final']['queen']} long"
    return f"{SHORT.get(x['kind'], x['kind'])}, round {x['det']['r']}, {x['det']['len']} long"


def result(x):
    return ("won" if x["won"] else "lost") + (" by wipe-out" if x["end"] == "wipe-out" else f" at round 500 ({x['end']})")


def main():
    recs = d_tab.load()
    idx = {}
    for x in recs:
        idx.setdefault((x["gid"], x["side"]), x)
    out = ["| # | game | map (cells) | run | our start | opponent | result | our queen | the opponent's queen in the same game |", "|---|---|---|---|---|---|---|---|---|"]
    for i, gid in enumerate(OURS, 1):
        me = [x for (g, s), x in idx.items() if g == gid and "meow" in x["groups"]][0]
        o = "B" if me["side"] == "A" else "A"
        him = idx.get((gid, o))
        run = me["run"].replace("-test", "")
        out.append(f"| {i} | {gid} | {me['map']} ({me['cells']}) | {run} | {tuple(me['sd']['start'])} | {me['opp'][:14]} | {result(me)} | {fate(me)} | {fate(him) if him else '-'} |")
    out.append("")
    out.append("| # | game | map (cells) | team read | its start | opponent | result | its queen |")
    out.append("|---|---|---|---|---|---|---|---|")
    for i, (gid, s) in enumerate(TOPS, 1):
        x = idx[(gid, s)]
        team = [g for g in x["groups"] if g in ("SSS", "forgot", "Vibing++")][0]
        out.append(f"| T{i} | {gid} | {x['map']} ({x['cells']}) | {team} | {tuple(x['sd']['start'])} | {x['opp'][:14]} | {result(x)} | {fate(x)} |")
    open(os.path.join(HERE, "d_out", "md_games.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
