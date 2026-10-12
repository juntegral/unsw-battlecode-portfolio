#!/usr/bin/env python3
"""Candidate 1, turn level: what our dragon did INSTEAD on every in-view chance it did not take, and what became
of the dragon that would have rammed.

Walks the meow games (opp elo >= 2000, Schooltime out) that have at least one in-view chance of ours in q3v2.
For every untaken in-view chance turn [round, side, id, length, steps, ...] it records:
  what   : the order given (move n steps / split / suicide), whether it ate, and whether its head ended nearer to or
           farther from her head (path distance, bodies ignored) than it started;
  enemy  : other enemy heads (not the queen) inside the attacker's 7x7 view, own other heads in view (the trade
           rule's "local edge"), her length, the round;
  fate   : the attacker's length at the end of the game (0 = dead), and whether it is our longest dragon at the end.
Usage: python3 h_c1walk.py run   -> h_out/c1walk.json
       python3 h_c1walk.py table -> stdout (h_out/c1walk.txt)
"""
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import lib

OUT = "h_out/c1walk.json"


class H(lib.Hooks):
    def __init__(self, side, wanted):
        self.side = side
        self.wanted = wanted          # {(round, id): chance record}
        self.pend = None
        self.rows = []

    def flush(self, g):
        p = self.pend
        self.pend = None
        if p is None:
            return
        b = g.board
        q = g.bodies.get(b.queen["B" if self.side == "A" else "A"])
        body = g.bodies.get(p["id"])
        if body is not None and p["qhead"] is not None:
            d1 = b.bfs(tuple(p["qhead"]), 14).get(body[0])
            p["end_dist"] = d1
        else:
            p["end_dist"] = None
        p["died"] = body is None
        self.rows.append(p)

    def round_start(self, g, r):
        self.flush(g)

    def action(self, g, did, kind, nsteps):
        self.flush(g)
        key = (g.round, did)
        c = self.wanted.get(key)
        if c is None:
            return
        b = g.board
        s = self.side
        o = "B" if s == "A" else "A"
        body = g.bodies[did]
        head = body[0]
        q = g.bodies.get(b.queen[o])
        qhead = q[0] if q else None
        en = al = 0
        en_small = 0
        for d2, other in g.bodies.items():
            if d2 == did:
                continue
            if b.cheb(other[0], head) <= 3:
                if g.teams[d2] == s:
                    al += 1
                elif d2 != b.queen[o]:
                    en += 1
                    en_small += len(other) <= 4
        self.pend = dict(round=g.round, id=did, len=len(body), steps_needed=c[4], kind=kind, nsteps=nsteps, ate=0,
                         qhead=list(qhead) if qhead else None, start_dist=c[4], en=en, al=al, qlen=len(q) if q else 0,
                         longest=c[7], ownq=c[8], units=sum(1 for d2 in g.bodies if g.teams[d2] == s))

    def moved(self, g, did, head, step_index, ate):
        if self.pend is not None and did == self.pend["id"] and did == g.current and ate:
            self.pend["ate"] += 1

    def end(self, g, rounds, winner, result):
        self.flush(g)
        mine = sorted(((len(body), -d) for d, body in g.bodies.items() if g.teams[d] == self.side), reverse=True)
        self.final_longest = -mine[0][1] if mine else None
        self.final_len = {d: len(body) for d, body in g.bodies.items() if g.teams[d] == self.side}
        self.final_second = mine[1][0] if len(mine) > 1 else 0


def work(job):
    gid, side, path, chances = job
    wanted = {(c[0], c[2]): c for c in chances}
    h = H(side, wanted)
    lib.Walk(path).run(h)
    for p in h.rows:
        p["final_len"] = h.final_len.get(p["id"], 0)
        p["is_final_longest"] = int(p["id"] == h.final_longest)
    return gid, dict(side=side, rows=h.rows, final_second=h.final_second)


def run():
    import csv
    paths = {r["game_id"]: r["replay_path"] for r in csv.DictReader(open("games.csv"))}
    base = json.load(open("h_out/base.json"))
    jobs = []
    for r in base:
        if "meow" not in r["groups"]:
            continue
        ch = [c for c in r["my_ch"] if c[9] and not c[5]]
        if ch:
            jobs.append((r["gid"], r["side"], paths[str(r["gid"])], ch))
    out = {}
    with Pool(4) as pool:
        for i, (gid, res) in enumerate(pool.imap_unordered(work, jobs, chunksize=2)):
            out[gid] = res
            if (i + 1) % 40 == 0:
                print(i + 1, "/", len(jobs), flush=True)
    json.dump(out, open(OUT, "w"), separators=(",", ":"))
    print("games", len(out), "turns", sum(len(v["rows"]) for v in out.values()))


def table():
    data = json.load(open(OUT))
    base = {r["gid"]: r for r in json.load(open("h_out/base.json")) if "meow" in r["groups"]}
    turns = []
    for gid, v in data.items():
        for p in v["rows"]:
            p["gid"] = int(gid)
            turns.append(p)
    print("untaken in-view chance turns:", len(turns), "in", len(data), "games")

    def lc(n):
        return "2-3" if n <= 3 else "4" if n == 4 else "5-9" if n <= 9 else "10-12"

    def what(p):
        if p["kind"] == 1:
            return "split"
        if p["kind"] == 2:
            return "suicide order"
        if p["kind"] is None:
            return "no order"
        if p["died"]:
            return "moved and died"
        d0, d1 = p["start_dist"], p["end_dist"]
        rel = "?" if d1 is None else "nearer" if d1 < d0 else "same distance" if d1 == d0 else "farther"
        return f"moved, ended {rel}" + (" (ate)" if p["ate"] else "")

    for sec, key in (("by attacker length", lambda p: lc(p["len"])), ("all", lambda p: "all")):
        tab = defaultdict(Counter)
        for p in turns:
            tab[key(p)][what(p)] += 1
        print(f"\n-- what the dragon did instead, {sec}")
        for k in sorted(tab):
            n = sum(tab[k].values())
            print(f"   {k:6s} n={n:3d}  " + "; ".join(f"{w} {c}" for w, c in tab[k].most_common()))
    # trade-rule conditions on those turns (2-4 long attackers)
    print("\n-- the trade rule's conditions on untaken turns of attackers 2-4 long")
    c = Counter()
    for p in turns:
        if p["len"] > 4:
            continue
        b = base[p["gid"]]
        big = b["cells"] > 1200
        edge = p["al"] >= p["en"] + 1          # other own heads in view >= enemy heads in view (the queen is one of them)
        late = p["round"] > 400 or (p["round"] > 300 and b["cells"] > 600 and p["ownq"])
        worth = p["qlen"] >= (max(5, p["len"] + 2) if big else p["len"])
        c["turns"] += 1
        c["fewer own other heads in view than enemy heads (local edge fails)"] += not edge
        c["after the round at which trading stops (400, or 300 with our queen alive on maps over 600 cells)"] += late
        c["queen too short to count as a target (shorter than the attacker; on maps over 1,200 cells shorter than max(5, own + 2))"] += not worth
        c["none of the three (rule should have allowed it)"] += edge and not late and worth
    for k, v in c.items():
        print(f"   {k}: {v}")
    # fate of the attacker on the FIRST untaken chance of each game
    print("\n-- the dragon that had the first untaken in-view chance of the game: what became of it")
    c = Counter()
    risk = []
    for gid, v in data.items():
        rows = sorted(v["rows"], key=lambda p: p["round"])
        p = rows[0]
        b = base[int(gid)]
        c["games"] += 1
        c["dead by the end of the game"] += p["final_len"] == 0
        c["alive at the end"] += p["final_len"] > 0
        c["... and our longest dragon at the end"] += p["is_final_longest"]
        if b["end_type"] != "wipe-out" and b["win"]:
            c["round-500 wins among these games"] += 1
            if p["is_final_longest"] or p["longest"]:
                second = v["final_second"]
                risk.append((int(gid), b["map"], p["round"], p["len"], "our longest then" if p["longest"] else "",
                             "our longest at the end" if p["is_final_longest"] else f"ended {p['final_len']}",
                             f"our final longest {b['my_fin']['longest']}, second {second}; her final longest {b['op_fin']['longest']}; her queen died r{b['op_qd']['round'] if b['op_qd'] else '-'}",
                             "STILL A WIN without it" if second > b["op_fin"]["longest"] else "WOULD NEED A NEW LEADER"))
    for k, v in c.items():
        print(f"   {k}: {v}")
    print("   round-500 wins in which that dragon was our longest then or at the end:")
    for x in sorted(risk):
        print("     ", *x)
    # segments the rule would spend: length of the attacker on the first untaken chance
    print("\n-- price: length of the attacker on the first untaken in-view chance of each game, and paid steps")
    lens = Counter()
    paid = Counter()
    for gid, v in data.items():
        p = sorted(v["rows"], key=lambda p: p["round"])[0]
        lens[lc(p["len"])] += 1
        paid[min(4, max(0, p["steps_needed"] - (-(-p["len"] // 4))))] += 1
    print("   attacker length:", dict(lens), " paid steps (4 = 4 or more):", dict(sorted(paid.items())))
    tot_len = sum(sorted(v["rows"], key=lambda p: p["round"])[0]["len"] for v in data.values())
    print(f"   segments spent (attacker lengths summed): {tot_len} in {len(data)} games; her queen's length on those turns summed: "
          f"{sum(sorted(v['rows'], key=lambda p: p['round'])[0]['qlen'] for v in data.values())}")
    # examples
    print("\n-- examples: untaken turns with her head on the next cell (1 step) or 2 steps away, attackers 2-4 long")
    ex = sorted((p for p in turns if p["len"] <= 4 and p["steps_needed"] <= 2), key=lambda p: (p["steps_needed"], p["gid"], p["round"]))
    for p in ex[:60]:
        b = base[p["gid"]]
        print(f"   {p['gid']} {b['map']:16s} r{p['round']:3d} our #{p['id']} L{p['len']} needs {p['steps_needed']} step(s); her queen L{p['qlen']}; it {what(p)};"
              f" own/enemy other heads in view {p['al']}/{p['en']}; game: {'W' if b['win'] else 'L'} {b['end_type']}, her queen {'alive' if b['op_fin']['queen'] else 'dead'} at the end")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run()
    else:
        table()
