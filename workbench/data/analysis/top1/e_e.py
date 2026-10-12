#!/usr/bin/env python3
"""Question (e): what starts the feeding of a non-queen leader? A clock or a state?

A "feeder death" = a death by choice (not a ram, a free cell next to the head at the start of the turn) within 3 path
steps of the head of an own dragon at least twice as long. It is a "leader feeder" when that dragon is not the queen and
a "queen feeder" when it is. The "start" of leader feeding in a game = the round of the first of three leader-feeder
deaths that fall within 15 rounds of each other (the same for queen feeding).

For every team (meow by build, forgot, SSS, Vibing++, test4 and WeHaveQuizzes in all their games in the walked set):
  how many games reach round 300 / have a start; the spread of the start round; the start against the own queen's death,
  the enemy queen's death, the unit count, the own and the enemy's longest dragon, the round itself; how the start moves
  with each of these states (a clock gives the same round whatever the state); and how many own heads stand within 15
  cells of the longest dragon 50 / 25 / 0 rounds before the start.
Reads e_out/w. Output: e_out/e_trigger.txt  (and e_out/e_trigger_games.txt: one line per game)
"""
from collections import Counter, defaultdict

import e_data as D
import e_lib as E

P = D.Out("e_trigger.txt")
G = D.Out("e_trigger_games.txt")
G.quiet = True


def starts(deaths, DI, queen, need=3, span=15, dist=3):
    rs = sorted(x[0] for x in deaths if x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= dist and (x[DI["tq"]] == 1) == queen)
    for i in range(len(rs) - need + 1):
        if rs[i + need - 1] - rs[i] <= span:
            return rs[i]
    return None


def quart(v):
    v = sorted(v)
    n = len(v)
    if not n:
        return "-"
    return "%d / %d / %d / %d / %d" % (v[0], v[n // 4], v[n // 2], v[(3 * n) // 4], v[-1])


def describe(name, recs):
    recs = [r for r in recs if r.tl(300) is not None]
    n = len(recs)
    if n < 5:
        return
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    rows = []
    for r in recs:
        st = starts(r.s["deaths"], DI, False)
        qst = starts(r.s["deaths"], DI, True)
        qd = r.s["qdeath"][0] if r.s["qdeath"] else None
        eqd = r.o["qdeath"][0] if r.o["qdeath"] else None
        row = dict(r=r, st=st, qst=qst, qd=qd, eqd=eqd)
        if st is not None:
            t, e = r.tl(st - st % 5), r.tl(st - st % 5, False)
            row.update(units=t[1], total=t[2], longest=t[3], elongest=e[3], eunits=e[1], etotal=e[2], small=t[10])
            lead = {x[0]: x for x in r.s["lead"]}
            for k, off in (("g50", 50), ("g25", 25), ("g0", 0)):
                x = lead.get((st - off) - (st - off) % 25)
                row[k] = (x[21], x[22], x[6]) if x else None
        rows.append(row)
        G.f.write("%s | %d | %s | %d cells | %s | start %s | queen feeding start %s | own queen died %s | enemy queen died %s | units %s | longest %s vs %s | %s\n" % (
            name, r.gid, r.map, r.cells, E.NAMES.get(r.opp, r.opp), st, qst, qd, eqd, row.get("units"), row.get("longest"), row.get("elongest"),
            "W" if r.won else "L"))
    have = [x for x in rows if x["st"] is not None]
    P("\n=== %s: %d games that reach round 300; leader feeding starts in %s; queen feeding starts in %s" % (
        name, n, D.frac(len(have), n), D.frac(sum(1 for x in rows if x["qst"] is not None), n)))
    if len(have) < 5:
        return
    P("    start round: min / quartile / median / quartile / max = %s" % quart([x["st"] for x in have]))
    h = Counter(x["st"] // 25 * 25 for x in have)
    P("    start round by 25-round block: " + ", ".join("%d: %d" % (k, h[k]) for k in sorted(h)))
    alive = [x for x in have if x["qd"] is None or x["qd"] > x["st"]]
    dead = [x for x in have if x["qd"] is not None and x["qd"] <= x["st"]]
    P("    own queen alive at the start: %s; dead: %s. Rounds from her death to the start: %s" % (
        D.frac(len(alive), len(have)), D.frac(len(dead), len(have)), quart([x["st"] - x["qd"] for x in dead])))
    for lab, sel in (("own queen dead before round 100", lambda x: x["qd"] is not None and x["qd"] < 100),
                     ("own queen dead in rounds 100-199", lambda x: x["qd"] is not None and 100 <= x["qd"] < 200),
                     ("own queen dead in rounds 200-299", lambda x: x["qd"] is not None and 200 <= x["qd"] < 300),
                     ("own queen dead in rounds 300-399", lambda x: x["qd"] is not None and 300 <= x["qd"] < 400),
                     ("own queen alive at round 400", lambda x: x["qd"] is None or x["qd"] >= 400)):
        v = [x for x in rows if sel(x)]
        hv = [x for x in v if x["st"] is not None]
        P("      %-34s %3d games, start in %3d: %s" % (lab, len(v), len(hv), quart([x["st"] for x in hv])))
    for lab, sel in (("enemy queen dead before round 200", lambda x: x["eqd"] is not None and x["eqd"] < 200),
                     ("enemy queen dead in rounds 200-349", lambda x: x["eqd"] is not None and 200 <= x["eqd"] < 350),
                     ("enemy queen alive at round 350", lambda x: x["eqd"] is None or x["eqd"] >= 350)):
        v = [x for x in rows if sel(x)]
        hv = [x for x in v if x["st"] is not None]
        P("      %-34s %3d games, start in %3d: %s" % (lab, len(v), len(hv), quart([x["st"] for x in hv])))
    for lab, sel in (("maps over 1,200 cells", lambda x: x["r"].big), ("maps of 1,200 cells or fewer", lambda x: not x["r"].big)):
        v = [x for x in rows if sel(x)]
        hv = [x for x in v if x["st"] is not None]
        P("      %-34s %3d games, start in %3d: %s" % (lab, len(v), len(hv), quart([x["st"] for x in hv])))
    for lab, sel in (("units at round 200: 56 or more", lambda x: x["r"].tl(200)[1] >= 56), ("units at round 200: 30-55", lambda x: 30 <= x["r"].tl(200)[1] < 56),
                     ("units at round 200: under 30", lambda x: x["r"].tl(200)[1] < 30)):
        v = [x for x in rows if sel(x)]
        hv = [x for x in v if x["st"] is not None]
        P("      %-34s %3d games, start in %3d: %s" % (lab, len(v), len(hv), quart([x["st"] for x in hv])))
    for lab, sel in (("won", lambda x: x["r"].won), ("lost", lambda x: not x["r"].won)):
        v = [x for x in rows if sel(x)]
        hv = [x for x in v if x["st"] is not None]
        P("      %-34s %3d games, start in %3d: %s" % (lab, len(v), len(hv), quart([x["st"] for x in hv])))
    P("    at the start: units %s | own total %s | own longest %s | enemy's longest %s | dragons of 4 or shorter %s" % (
        quart([x["units"] for x in have]), quart([x["total"] for x in have]), quart([x["longest"] for x in have]), quart([x["elongest"] for x in have]),
        quart([x["small"] for x in have])))
    c = Counter("60+" if x["units"] >= 60 else "56-59" if x["units"] >= 56 else "40-55" if x["units"] >= 40 else "20-39" if x["units"] >= 20 else "under 20" for x in have)
    P("    units at the start: " + ", ".join("%s: %d" % (k, c[k]) for k in ("60+", "56-59", "40-55", "20-39", "under 20")))
    for k, lab in (("g50", "50 rounds before the start"), ("g25", "25 rounds before"), ("g0", "at the start")):
        v = [x[k] for x in have if x.get(k)]
        P("    own heads within 15 cells of the longest dragon %s: median %s (their length %s); nearest enemy head to it: median %s cells" % (
            lab, D.med([a[0] for a in v]), D.med([a[1] for a in v]), D.med([a[2] for a in v])))
    # queen feeding against leader feeding
    both = [x for x in rows if x["st"] is not None and x["qst"] is not None]
    P("    games with both kinds of feeding: %d; queen feeding first in %d" % (len(both), sum(1 for x in both if x["qst"] < x["st"])))
    qs = [x["qst"] for x in rows if x["qst"] is not None]
    if len(qs) >= 5:
        P("    queen feeding start round: %s" % quart(qs))


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        t = r.team
        if r.map == "Schooltime":
            continue
        if t == E.ME and r.study:
            by["meow, live bot"].append(r) if r.build == "live" else by["meow, test builds"].append(r)
        elif t in E.TOP3 and r.study:
            by[E.NAMES[t]].append(r)
        elif t in (E.T4, E.WHQ):
            by[E.NAMES[t] + (" against us" if r.opp == E.ME else " against the top three")].append(r)
    for name in ("meow, live bot", "meow, test builds", "test4 against us", "test4 against the top three", "WeHaveQuizzes against us",
                 "WeHaveQuizzes against the top three", "forgot", "SSS", "Vibing++"):
        describe(name, by.get(name, []))
        bd = [r for r in by.get(name, []) if r.bd]
        describe(name + " | only round-500 games with both queens dead", bd)


if __name__ == "__main__":
    main()
