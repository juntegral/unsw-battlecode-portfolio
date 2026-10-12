#!/usr/bin/env python3
"""c_freedeaths.py <team_id> <size|map> [max_games=120] [jobs=4] [upto=300]: non-ram deaths WITH a free cell next to the head.

Such a death is a choice of the bot (or a blind step): the dragon had a free neighbour cell and still died. For each one:
the reason the replay gives (wall = moved into kelp, self = into its own body, body = into another dragon's body,
noaction = suicide order or an order that could not be carried out), the length, whether the fatal step went through
a portal, and whose body it hit (own team / enemy). Per map, for the team and for its opponents in the same games:
deaths per game by class, and the share of all non-ram deaths that had a free cell.
"""
import csv
import sys
from collections import Counter
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Stop, Walk2  # noqa: E402


class F(Hooks2):
    def __init__(self, upto):
        self.upto = upto
        self.c = Counter()

    def round_start(self, g, r):
        if r > self.upto:
            raise Stop

    def death(self, g, did, reason, length, body, actor):
        if reason == "headon":
            return
        s = g.teams[did]
        b = g.board
        occ = c_lib.occupied(g)
        head = body[0]
        free = sum(1 for n in b.nb(head) if n is not None and n not in occ)
        ph = "r0-149" if g.round < 150 else "r150+"
        self.c[(s, ph, "all non-ram")] += 1
        if free == 0:
            return
        kind = reason
        if did == actor and g.act_kind == 0 and g.act_dirs:
            i = min(g.step_index, len(g.act_dirs) - 1)
            d = g.act_dirs[i]
            tgt = b.step(head, d)
            if tgt is not None:
                portal = b.manhattan(head, tgt) != 1
                who = ""
                if reason == "body":
                    owner = None
                    for d2, body2 in g.bodies.items():
                        if d2 != did and tgt in body2:
                            owner = g.teams[d2]
                            break
                    who = " of a team-mate" if owner == s else " of an enemy" if owner else ""
                kind = f"{reason}{who}{', through a portal' if portal else ''}"
        elif did == actor and g.act_kind == 2:
            kind = "suicide order"
        elif did == actor and g.act_kind == 1:
            kind = "split order that failed"
        L = "L2" if length <= 2 else "L3-4" if length <= 4 else "L5+"
        self.c[(s, ph, "free: " + kind)] += 1
        self.c[(s, ph, "free, " + L)] += 1
        self.c[(s, ph, "free, all")] += 1
        self.c[(s, ph, "free, segments")] += length


def work(job):
    gid, path, s, upto, mp = job
    f = F(upto)
    try:
        Walk2(path).run(f)
    except Stop:
        pass
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e), mp
    out = Counter()
    for (side, ph, what), v in f.c.items():
        out[("own" if side == s else "opp", ph, what)] += v
    return gid, out, None, mp


if __name__ == "__main__":
    team = int(sys.argv[1])
    want = sys.argv[2]
    nums = [x for x in sys.argv[3:] if x.isdigit()]
    maxg = int(nums[0]) if nums else 120
    jobs = int(nums[1]) if len(nums) > 1 else 4
    upto = int(nums[2]) if len(nums) > 2 else 300
    todo = []
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if want not in (size, g["map"], "any"):
            continue
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            try:
                if float(g[f"team{o}Elo"]) < 2000:
                    continue
            except ValueError:
                continue
            todo.append((g["game_id"], g["replay_path"], s, upto, g["map"]))
    todo = todo[:: max(1, len(todo) // maxg)][:maxg]
    total = {}
    games = Counter()
    with Pool(jobs) as pool:
        for gid, out, err, mp in pool.imap_unordered(work, todo):
            if err:
                print("error", gid, err)
                continue
            for key in (mp, "ALL"):
                total.setdefault(key, Counter()).update(out)
                games[key] += 1
    print(f"=== FREE-CELL DEATHS team {team}, {want}, {len(todo)} games, rounds 0-{upto}: non-ram deaths with a free cell next to the head, per game")
    for mp in sorted(total):
        n = games[mp]
        t = total[mp]
        print(f"  {mp} ({n} games)")
        for side in ("own", "opp"):
            who = f"team {team}" if side == "own" else "its opponents"
            for ph in ("r0-149", "r150+"):
                allnr = t[(side, ph, "all non-ram")]
                fr = t[(side, ph, "free, all")]
                kinds = sorted(((k[2][6:], v) for k, v in t.items() if k[0] == side and k[1] == ph and k[2].startswith("free: ")), key=lambda kv: -kv[1])
                print(f"    {who:13s} {ph:7s} | non-ram deaths {allnr / n:6.1f} per game, with a free cell {fr / n:5.1f} ({100 * fr / max(1, allnr):3.0f}%), segments {t[(side, ph, 'free, segments')] / n:5.1f} | "
                      f"L2 {t[(side, ph, 'free, L2')] / n:4.1f} L3-4 {t[(side, ph, 'free, L3-4')] / n:4.1f} L5+ {t[(side, ph, 'free, L5+')] / n:4.1f} | " +
                      ", ".join(f"{k} {v / n:.1f}" for k, v in kinds[:6]))
