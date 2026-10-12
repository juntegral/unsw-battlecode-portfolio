#!/usr/bin/env python3
"""d_extra.py <folder under ../../online/smoke> [jobs]: run the d_class walker on a smoke-test folder that is NOT in
games.csv (sub-session A4; used for the qn23 "queen no trap" candidate, 45 games).

Reads game-<id>.json (teams, map, winner) and M<id>.replay from the folder, finds both queens' death rounds in a
first light pass, then walks again with d_class.H.  Writes d_out/cls_extra/<folder>/<id>.json in the d_out/cls
format (plus cells, team names and elo), so d_tab.classify() works on it.  Read-only on the smoke folder.
"""
import glob
import json
import os
import sys
from multiprocessing import Pool

import d_class
import lib

HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE = os.path.normpath(os.path.join(HERE, "..", "..", "online", "smoke"))


class Deaths(lib.Hooks):
    def __init__(self):
        self.d = {"A": None, "B": None}

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        if did == g.board.queen[s]:
            self.d[s] = g.round

    def end(self, g, rounds, winner, result):
        self.rounds, self.winner = rounds, winner
        self.final = {s: (len(g.bodies[g.board.queen[s]]) if g.board.queen[s] in g.bodies else 0) for s in "AB"}
        self.units = {s: sum(1 for d in g.bodies if g.teams[d] == s) for s in "AB"}


def work(args):
    folder, meta_path = args
    try:
        meta = json.load(open(meta_path))
        gid = str(meta["id"])
        out = os.path.join(HERE, "d_out", "cls_extra", folder, gid + ".json")
        if os.path.exists(out):
            return gid, None
        rp = os.path.join(SMOKE, folder, f"M{gid}.replay")
        if not os.path.exists(rp):
            return gid, "no replay"
        pre = Deaths()
        lib.Walk(rp).run(pre)
        h = d_class.H(pre.d)
        g = lib.Walk(rp)
        g.run(h)
        b = g.board
        end_type = "wipe-out" if min(pre.units.values()) == 0 else "round 500"
        data = dict(version=d_class.VERSION, game_id=int(gid), map=meta["mapName"], w=b.w, h=b.h, cells=b.w * b.h,
                    rounds=h.rounds, winner=h.winner, battle_id=folder, end_type=end_type, final_queen=pre.final,
                    names={"A": meta["teamAName"], "B": meta["teamBName"]}, elo={"A": meta["teamAElo"], "B": meta["teamBElo"]},
                    sides={s: dict(team=int(meta[f"team{s}Id"]), queen=b.queen[s], start=list(b.starts[b.queen[s]]),
                                   death=h.dth[s], turns=[d_class.clean(t) for t in h.turns[s]],
                                   enc=[d_class.clean(t) for t in h.enc[s] if "full" not in t]) for s in "AB"})
        json.dump(data, open(out, "w"), separators=(",", ":"))
        return gid, None
    except Exception:  # noqa: BLE001
        import traceback
        return "?", traceback.format_exc()[-500:]


def main():
    folder = sys.argv[1]
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    os.makedirs(os.path.join(HERE, "d_out", "cls_extra", folder), exist_ok=True)
    metas = sorted(glob.glob(os.path.join(SMOKE, folder, "game-*.json")))
    print(folder, "games:", len(metas), flush=True)
    os.nice(10)
    with Pool(jobs) as pool:
        errs = [(g, e) for g, e in pool.imap_unordered(work, [(folder, m) for m in metas]) if e]
    print("done; errors", len(errs), errs[:5])


if __name__ == "__main__":
    main()
