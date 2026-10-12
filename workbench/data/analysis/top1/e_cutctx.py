#!/usr/bin/env python3
"""The situation at every leader cut, and what became of the stub. One more walk over the study games.

A leader cut = a split in which the team's longest dragon of the round (8 or longer; or a dragon born this round out of
such a cut, so chains count) keeps 2-3 segments and gives the rest to a new id. From round 250. Recorded per cut:
  free    free cells next to the parent's head at the start of its turn (no body on it; kelp and portals respected)
  room    the largest number of cells reachable from one of those free cells without crossing any body (capped at 40):
          the size of the pocket ahead of the head
  enemy   Manhattan distance from the parent's head to the nearest enemy head, and that enemy's length
  crowd   own heads within 2 cells of the parent's head
  heir    free cells next to the child's head right after the split
  stub    what became of the 2-3-long head part: died within 3 / 10 rounds and how (rammed, by choice = it had a free
          cell, boxed in), or alive after 10 rounds, and how far its head is then from where it was cut
Output: e_out/cc/<gid>.json (one list of rows per side); `python3 e_cutctx.py agg` prints the table to e_out/cutctx.txt.
Usage: python3 e_cutctx.py run [workers=5] | one <gid> | agg"""
import json
import os
import sys
from collections import deque
from multiprocessing import Pool

import e_lib as E

OUT = os.path.join(E.HERE, "e_out", "cc")
CAP = 40


class W(E.Hooks):
    def __init__(self):
        self.long_id = {"A": None, "B": None}
        self.born_round = {}
        self.cut_child = {}          # child id -> round it was born in a leader cut
        self.t_free = {}             # did -> (free cells list) at its turn start this round
        self.rows = {"A": [], "B": []}
        self.stubs = {}              # stub id -> row
        self.pending = []            # rows waiting for the 10-round check

    def round_start(self, g, r):
        best = {"A": (0, None), "B": (0, None)}
        for d, body in g.bodies.items():
            s = g.teams[d]
            if len(body) > best[s][0]:
                best[s] = (len(body), d)
        self.long_id = {s: best[s][1] for s in "AB"}
        self.t_free = {}
        keep = []
        for row in self.pending:
            if r - row["r"] >= 10:
                sid = row["stub"]
                if sid in g.bodies and row["fate"] is None:
                    row["fate"] = "alive"
                    row["moved"] = g.board.manhattan(g.bodies[sid][0], tuple(row["at"]))
                    row["stublen"] = len(g.bodies[sid])
                self.stubs.pop(sid, None)
            else:
                keep.append(row)
        self.pending = keep

    def turn(self, g, did):
        body = g.bodies[did]
        self.t_free[did] = E.free_neighbours(g, body[0])

    def room(self, g, start):
        occ = g.occ
        seen = {start}
        q = deque([start])
        while q and len(seen) < CAP:
            c = q.popleft()
            for n in g.board.nb(c):
                if n is not None and n not in occ and n not in seen:
                    seen.add(n)
                    q.append(n)
        return min(len(seen), CAP)

    def action(self, g, did, kind, nsteps):
        if kind != 1:
            return
        # the state just before the split is applied
        body = g.bodies[did]
        s = g.teams[did]
        self._pre = None
        if len(body) < 8 or g.round < 250:
            return
        if did != self.long_id[s] and self.cut_child.get(did) != g.round:
            return
        free = self.t_free.get(did)
        if free is None:
            free = E.free_neighbours(g, body[0])
        room = max((self.room(g, c) for c in free), default=0)
        em, el = 999, 0
        crowd = 0
        head = body[0]
        for d, b in g.bodies.items():
            if d == did:
                continue
            m = g.board.manhattan(head, b[0])
            if g.teams[d] != s:
                if m < em:
                    em, el = m, len(b)
            elif m <= 2:
                crowd += 1
        self._pre = (did, len(free), room, em, el, crowd, head)

    def split(self, g, parent, child, before, plen, clen):
        pre = getattr(self, "_pre", None)
        self._pre = None
        if pre is None or pre[0] != parent or plen > 3 or before < 8:
            return
        s = g.teams[parent]
        self.cut_child[child] = g.round
        heir_free = len(E.free_neighbours(g, g.bodies[child][0]))
        row = dict(r=g.round, parent=parent, child=child, before=before, keep=plen, free=pre[1], room=pre[2], em=pre[3], el=pre[4],
                   crowd=pre[5], heir_free=heir_free, at=list(pre[6]), chain=int(parent != self.long_id[s]), stub=parent, fate=None,
                   dt=None, moved=None, stublen=None)
        self.rows[s].append(row)
        self.stubs[parent] = row
        self.pending.append(row)

    def death(self, g, did, reason, length, body, actor):
        row = self.stubs.get(did)
        if row is None or row["fate"] is not None:
            return
        if reason == "headon":
            fate = "rammed" if (actor is not None and actor != did) else "it rammed"
        else:
            fate = "by choice" if E.free_neighbours(g, body[0]) else "boxed in"
        row["fate"] = fate
        row["dt"] = g.round - row["r"]
        row["reason"] = reason

    def end(self, g, rounds, winner, result):
        for row in self.pending:
            if row["fate"] is None:
                row["fate"] = "game over"


def walk(meta):
    g = E.Walk(meta["path"])
    w = W()
    g.run(w)
    return dict(gid=meta["gid"], sides=w.rows)


def one(meta):
    path = os.path.join(OUT, "%d.json" % meta["gid"])
    if os.path.exists(path):
        return meta["gid"], "skip"
    try:
        out = walk(meta)
    except Exception as e:  # noqa: BLE001
        return meta["gid"], "ERROR %r" % (e,)
    tmp = path + ".tmp%d" % os.getpid()
    with open(tmp, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    os.replace(tmp, path)
    return meta["gid"], "ok"


def groups(g, S):
    out = []
    O = E.other(S)
    t, o = g[S], g[O]
    if E.in_study(g, S):
        if t == E.ME:
            out += ["meow", "meow live" if E.build(g) == "live" else "meow test"]
        for k, n in ((E.FORGOT, "forgot"), (E.SSS, "SSS"), (E.VIB, "Vibing++")):
            if t == k:
                out += [n, "top3"]
    if o == E.ME and g[S + "e"] >= 2000 and g["map"] != "Schooltime":
        out.append("opp")
        if t == E.T4:
            out.append("test4 (vs us)")
        elif t == E.WHQ:
            out.append("WHQ (vs us)")
    return out


def agg():
    metas = {g["gid"]: g for g in E.load_games()}
    f = open(os.path.join(E.HERE, "e_out", "cutctx.txt"), "w")

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        f.write(s + "\n")

    order = ("meow live", "meow test", "meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++", "top3")
    P("THE SITUATION AT EVERY LEADER CUT FROM ROUND 250 (all study games of the group; a leader cut = the team's longest dragon of")
    P("8+, or a dragon born in the same round out of such a cut, keeps 2-3 and gives the rest to a new id)")
    P("free = free cells next to the head at the start of its turn; room = cells reachable from them without crossing a body (capped 40)")
    for big, name in ((False, "SMALL MAPS (<= 1,200 cells)"), (True, "BIG MAPS (> 1,200 cells)")):
        P("")
        P(name)
        P("%-14s %6s %6s | with a free cell (voluntary): n, share | of the voluntary ones: room <=4 / 5-8 / 9-20 / more | enemy head within 3 / 4-6 / farther | "
          "own heads within 2 cells: 0 / 1 / 2+ | heir born with no free cell | the stub afterwards: dies within 3 rounds / in 4-10 / alive after 10 (moved 5+ cells away) | "
          "how the stubs that died within 10 rounds died: boxed in / by choice / rammed" % ("group", "games", "cuts"))
        a = {}
        for fn in os.listdir(OUT):
            if not fn.endswith(".json"):
                continue
            d = json.load(open(os.path.join(OUT, fn)))
            g = metas[d["gid"]]
            if (g["cells"] > 1200) != big:
                continue
            for S in "AB":
                for grp in groups(g, S):
                    x = a.setdefault(grp, dict(games=0, cuts=0, vol=0, room=[0, 0, 0, 0], en=[0, 0, 0], crowd=[0, 0, 0], heir0=0,
                                               d3=0, d10=0, alive=0, moved=0, how={}, fvol=0, forced_heir0=0, forced=0))
                    x["games"] += 1
                    for row in d["sides"][S]:
                        x["cuts"] += 1
                        if row["free"] == 0:
                            x["forced"] += 1
                            x["forced_heir0"] += int(row["heir_free"] == 0)
                            continue
                        x["vol"] += 1
                        rm = row["room"]
                        x["room"][0 if rm <= 4 else 1 if rm <= 8 else 2 if rm <= 20 else 3] += 1
                        x["en"][0 if row["em"] <= 3 else 1 if row["em"] <= 6 else 2] += 1
                        x["crowd"][min(2, row["crowd"])] += 1
                        x["heir0"] += int(row["heir_free"] == 0)
                        if row["fate"] in ("alive",):
                            x["alive"] += 1
                            x["moved"] += int((row["moved"] or 0) >= 5)
                        elif row["fate"] in ("game over", None) or row["dt"] is None:
                            pass
                        else:
                            if row["dt"] <= 3:
                                x["d3"] += 1
                            else:
                                x["d10"] += 1
                            x["how"][row["fate"]] = x["how"].get(row["fate"], 0) + 1
        for grp in order:
            x = a.get(grp)
            if not x or not x["vol"]:
                continue
            v = x["vol"]
            pc = lambda k: "%2.0f%%" % (100.0 * k / v)
            P("%-14s %6d %6d | %5d %3.0f%% | %s / %s / %s / %s | %s / %s / %s | %s / %s / %s | %s (forced cuts: %2.0f%% of %d) | %s / %s / %s (%s) | %s / %s / %s" % (
                grp, x["games"], x["cuts"], v, 100.0 * v / x["cuts"], pc(x["room"][0]), pc(x["room"][1]), pc(x["room"][2]), pc(x["room"][3]),
                pc(x["en"][0]), pc(x["en"][1]), pc(x["en"][2]), pc(x["crowd"][0]), pc(x["crowd"][1]), pc(x["crowd"][2]), pc(x["heir0"]),
                100.0 * x["forced_heir0"] / max(1, x["forced"]), x["forced"],
                pc(x["d3"]), pc(x["d10"]), pc(x["alive"]), pc(x["moved"]),
                x["how"].get("boxed in", 0), x["how"].get("by choice", 0), x["how"].get("rammed", 0) + x["how"].get("it rammed", 0)))
    f.close()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "one":
        meta = next(g for g in E.load_games() if g["gid"] == int(sys.argv[2]))
        out = walk(meta)
        for S in "AB":
            for row in out["sides"][S]:
                print(S, row)
    elif sys.argv[1] == "agg":
        agg()
    else:
        jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        rows = [m for m in E.study_games() if not os.path.exists(os.path.join(OUT, "%d.json" % m["gid"]))]
        print("games to walk:", len(rows), flush=True)
        os.nice(10)
        bad = 0
        with Pool(min(jobs, 5)) as p:
            for i, (gid, st) in enumerate(p.imap_unordered(one, rows, chunksize=2)):
                if st.startswith("ERROR"):
                    bad += 1
                    print(gid, st, flush=True)
                if i % 200 == 0:
                    print(i, flush=True)
        print("done, errors:", bad, flush=True)
