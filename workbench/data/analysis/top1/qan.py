#!/usr/bin/env python3
"""Queen-centred comparison: top teams vs us, wins vs losses. Reads q/*.json (from extract.py).

Usage: python3 qan.py [section ...]   sections: env death intr hazard hunt (default all)
Per-round queen record: [x, y, len, e8m, e8p, e4p, a6p, a3p, seen, margin, near_small, free, ball4, degree,
                         portal_dist, start_manh, is_longest]
"""
import glob
import json
import statistics
import sys
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
MIN = 2000
PH = ((0, 50), (50, 100), (100, 200), (200, 300), (300, 400), (400, 500))
SIZES = ("small", "medium", "large")


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def load():
    out = []
    for f in glob.glob("q/*.json"):
        d = json.load(open(f))
        out.append(d)
    return out


def sides(games, team, min_elo=MIN, opp_in=None):
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] != team:
                continue
            oe = d["sides"][o]["elo"] or 0
            if oe < min_elo:
                continue
            if opp_in and d["sides"][o]["team"] not in opp_in:
                continue
            yield d, s, o


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else float("nan")


def env_rows(d, s, lo, hi):
    """Per-game means over the rounds in [lo, hi) while the queen of side s is alive."""
    q = d["sides"][s]["per"]["q"][lo:hi]
    q = [x for x in q if x]
    if len(q) < 10:
        return None
    n = len(q)
    cells = len({(x[0], x[1]) for x in q})
    return dict(n=n, len=mean(x[2] for x in q), e8m=mean(x[3] for x in q), e8p=mean(x[4] for x in q),
                e4p=mean(x[5] for x in q), a6p=mean(x[6] for x in q), a3p=mean(x[7] for x in q),
                seen=mean(x[8] > 0 for x in q), exposed=mean(x[9] is not None and x[9] <= 0 for x in q),
                small2=mean(x[10] is not None and x[10] <= 2 for x in q),
                free=mean(x[11] for x in q), ball=mean(x[12] for x in q), deg=mean(x[13] for x in q),
                portal=mean(x[14] >= 0 and x[14] <= 4 for x in q), home=mean(x[15] for x in q),
                cells100=cells * 100 / n, longest=mean(x[16] for x in q))


KEYS = ("len", "e8m", "e8p", "e4p", "a6p", "a3p", "seen", "exposed", "small2", "free", "ball", "deg", "portal",
        "home", "cells100", "longest")


def section_env(games):
    print("\n################ QUEEN ENVIRONMENT (per-game means while alive, then mean over games)")
    print("columns:", " ".join(KEYS))
    for sz in SIZES:
        print(f"\n--- map size {sz}")
        for team, name in TOP.items():
            for who in ("own", "opp"):
                for lo, hi in PH:
                    rows = []
                    for d, s, o in sides(games, team):
                        if size(d) != sz:
                            continue
                        r = env_rows(d, s if who == "own" else o, lo, hi)
                        if r:
                            rows.append(r)
                    if len(rows) < 5:
                        continue
                    print(f"{name:9s} {who} r{lo:3d}-{hi:3d} n={len(rows):3d} " + " ".join(
                        f"{k}={mean(r[k] for r in rows):.2f}" for k in KEYS))
    print("\n--- wins vs losses control (own queen, rounds 50-200, all sizes pooled then by size)")
    for team, name in TOP.items():
        for sz in ("all",) + SIZES:
            for res in ("W", "L"):
                rows = []
                for d, s, o in sides(games, team):
                    if sz != "all" and size(d) != sz:
                        continue
                    if (d["winner"] == s) != (res == "W"):
                        continue
                    r = env_rows(d, s, 50, 200)
                    if r:
                        rows.append(r)
                if len(rows) >= 5:
                    print(f"{name:9s} {sz:6s} {res} n={len(rows):3d} " + " ".join(
                        f"{k}={mean(r[k] for r in rows):.2f}" for k in KEYS))


def section_death(games):
    print("\n################ QUEEN DEATHS")
    for team, name in TOP.items():
        for who in ("own", "opp"):
            for sz in SIZES:
                n = 0
                reasons = Counter()
                rounds = []
                klen = Counter()
                kdist = Counter()
                qlen = Counter()
                ksteps = Counter()
                own_ram = 0
                for d, s, o in sides(games, team):
                    if size(d) != sz:
                        continue
                    n += 1
                    side = s if who == "own" else o
                    qd = d["sides"][side]["qdeath"]
                    if not qd:
                        continue
                    r = qd["reason"]
                    if r == "headon":
                        if qd["killer"] is None:
                            r = "own_ram"
                        elif qd["killer"]["team"] == side:
                            r = "ally_ram"
                        else:
                            r = "rammed"
                            k = qd["killer"]
                            klen["2" if k["len"] <= 2 else "3" if k["len"] == 3 else "4" if k["len"] == 4 else "5-9" if k["len"] <= 9 else "10+"] += 1
                            sd = k.get("start_path_to_qstart")
                            kdist["born" if k["born_this_round"] else "far" if sd is None else str(min(sd, 6))] += 1
                            ksteps[min(k["steps_used"], 5)] += 1
                    reasons[r] += 1
                    rounds.append(qd["round"])
                    qlen[min(qd["len"], 6)] += 1
                dead = sum(reasons.values())
                print(f"{name:9s} {who} {sz:6s} games={n:3d} queen died={dead:3d} ({dead / max(1, n):.2f}) median r={med(rounds):5.0f} "
                      f"causes={dict(reasons.most_common())}")
                print(f"{'':20s} rammed: killer len {dict(sorted(klen.items()))} | killer path dist to queen at round start "
                      f"{dict(sorted(kdist.items()))} | steps used {dict(sorted(ksteps.items()))} | queen len at death {dict(sorted(qlen.items()))}")


def section_intr(games):
    print("\n################ INTRUDERS: enemy heads that came within 6 steps (path) of a live queen")
    for team, name in TOP.items():
        for who in ("own", "opp"):
            for sz in SIZES:
                out = Counter()
                alive_rounds = 0
                eps = 0
                small = Counter()
                dur = []
                for d, s, o in sides(games, team):
                    if size(d) != sz:
                        continue
                    side = s if who == "own" else o
                    sd = d["sides"][side]
                    alive_rounds += sum(1 for x in sd["per"]["q"] if x)
                    for ep in sd["episodes"]:
                        eps += 1
                        oc = ep["outcome"]
                        if oc == "it_rammed":
                            oc = "it_rammed_queen" if ep.get("victim_queen") else "it_rammed_other"
                        out[oc] += 1
                        if ep["len"] <= 4:
                            small[oc] += 1
                        dur.append(ep["end"] - ep["start"])
                tot = sum(out.values())
                if not tot:
                    continue
                print(f"{name:9s} {who} {sz:6s} episodes={eps:5d} per100 queen-rounds={eps * 100 / max(1, alive_rounds):5.2f} "
                      f"median dur={med(dur):.0f} | " + " ".join(f"{k}={v / tot:.2f}" for k, v in out.most_common()))


def section_hazard(games):
    print("\n################ HAZARD: P(queen rammed this round | state at round start), rounds 20-400")
    print("state = closest small (len<=4) enemy head by path distance; 'exp' = some enemy head has her head cell in reach")
    for team, name in TOP.items():
        for who in ("own", "opp"):
            for sz in SIZES:
                cnt = Counter()
                die = Counter()
                for d, s, o in sides(games, team):
                    if size(d) != sz:
                        continue
                    side = s if who == "own" else o
                    sd = d["sides"][side]
                    qd = sd["qdeath"]
                    ram_round = qd["round"] if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] != side else -1
                    for r, x in enumerate(sd["per"]["q"]):
                        if not x or r < 20 or r >= 400:
                            continue
                        ns = x[10]
                        key = "none<=12" if ns is None else "d1" if ns <= 1 else "d2" if ns == 2 else "d3" if ns == 3 else "d4-6" if ns <= 6 else "d7+"
                        cnt[key] += 1
                        die[key] += r == ram_round
                        e = "exp" if (x[9] is not None and x[9] <= 0) else "safe"
                        cnt[e] += 1
                        die[e] += r == ram_round
                        cnt["all"] += 1
                        die["all"] += r == ram_round
                if not cnt["all"]:
                    continue
                keys = ("all", "safe", "exp", "d1", "d2", "d3", "d4-6", "d7+", "none<=12")
                print(f"{name:9s} {who} {sz:6s} " + " | ".join(
                    f"{k}: {cnt[k] / cnt['all']:.3f} of rounds, ram {1000 * die[k] / max(1, cnt[k]):.1f}/1000" for k in keys))


def section_hunt(games):
    print("\n################ WHO KILLS QUEENS: rams on enemy queens per game, attacker length, steps, and r500 results")
    for team, name in TOP.items():
        for sz in SIZES:
            n = 0
            kills = Counter()
            alen = Counter()
            for d, s, o in sides(games, team):
                if size(d) != sz:
                    continue
                n += 1
                for h in d["headons"]:
                    # [r, att_team, att_id, att_len, steps_used, steps_req, vic_team, vic_id, vic_len, vic_queen, vic_longest, att_queen, manh]
                    if h[9] and h[6] != h[1]:
                        if h[1] == s:
                            kills["we_killed_their_queen"] += 1
                            alen[min(h[3], 6)] += 1
                        else:
                            kills["they_killed_our_queen"] += 1
            print(f"{name:9s} {sz:6s} games={n:3d} " + " ".join(f"{k}={v / max(1, n):.2f}" for k, v in sorted(kills.items()))
                  + f" attacker len {dict(sorted(alen.items()))}")


def main():
    games = load()
    print("games loaded", len(games))
    want = sys.argv[1:] or ["env", "death", "intr", "hazard", "hunt"]
    for w in want:
        globals()["section_" + w](games)


if __name__ == "__main__":
    main()
