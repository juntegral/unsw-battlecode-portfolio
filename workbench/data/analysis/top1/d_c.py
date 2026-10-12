#!/usr/bin/env python3
"""d_c.py [large|medium|small]: how each queen lives, per 50 rounds, next to her own team (sub-session A4, question c).

Reads d_out/life/*.json (d_life.py), q/*.json (pearls eaten, splits) and games.csv.  Opponents rated 2000+, no
Schooltime.  Groups: meow live bot (all sizes, and rules on / off), meow all runs, the opponent's queen in our games,
forgot, SSS, Vibing++.  With an argument only maps of that size class (small: 700 cells or fewer, medium: up to
1,500, large: over 1,500).

Per 50-round block, per group (queens alive, counted round by round):
  queens      queen-rounds in the block / 50 (so "queens alive on average")
  eat q       natural pearls the queen ate per 100 queen-rounds;  eat team = natural pearls per 100 dragon-rounds of
              the whole team (queen included)
  home q/t    mean path distance from her start cell: queen / the other own heads
  half q/t    share of rounds on the enemy's side (nearer by path to the enemy queen's start): queen / other heads
  seen        share of her rounds with an enemy head in her 7x7 view
  e4 q/t      enemy heads within 4 cells (wrapped manhattan) of her head / of an average other own head
  e8 q/t      the same within 8 cells
  own4        own heads within 4 cells of her head
  len         her mean length;   splits = her splits per 100 queen-rounds
  cells25     distinct cells her head used per 25 rounds (windows in which she was alive throughout)
Second table: the hand-over.  Queen's natural pearls and splits per 100 rounds, and distance from start, by the
number of own dragons at the start of the block, and before / after the first enemy head came into her view.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
GROUPS = ["meow live", "meow live rules on", "meow live rules off", "meow", "opp", "forgot", "SSS", "Vibing++"]
size_arg = sys.argv[1] if len(sys.argv) > 1 else None


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def main():
    acc = defaultdict(lambda: defaultdict(Counter))      # group -> block -> counters
    hand = defaultdict(lambda: defaultdict(Counter))     # group -> (state) -> counters
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        if size_arg and size(int(g["cells"])) != size_arg:
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
            if not groups:
                continue
            if life is None:
                life = json.load(open(p))
                q = json.load(open(os.path.join(HERE, "q", g["game_id"] + ".json")))
            ls, qs = life["sides"][s], q["sides"][s]
            units = ls["units"]
            pos = ls["pos"]
            first = ls["first_seen"]
            nat_q = Counter()
            for k, v in qs["qeats"].items():
                b, og = k.split(":")
                if og == "natural":
                    nat_q[int(b)] += v
            nat_t = Counter()
            for k, v in qs["flow"].items():
                parts = k.split(":")
                if parts[1] == "natural":
                    nat_t[int(parts[0])] += v
            sp = Counter(min(r // 50, 9) for r, a, b, c in qs["qsplits"])
            mother = Counter(min(r // 50, 9) for r, a, b, c in qs["qsplits"] if a <= 5)
            for k in range(10):
                blk = ls["blk"][k]
                if not blk["qr"]:
                    continue
                dr = sum(units[k * 50:(k + 1) * 50])
                # the 25-round windows of this block in which she was alive throughout
                win = []
                for w0 in (k * 50, k * 50 + 25):
                    seg = pos[w0:w0 + 25]
                    if len(seg) == 25 and all(seg):
                        win.append(len({tuple(c) for c in seg}))
                for grp in groups:
                    a = acc[grp][k]
                    for key, v in blk.items():
                        a[key] += v
                    a["nat_q"] += nat_q[k]
                    a["nat_t"] += nat_t[k]
                    a["dr"] += dr
                    a["splits"] += sp[k]
                    a["win_n"] += len(win)
                    a["win_cells"] += sum(win)
                    # hand-over states
                    u = units[k * 50] if k * 50 < len(units) else 0
                    ub = "1-3" if u <= 3 else "4-7" if u <= 7 else "8-15" if u <= 15 else "16-31" if u <= 31 else "32+"
                    seen = "after first enemy seen" if first is not None and first < k * 50 else "before"
                    for st in ("units " + ub, seen):
                        h = hand[grp][st]
                        h["qr"] += blk["qr"]
                        h["nat"] += nat_q[k]
                        h["mother"] += mother[k]
                        h["home"] += blk["home"]
                        h["len"] += blk["lensum"]
    print(f"=== per 50 rounds{' (' + size_arg + ' maps)' if size_arg else ''}")
    hdr = "block | queens | eat q | eat team | home q | home team | half q | half team | seen | e4 q | e4 team | e8 q | e8 team | own4 | len | splits | cells25"
    for grp in GROUPS:
        print(f"--- {grp}")
        print(hdr)
        for k in range(10):
            a = acc[grp][k]
            if a["qr"] < 100:
                continue
            qr, tn = a["qr"], max(1, a["tn"])
            print(f"r{k * 50}-{k * 50 + 49} | {qr / 50:.0f} | {100 * a['nat_q'] / qr:.1f} | {100 * a['nat_t'] / max(1, a['dr']):.1f} | {a['home'] / qr:.1f} | {a['thome'] / tn:.1f} | "
                  f"{100 * a['half'] / qr:.0f}% | {100 * a['thalf'] / tn:.0f}% | {100 * a['seenr'] / qr:.0f}% | {a['m4'] / qr:.2f} | {a['tm4'] / tn:.2f} | {a['m8'] / qr:.2f} | {a['tm8'] / tn:.2f} | "
                  f"{a['a4'] / qr:.2f} | {a['lensum'] / qr:.1f} | {100 * a['splits'] / qr:.1f} | {a['win_cells'] / max(1, a['win_n']):.1f}")
    print("\n=== the hand-over: queen's natural pearls and mother splits per 100 rounds, distance from start, mean length; by state at the start of the 50-round block")
    states = ["units 1-3", "units 4-7", "units 8-15", "units 16-31", "units 32+", "before", "after first enemy seen"]
    print("group | " + " | ".join(states))
    for grp in GROUPS:
        cells = []
        for st in states:
            h = hand[grp][st]
            if h["qr"] < 100:
                cells.append("-")
                continue
            cells.append(f"eat {100 * h['nat'] / h['qr']:.1f}, splits {100 * h['mother'] / h['qr']:.1f}, home {h['home'] / h['qr']:.1f}, len {h['len'] / h['qr']:.1f} ({h['qr'] // 50} blocks)")
        print(f"{grp} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
