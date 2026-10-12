#!/usr/bin/env python3
"""Candidate 4: what a ram between small dragons is worth to the side that starts it, by kind of ram.

A ram here = a non-queen dragon of 4 or shorter (the starter) moves its head into the head of an enemy non-queen
dragon of 4 or shorter (the victim); both die.  For each ram:
  rel   the victim is longer / same / shorter than the starter (lengths at the start of the starter's action)
  edge  the starter had at least as many other own heads as enemy heads in its 7x7 view at the start of its action
  L1, L2  lengths of the two dragons when they died (the starter may have paid segments for its steps)
  the pearls of the two corpses: eaten by the starter's team / by the victim's team / never eaten
Per group of starter (meow live, meow tc30, opponents of meow, the three top teams), map class, rel and edge:
  rams per game, segments lost by each side, corpse pearls eaten by each side, and the swing per ram
  swing = (starter side: pearls eaten - L1) - (victim side: pearls eaten - L2).  Positive = good for the starter.
Usage: python3 h_c4pearls.py run [jobs] -> h_out/c4p/<gid>.json ; python3 h_c4pearls.py table -> stdout
Games: those of h_c3.pick_rows() (all 401 of ours and 130 per top team).
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import lib
import h_c3

OUTD = "h_out/c4p"
TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}


class H(lib.Hooks):
    def __init__(self):
        self.cur = None
        self.dead = []
        self.rams = []            # dict per ram
        self.by_corpse = {}       # dead dragon id -> ram index

    def close(self, g):
        c = self.cur
        self.cur = None
        if c is None:
            return
        did, s, n, al, en, lens = c
        heads = [(d, t, L) for d, t, r, L in self.dead if r == "headon"]
        mine = [x for x in heads if x[0] == did]
        theirs = [x for x in heads if x[1] != s]
        if not mine or len(theirs) != 1:
            return
        vid, vt, vL = theirs[0]
        o = "B" if s == "A" else "A"
        if vid == g.board.queen[o]:
            return
        v0 = lens.get(vid, vL)
        if v0 > 4:
            return
        rel = "longer" if v0 > n else "same" if v0 == n else "shorter"
        idx = len(self.rams)
        self.rams.append(dict(side=s, round=g.round, n=n, rel=rel, edge=int(al >= en), L1=mine[0][2], L2=vL, own=0, enemy=0))
        self.by_corpse[did] = idx
        self.by_corpse[vid] = idx

    def round_start(self, g, r):
        self.close(g)

    def action(self, g, did, kind, nsteps):
        self.close(g)
        self.dead = []
        b = g.board
        s = g.teams[did]
        if did == b.queen[s] or kind != 0:
            return
        body = g.bodies[did]
        n = len(body)
        if n > 4:
            return
        head = body[0]
        al = en = 0
        lens = {}
        for d2, other in g.bodies.items():
            if d2 == did:
                continue
            if b.cheb(other[0], head) <= 3:
                if g.teams[d2] == s:
                    al += 1
                else:
                    en += 1
                    lens[d2] = len(other)
        if en:
            self.cur = (did, s, n, al, en, lens)

    def death(self, g, did, reason, length, body, actor):
        self.dead.append((did, g.teams[did], reason, length))

    def eat(self, g, did, cell, origin):
        if origin[0] != "corpse":
            return
        idx = self.by_corpse.get(origin[2])
        if idx is None:
            return
        ram = self.rams[idx]
        if g.teams[did] == ram["side"]:
            ram["own"] += 1
        else:
            ram["enemy"] += 1

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
        json.dump(dict(game_id=row["game_id"], rams=h.rams), open(tmp, "w"), separators=(",", ":"))
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
    T = defaultdict(lambda: Counter())
    ng = Counter()
    for f in os.listdir(OUTD):
        if not f.endswith(".json"):
            continue
        d = json.load(open(f"{OUTD}/{f}"))
        g = games[d["game_id"]]
        cls = "large" if int(g["cells"]) > 1200 else "other"
        grp = {}
        for s in "AB":
            o = "B" if s == "A" else "A"
            tid, oid = g[f"team{s}Id"], g[f"team{o}Id"]
            names = []
            if tid == "1119":
                b = g["battle_id"]
                names.append("meow tc30" if b in ("tc30-test-new", "tc30-dev1b-new") else "meow live" if (b.startswith("dl-") or b.endswith("-old")) else "meow other cand")
            elif oid == "1119":
                names.append("opp of meow")
                b = g["battle_id"]
                names.append("opp vs tc30" if b in ("tc30-test-new", "tc30-dev1b-new") else "opp vs live" if (b.startswith("dl-") or b.endswith("-old")) else "opp vs other cand")
            if tid in ("306", "91", "264") and float(g[f"team{o}Elo"] or 0) >= 2000:
                names.append(TEAMS[tid])
                names.append("top3")
            grp[s] = names
            for nme in names:
                ng[(nme, cls)] += 1
        for s in "AB":
            res = "W" if g["winner"] == s else "L"
            for nme in grp[s]:
                ng[(nme + " " + res, cls)] += 1
        for ram in d["rams"]:
            res = "W" if g["winner"] == ram["side"] else "L"
            for nme in grp[ram["side"]]:
                for key in ((nme, cls, ram["rel"], ram["edge"]), (nme, cls, "all", "all"), (nme, cls, ram["rel"], "all"), (nme, cls, "all", ram["edge"]),
                            (nme + " " + res, cls, "all", "all")):
                    c = T[key]
                    c["n"] += 1
                    c["L1"] += ram["L1"]
                    c["L2"] += ram["L2"]
                    c["own"] += ram["own"]
                    c["enemy"] += ram["enemy"]
    G = ["meow live", "meow tc30", "opp of meow", "opp vs live", "opp vs tc30", "Vibing++", "SSS", "forgot", "top3"]
    WL = [x + r for x in ("meow live", "Vibing++", "SSS", "forgot", "top3") for r in (" W", " L")]
    print("== total swing per game from the rams each side STARTS (rams a game x swing per ram) ==")
    for cls in ("large", "other"):
        for g in G + WL:
            c = T[(g, cls, "all", "all")]
            if not ng[(g, cls)] or not c["n"]:
                continue
            swing = (c["own"] - c["L1"]) - (c["enemy"] - c["L2"])
            print(f"   {cls:5s} {g:14s} games {ng[(g, cls)]:4d}  rams started {c['n'] / ng[(g, cls)]:5.1f} a game  swing {swing / ng[(g, cls)]:+6.1f} segments a game")
    for cls in ("large", "other"):
        print(f"\n===== maps {'over 1,200 cells' if cls == 'large' else 'of 1,200 cells or fewer'}: rams started by a dragon of 4 or shorter on an enemy of 4 or shorter")
        print("   per ram: starter's length lost / victim's length lost / corpse pearls eaten by the starter's team / by the victim's team / swing for the starter's team")
        for label, rel, edge in (("all", "all", "all"),
                                 ("not outnumbered, victim longer", "longer", 1), ("not outnumbered, victim same", "same", 1), ("not outnumbered, victim shorter", "shorter", 1),
                                 ("alone or outnumbered, victim longer", "longer", 0), ("alone or outnumbered, victim same", "same", 0), ("alone or outnumbered, victim shorter", "shorter", 0)):
            print(f"-- {label}")
            for g in G:
                c = T[(g, cls, rel, edge)]
                n = c["n"]
                if not n or not ng[(g, cls)]:
                    continue
                swing = (c["own"] - c["L1"]) - (c["enemy"] - c["L2"])
                print(f"   {g:14s} {n / ng[(g, cls)]:5.1f} a game ({n:5d}):  {c['L1'] / n:4.2f} / {c['L2'] / n:4.2f} / {c['own'] / n:4.2f} / {c['enemy'] / n:4.2f} / {swing / n:+5.2f}"
                      f"   (starter's team eats {100 * c['own'] / max(1, c['own'] + c['enemy']):.0f}% of the eaten pearls)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        try:
            os.nice(10)
        except OSError:
            pass
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    else:
        table()
