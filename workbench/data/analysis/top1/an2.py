#!/usr/bin/env python3
"""Analysis of the second pass (q2/*.json): assassin tracks, leader exposure, queen vs team surroundings.

Sections: kills leader crowd   (default all)
"""
import glob
import json
import sys
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}
Q = {}
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    Q[d["game_id"]] = d
Q2 = {}
for f in glob.glob("q2/*.json"):
    d = json.load(open(f))
    Q2[d["game_id"]] = d


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def sides(team):
    for gid, d in Q.items():
        if gid not in Q2:
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= 2000:
                yield d, Q2[gid], s, o


def describe(kills, label):
    n = len(kills)
    if not n:
        print(f"  {label}: none")
        return
    born = sum(k["born_same_round"] for k in kills)
    seen = sum(1 for k in kills if "1" in k["track"] and k["track"]["1"][2] <= 3)
    unseen = n - born - seen
    klen = Counter("2" if k["klen"] <= 2 else "3" if k["klen"] == 3 else "4" if k["klen"] == 4 else "5-9" if k["klen"] <= 9 else "10+" for k in kills)
    steps = Counter(min(k["steps"], 5) for k in kills)

    def far(k, back):
        t = k["track"].get(str(back))
        if t is None:
            return "n/a"
        return "far(>=10)" if t[0] < 0 or t[0] >= 10 else "mid(5-9)" if t[0] >= 5 else "near(<=4)"
    d5 = Counter(far(k, 5) for k in kills)
    d8 = Counter(far(k, 8) for k in kills)
    grow = [k["klen"] - k["track"]["8"][1] for k in kills if "8" in k["track"]]
    grew = sum(1 for g in grow if g >= 2)
    print(f"  {label}: n={n} | victim could NOT see the killer at the start of the fatal round: {unseen / n:.2f} "
          f"(could see {seen / n:.2f}, killer born that round {born / n:.2f})")
    print(f"      killer length {dict(sorted(klen.items()))} | steps used {dict(sorted(steps.items()))}")
    print(f"      killer distance 5 rounds before {dict(d5)} | 8 rounds before {dict(d8)} | grew >= 2 in the last 8 rounds: {grew}/{len(grow)}")


def section_kills():
    print("################ ASSASSIN TRACKS (rams on an enemy queen / on an enemy longest dragon >= 15)")
    for team, name in TOP.items():
        for sz in ("small", "medium", "large"):
            qk, lk = [], []
            n = 0
            for d, d2, s, o in sides(team):
                if size(d) != sz or d["map"] in SEALED:
                    continue
                n += 1
                for k in d2["kills"]:
                    if k["victim_team"] != o:
                        continue
                    if k["queen"]:
                        qk.append(k)
                    elif k["longest"]:
                        lk.append(k)
            print(f"{name} {sz} (games {n}) kills made BY this team:")
            describe(qk, "enemy queens")
            describe(lk, "enemy leaders (non-queen, >= 15)")


def section_leader():
    print("\n################ LEADER EXPOSURE: rounds (>= 250) in which the longest dragon (>= 15) had >= 1 enemy head (len <= 12) with it in one-turn reach")
    for team, name in TOP.items():
        for sz in ("medium", "large"):
            for who in ("own leader", "enemy leader"):
                rounds = exposed = kills = 0
                games = 0
                kill_exposed = 0
                for d, d2, s, o in sides(team):
                    if size(d) != sz or d["map"] in SEALED:
                        continue
                    side = s if who == "own leader" else o
                    rows = d2["leader"][side]
                    games += 1
                    rounds += len(rows)
                    ex = {r[0] for r in rows if r[2] >= 1}
                    exposed += len(ex)
                    for k in d2["kills"]:
                        if k["victim_team"] == side and k["longest"] and k["round"] >= 250:
                            kills += 1
                            kill_exposed += k["round"] in ex
                if games:
                    print(f"{name:9s} {sz:6s} {who:12s} games={games:3d} leader-rounds/game={rounds / games:6.1f} exposed rounds/game={exposed / games:5.1f} "
                          f"({exposed / max(1, rounds):.3f}) killed by ram/game={kills / games:.2f} kills per 1000 exposed rounds={1000 * kill_exposed / max(1, exposed):.0f}")


def section_crowd():
    print("\n################ QUEEN vs HER TEAM: allies within manh 6 and enemies within manh 8 (queen / team mean), sealed map excluded")
    for team, name in TOP.items():
        for sz in ("small", "medium", "large"):
            for lo, hi in ((20, 100), (100, 200), (200, 300), (300, 500)):
                qa = ta = qe = te = 0.0
                n = 0
                for d, d2, s, o in sides(team):
                    if size(d) != sz or d["map"] in SEALED:
                        continue
                    for r, a, ma, e, me, units in d2["crowd"][s]:
                        if a is None or not (lo <= r < hi) or units < 8:
                            continue
                        qa += a
                        ta += ma
                        qe += e
                        te += me
                        n += 1
                if n >= 50:
                    print(f"{name:9s} {sz:6s} r{lo:3d}-{hi:3d} samples={n:5d} allies: queen {qa / n:.2f} team {ta / n:.2f} ratio {qa / max(1e-9, ta):.2f} | "
                          f"enemies: queen {qe / n:.2f} team {te / n:.2f} ratio {qe / max(1e-9, te):.2f}")
    print("\n  same, rounds 50-300, by result (W/L):")
    for team, name in TOP.items():
        for res in ("W", "L"):
            qa = ta = qe = te = 0.0
            n = 0
            for d, d2, s, o in sides(team):
                if d["map"] in SEALED or (d["winner"] == s) != (res == "W"):
                    continue
                for r, a, ma, e, me, units in d2["crowd"][s]:
                    if a is None or not (50 <= r < 300) or units < 8:
                        continue
                    qa += a
                    ta += ma
                    qe += e
                    te += me
                    n += 1
            if n:
                print(f"  {name:9s} {res} samples={n:5d} allies: queen {qa / n:.2f} team {ta / n:.2f} ratio {qa / max(1e-9, ta):.2f} | "
                      f"enemies: queen {qe / n:.2f} team {te / n:.2f} ratio {qe / max(1e-9, te):.2f}")


if __name__ == "__main__":
    print("games with both passes:", len(set(Q) & set(Q2)))
    for w in (sys.argv[1:] or ["kills", "leader", "crowd"]):
        globals()["section_" + w]()
