#!/usr/bin/env python3
"""Candidate 4 ("do not give way"): ram chances on small enemy dragons, turn by turn.

A chance = a non-queen dragon D of 4 or shorter starts its turn with the head of an enemy non-queen dragon E of 4 or
shorter inside its 7x7 view and a path of free cells to that head no longer than D's reach (1, 2, 3 steps for
lengths 2, 3, 4).  If several enemies qualify the nearest counts (ties: the longer enemy).
steps = 1 is a "meeting" (head on the next cell), steps 2-3 a "charge chance".
Taken = D dies head-on in this action together with an enemy dragon (it rammed).
Recorded with each chance:  rel   = E is longer / same / shorter than D
                            edge  = other own heads in D's view >= enemy heads in D's view (our code's
                                    TRADE_LOCAL_EDGE test; a lone dragon facing a lone enemy fails it)
                            round block, map class (over 1,200 cells or not), group.
Usage: python3 h_c4walk.py run [jobs] -> h_out/c4w/<gid>.json ; python3 h_c4walk.py table -> stdout
The games walked are those of h_c3.pick_rows(): all 401 of ours and 130 per top team.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict, deque
from multiprocessing import Pool

import lib
import h_c3

OUTD = "h_out/c4w"
TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}


class H(lib.Hooks):
    def __init__(self):
        self.tab = Counter()   # (side, block, n, rel, steps, edge, taken)
        self.pend = None
        self.dead = []

    def close(self, g):
        p = self.pend
        self.pend = None
        if p is None:
            return
        did, key = p
        heads = [d for d, t, r in self.dead if r == "headon"]
        teams = {t for d, t, r in self.dead if r == "headon"}
        taken = int(did in heads and len(teams) == 2)
        self.tab[key + (taken,)] += 1

    def round_start(self, g, r):
        self.close(g)

    def action(self, g, did, kind, nsteps):
        self.close(g)
        self.dead = []
        b = g.board
        s = g.teams[did]
        if did == b.queen[s]:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 4:
            return
        head = body[0]
        o = "B" if s == "A" else "A"
        qo = b.queen[o]
        en = al = 0
        targets = {}
        occupied = set()
        for d2, other in g.bodies.items():
            if d2 == did:
                continue
            occupied.update(other)
            if b.cheb(other[0], head) <= 3:
                if g.teams[d2] == s:
                    al += 1
                else:
                    en += 1
                    if d2 != qo and len(other) <= 4:
                        targets[other[0]] = len(other)
        if not targets:
            return
        rc = lib.reach(n)
        dist = {head: 0}
        dq = deque([head])
        found = []
        own = set(body)
        while dq:
            c = dq.popleft()
            dc = dist[c]
            if dc >= rc:
                continue
            for nb in b.nb(c):
                if nb is None or nb in dist:
                    continue
                if nb in targets:
                    found.append((dc + 1, -targets[nb], nb))
                    dist[nb] = dc + 1
                    continue
                if nb in occupied or nb in own:
                    continue
                dist[nb] = dc + 1
                dq.append(nb)
        if not found:
            return
        found.sort()
        steps, neg_len, cell = found[0]
        m = -neg_len
        rel = "longer" if m > n else "same" if m == n else "shorter"
        blk = 0 if g.round < 150 else 1 if g.round < 300 else 2
        self.pend = (did, (s, blk, n, rel, steps, int(al >= en)))

    def death(self, g, did, reason, length, body, actor):
        self.dead.append((did, g.teams[did], reason))

    def end(self, g, rounds, winner, result):
        self.close(g)


def work(row):
    out = f"{OUTD}/{row['game_id']}.json"
    if os.path.exists(out):
        return row["game_id"], None
    try:
        h = H()
        lib.Walk(row["replay_path"]).run(h)
        tmp = out + ".tmp%d" % os.getpid()
        json.dump(dict(game_id=row["game_id"], tab=[list(k) + [v] for k, v in h.tab.items()]), open(tmp, "w"), separators=(",", ":"))
        os.replace(tmp, out)
        return row["game_id"], None
    except Exception as exc:  # noqa: BLE001
        return row["game_id"], f"{type(exc).__name__}: {exc}"


def run(jobs):
    os.makedirs(OUTD, exist_ok=True)
    rows = h_c3.pick_rows()
    errs = []
    with Pool(jobs) as pool:
        for i, (gid, err) in enumerate(pool.imap_unordered(work, rows, chunksize=4)):
            if err:
                errs.append((gid, err))
            if (i + 1) % 100 == 0:
                print(i + 1, "/", len(rows), "errors", len(errs), flush=True)
    print("done", len(rows), "errors", errs[:5])


def table():
    games = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
    T = defaultdict(lambda: [0, 0])
    ng = Counter()
    for f in os.listdir(OUTD):
        if not f.endswith(".json"):
            continue
        d = json.load(open(f"{OUTD}/{f}"))
        g = games[d["game_id"]]
        cls = "large" if int(g["cells"]) > 1200 else "other"
        for s in "AB":
            o = "B" if s == "A" else "A"
            tid, oid = g[f"team{s}Id"], g[f"team{o}Id"]
            grp = []
            if tid == "1119":
                b = g["battle_id"]
                grp.append("meow tc30" if b in ("tc30-test-new", "tc30-dev1b-new") else "meow live" if (b.startswith("dl-") or b.endswith("-old")) else "meow other cand")
            elif oid == "1119":
                grp.append("opp of meow")
            if tid in ("306", "91", "264") and float(g[f"team{o}Elo"] or 0) >= 2000:
                grp.append(TEAMS[tid])
                grp.append("top3")
            for gn in grp:
                ng[(gn, cls)] += 1
            for side, blk, n, rel, steps, edge, taken, v in d["tab"]:
                if side != s:
                    continue
                st = "meeting" if steps == 1 else "charge"
                notshorter = "not shorter" if rel != "shorter" else "shorter"
                for gn in grp:
                    for key in ((gn, cls, st, "all", "all", "all"), (gn, cls, st, notshorter, "all", "all"), (gn, cls, st, notshorter, edge, "all"),
                                (gn, cls, st, "all", edge, "all"), (gn, cls, st, notshorter, edge, blk), (gn, cls, st, notshorter, "all", blk),
                                (gn, cls, st, rel, "all", "all"), (gn, cls, st, notshorter, edge, f"L{n}"),
                                (gn, cls, st, rel, edge, "rel-edge")):
                        T[key][0] += v
                        T[key][1] += v * taken
    G = ["meow live", "meow tc30", "meow other cand", "opp of meow", "Vibing++", "SSS", "forgot", "top3"]

    def pc(k):
        v = T[k]
        return f"{100 * v[1] / v[0]:3.0f}% of {v[0]:6d}" if v[0] else "       -      "

    print("games walked:", {f"{k[0]} {k[1]}": v for k, v in sorted(ng.items())})
    for cls in ("large", "other"):
        print(f"\n===== maps {'over 1,200 cells' if cls == 'large' else 'of 1,200 cells or fewer'}")
        for st in ("meeting", "charge"):
            what = "the enemy head is on the next cell" if st == "meeting" else "the enemy head is 2-3 free steps away, inside reach"
            print(f"-- {st}: {what}.  Rammed, share of such turns")
            print("   group            | all | enemy not shorter | ... and own other heads >= enemy heads in view | ... and fewer own heads (alone or outnumbered) | enemy shorter")
            for g in G:
                print(f"   {g:16s} | {pc((g, cls, st, 'all', 'all', 'all'))} | {pc((g, cls, st, 'not shorter', 'all', 'all'))} | "
                      f"{pc((g, cls, st, 'not shorter', 1, 'all'))} | {pc((g, cls, st, 'not shorter', 0, 'all'))} | {pc((g, cls, st, 'shorter', 'all', 'all'))}")
            print("   enemy not shorter, by round (0-149 | 150-299 | 300+), all then alone-or-outnumbered")
            for g in G:
                print(f"   {g:16s} | " + " | ".join(pc((g, cls, st, 'not shorter', 'all', b)) for b in (0, 1, 2)) + "  ||  "
                      + " | ".join(pc((g, cls, st, 'not shorter', 0, b)) for b in (0, 1, 2)))
        for st in ("meeting", "charge"):
            print(f"-- {st}, by the enemy's length against the own: longer / same / shorter, each as: own heads >= enemy heads in view, then fewer")
            for g in G:
                cells_ = []
                for rel in ("longer", "same", "shorter"):
                    cells_.append(pc((g, cls, st, rel, 1, "rel-edge")) + " , " + pc((g, cls, st, rel, 0, "rel-edge")))
                print(f"   {g:16s} | " + "   ;   ".join(cells_))
        print("-- rams made per game on small enemy heads (meetings + charges), and chances per game in brackets:")
        print("   group            | not outnumbered: enemy longer, same, shorter | alone or outnumbered: enemy longer, same, shorter | all")
        for g in G:
            n = ng[(g, cls)]
            if not n:
                continue
            cells_ = []
            tot = 0.0
            for edge in (1, 0):
                part = []
                for rel in ("longer", "same", "shorter"):
                    a = T[(g, cls, "meeting", rel, edge, "rel-edge")]
                    c = T[(g, cls, "charge", rel, edge, "rel-edge")]
                    part.append(f"{(a[1] + c[1]) / n:4.1f} ({(a[0] + c[0]) / n:5.1f})")
                    tot += (a[1] + c[1]) / n
                cells_.append(", ".join(part))
            print(f"   {g:16s} | " + " | ".join(cells_) + f" | {tot:5.1f}")
        print("-- chances per game (enemy not shorter): meetings, charge chances; and rams made from them")
        for g in G:
            n = ng[(g, cls)]
            if not n:
                continue
            m, c = T[(g, cls, "meeting", "not shorter", "all", "all")], T[(g, cls, "charge", "not shorter", "all", "all")]
            print(f"   {g:16s} meetings {m[0] / n:5.1f} a game, rammed {m[1] / n:4.1f}; charge chances {c[0] / n:5.1f}, rammed {c[1] / n:4.1f}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    else:
        table()
