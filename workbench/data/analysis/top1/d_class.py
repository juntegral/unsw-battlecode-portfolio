#!/usr/bin/env python3
"""d_class.py: every queen's last turns and every queen turn with an enemy head in view (sub-session A4).

  python3 d_class.py run [jobs] [--only id,id]   walk the replays, write d_out/cls/<game_id>.json (both sides of each game)
  python3 d_class.py show <game_id> <A|B>         print the stored death record of one queen in readable form

Games: every game in games.csv (Schooltime left out) in which meow (1119), Vibing++ (306), SSS (91) or forgot (264)
plays a team rated 2000+.  Both queens of each such game are recorded, so "our opponents" come for free.

What is stored per side
  death   : round, reason, length, position, who acted, the killer (id, length at the start of its move, steps used,
            start cell, born this round, parent), the fatal step of an own-action death (direction, portal step or
            not, what was on the destination).
  turns   : the queen's last LOOKBACK turns before her death, each with the board around her at the START OF HER OWN
            TURN (after lower ids moved): the four sides (kelp / free / pearl / own body / ally body or head / enemy
            body or head, the occupant's id, length and segment index), the free region she can still walk into
            (flood through cells without a body, capped), whether her head stands on a "tree cell" (terrain that has no
            way round: a dead-end corridor or nook, found by pruning one-exit cells of the kelp/portal graph), every
            enemy head near her, and for every cell she could end her move on whether a visible enemy head could move
            into it this round.
  enc     : one compact row for EVERY turn of the game in which an enemy head was inside her 7x7 view.

Reach model.  An enemy of length L with head at s can move its head into cell c this round if there is a path of
cells without a body from s to c of k steps with k <= ceil(L/4) + (L-2) + pearls eaten on the way before the last
step (rules: movement.md, execution-order.md).  Bodies are taken as they stand at the start of the queen's turn,
except the queen's own last segment, which is taken as gone (she moves).  Other dragons that move between her turn
and the enemy's are not modelled.  "In view" = Chebyshev distance 3 or less from her head, wrapped (vision.md).
"""
import csv
import json
import os
import sys
from collections import deque
from multiprocessing import Pool

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "d_out", "cls")
TEAMS = {"1119": "meow", "306": "Vibing++", "91": "SSS", "264": "forgot"}
LOOKBACK = 12
CAP = 40
VERSION = 4


def edge_key(b, cell, d):
    x, y = cell
    if d == 0:
        return (x, y, "N")
    if d == 2:
        return (x, (y + 1) % b.h, "N")
    if d == 3:
        return (x, y, "W")
    return ((x + 1) % b.w, y, "W")


def is_portal(b, cell, d):
    return edge_key(b, cell, d) in b.portal_pair


def tree_cells(b):
    """Cells removed when one-exit cells of the terrain graph are pruned again and again: no way round from there."""
    nbs = {}
    for x in range(b.w):
        for y in range(b.h):
            c = (x, y)
            nbs[c] = set(n for n in b.nb(c) if n is not None and n != c)
    deg = {c: len(v) for c, v in nbs.items()}
    dead = set()
    stack = [c for c, d in deg.items() if d <= 1]
    while stack:
        c = stack.pop()
        if c in dead:
            continue
        dead.add(c)
        for n in nbs[c]:
            if n not in dead:
                deg[n] -= 1
                if deg[n] <= 1:
                    stack.append(n)
    return dead


def reach_map(b, blocked, pearls, src, length, target, maxdepth=9):
    """cell -> fewest steps in which a dragon (head src, length) can move its head into it this round.
    `blocked` cells cannot be entered, except `target` (the queen's head: entering it is the ram)."""
    free = -(-length // 4)
    budget = length - 2
    layer = {src: 0}
    out = {}
    s = 0
    while layer and s < maxdepth:
        s += 1
        nxt = {}
        for c, p in layer.items():
            if s > free and s - free > budget + p:
                continue
            for n in b.nb(c):
                if n is None or n == src:
                    continue
                if n in blocked:
                    if n == target and n not in out:
                        out[n] = s
                    continue
                p2 = p + 1 if (n in pearls and n not in out) else p
                if nxt.get(n, -1) < p2:
                    nxt[n] = p2
                if n not in out:
                    out[n] = s
        layer = nxt
    return out


def flood(b, blocked, src, cap=CAP, skip=None):
    """Number of cells without a body reachable from src (src not counted), capped."""
    seen = {src}
    q = deque([src])
    n = 0
    while q:
        c = q.popleft()
        for x in b.nb(c):
            if x is None or x in seen or x in blocked or x == skip:
                continue
            seen.add(x)
            n += 1
            if n >= cap:
                return cap
            q.append(x)
    return n


def own_moves(b, blocked, pearls, src, length):
    """cell -> (fewest steps, paid steps needed) for the queen's own move this turn."""
    free = -(-length // 4)
    budget = length - 2
    layer = {src: 0}
    out = {}
    s = 0
    while layer and s < 6:
        s += 1
        nxt = {}
        for c, p in layer.items():
            if s > free and s - free > budget + p:
                continue
            for n in b.nb(c):
                if n is None or n == src or n in blocked:
                    continue
                p2 = p + 1 if (n in pearls and n not in out) else p
                if nxt.get(n, -1) < p2:
                    nxt[n] = p2
                if n not in out:
                    out[n] = (s, max(0, s - free))
        layer = nxt
    return out


class H(lib.Hooks):
    def __init__(self, deaths):
        self.qd = deaths                      # side -> death round or None (from q/<id>.json)
        self.turns = {"A": [], "B": []}
        self.enc = {"A": [], "B": []}
        self.dth = {"A": None, "B": None}
        self.cur = {"A": None, "B": None}     # the queen's turn record under way (full or compact)
        self.parent = {}
        self.victim = {}
        self.round_heads = {}
        self.tree = None
        self.seen_hist = {"A": deque(maxlen=4), "B": deque(maxlen=4)}  # enemy ids in her view, last turns

    # ---------- per-turn snapshot
    def snap(self, g, side, kind):
        b = g.board
        r = g.round
        qid = b.queen[side]
        q = g.bodies[qid]
        head, L = q[0], len(q)
        dround = self.qd[side]
        full = dround is not None and r >= dround - LOOKBACK
        vis = []
        for d, body in g.bodies.items():
            if g.teams[d] != side and b.cheb(body[0], head) <= 3:
                vis.append(d)
        self.seen_hist[side].append(set(vis))
        if not vis and not full:
            self.cur[side] = None
            return
        if self.tree is None:
            self.tree = tree_cells(b)
        occ = {}
        for d, body in g.bodies.items():
            for k, c in enumerate(body):
                occ[c] = (d, k)
        pearls = g.pearls
        tail = q[-1]
        blocked_mv = set(occ)                 # for her own move
        blocked_en = set(occ)
        blocked_en.discard(tail)              # her last segment is gone once she moves
        pdist = b.bfs(head, 9)
        qreach = min(5, lib.reach(L))
        # enemies near her: in view, or within 9 path steps (bodies ignored)
        en = []
        rmaps = {}
        for d, body in g.bodies.items():
            if g.teams[d] == side:
                continue
            h2 = body[0]
            ch = b.cheb(h2, head)
            pd = pdist.get(h2)
            if ch > 4 and pd is None:
                continue
            n2 = len(body)
            # no reach map for an enemy that cannot get near the cells she can end on (cheap skip, same result)
            if pd is None or lib.reach(n2) + 2 < pd - qreach:
                rm = {}
            else:
                rm = reach_map(b, blocked_en, pearls, h2, n2, head, min(9, pd + qreach + 3))
            rmaps[d] = rm
            seen_part = any(b.cheb(c, head) <= 3 for c in body)
            en.append([d, n2, h2[0], h2[1], ch, pd if pd is not None else -1, int(ch <= 3), rm.get(head, 0),
                       lib.reach(n2), int(seen_part)])
        visset = set(vis)
        # allied heads near
        a3 = a6 = 0
        for d, body in g.bodies.items():
            if g.teams[d] == side and d != qid:
                pd = pdist.get(body[0])
                if pd is not None:
                    a3 += pd <= 3
                    a6 += pd <= 6
        small_vis = [g.bodies[d][0] for d in vis if len(g.bodies[d]) <= 4]
        sdist = {}
        if small_vis:
            # bodies-ignored path distance to the nearest visible small enemy head, for her cell and her options
            best = {}
            for sh in small_vis:
                dd = b.bfs(sh, 12)
                for c, v in dd.items():
                    if v < best.get(c, 99):
                        best[c] = v
            sdist = best
        d0_small = sdist.get(head, -1) if small_vis else -1

        def threat(c):
            """(steps of the quickest visible enemy into c or 0, same over all enemies near)"""
            v = a = 0
            for row in en:
                s = rmaps[row[0]].get(c)
                if s:
                    if a == 0 or s < a:
                        a = s
                    if row[0] in visset and (v == 0 or s < v):
                        v = s
            return v, a

        # the four sides
        sides = []
        nfree = nsafe = nsafe_all = 0
        rel = [0, 0, 0]
        for d in range(4):
            ek = edge_key(b, head, d)
            if ek in b.kelp:
                sides.append(["K"])
                continue
            c = b.step(head, d)
            portal = int(ek in b.portal_pair)
            o = occ.get(c)
            if o is None:
                tv, ta = threat(c)
                nfree += 1
                nsafe += tv == 0
                nsafe_all += ta == 0
                ds = sdist.get(c, -1) if small_vis else -1
                if small_vis and d0_small >= 0 and ds >= 0:
                    rel[0 if ds < d0_small else 1 if ds == d0_small else 2] += 1
                row = ["P" if c in pearls else "F", c[0], c[1], portal, tv, ta, ds, int(c in self.tree)]
                if full:
                    row.append(flood(b, blocked_en, c, CAP, skip=None))
                sides.append(row)
            else:
                oid, idx = o
                if oid == qid:
                    code = "o"
                elif g.teams[oid] == side:
                    code = "A" if idx == 0 else "a"
                else:
                    code = "E" if idx == 0 else "e"
                sides.append([code, c[0], c[1], portal, oid, len(g.bodies[oid]), idx])
        # every cell she can end on this turn
        mv = own_moves(b, blocked_mv, pearls, head, L)
        nsafe_freeonly = nsafe_paid = 0
        for c, (s, paid) in mv.items():
            tv, ta = threat(c)
            if tv == 0:
                if paid == 0:
                    nsafe_freeonly += 1
                else:
                    nsafe_paid += 1
        tv0, ta0 = threat(head)
        rec = dict(r=r, len=L, head=list(head), kind=kind, dirs="".join("NESW"[x] for x in g.act_dirs) if kind == 0 else "",
                   nvis=len(vis), nvis_small=len(small_vis), reach0=tv0, reach0_all=ta0, nfree=nfree, nsafe=nsafe,
                   nsafe_all=nsafe_all, nsafe_free=nsafe_freeonly, nsafe_paid=nsafe_paid, d0_small=d0_small, rel=rel,
                   a3=a3, a6=a6, end=None, ate=0, fate=None, _mv=mv, _threat=threat, _sdist=sdist)
        if full:
            rec["sides"] = sides
            rec["en"] = en
            rec["tree"] = int(head in self.tree)
            rec["deg"] = b.degree(head)
            rec["froom"] = flood(b, set(occ), head, CAP)
            rec["body"] = [list(c) for c in q]
            rec["full"] = 1
        else:
            rec["en"] = [row for row in en if row[6]]
        self.cur[side] = rec
        (self.turns if full else self.enc)[side].append(rec)
        if full and vis:
            self.enc[side].append(rec)

    def close(self, side):
        """Fill in what the chosen move did; called when her action has been applied."""
        rec = self.cur[side]
        if rec is None or "_mv" not in rec:
            return
        threat, sdist = rec.pop("_threat"), rec.pop("_sdist")
        rec.pop("_mv")
        end = rec["end"]
        if end is not None:
            c = tuple(end)
            tv, ta = threat(c)
            rec["end_reach"], rec["end_reach_all"] = tv, ta
            rec["end_dsmall"] = sdist.get(c, -1) if rec["nvis_small"] else -1
        else:
            rec["end_reach"], rec["end_reach_all"] = rec["reach0"], rec["reach0_all"]
            rec["end_dsmall"] = rec["d0_small"]

    # ---------- hooks
    def round_start(self, g, r):
        for s in "AB":
            self.close(s)
            self.cur[s] = None if self.cur[s] is None else self.cur[s]
        self.round_heads = {d: (body[0], len(body)) for d, body in g.bodies.items()}

    def action(self, g, did, kind, nsteps):
        b = g.board
        for s in "AB":
            if did == b.queen[s]:
                self.close(s)
                self.snap(g, s, 2 if kind is None else kind)

    def moved(self, g, did, head, step_index, ate):
        b = g.board
        for s in "AB":
            if did == b.queen[s] and g.current == did and self.cur[s] is not None and self.cur[s]["r"] == g.round:
                self.cur[s]["end"] = list(head)
                self.cur[s]["ate"] += int(ate)

    def split(self, g, parent, child, before, plen, clen):
        self.parent[child] = (parent, g.round)
        b = g.board
        for s in "AB":
            if parent == b.queen[s] and self.cur[s] is not None and self.cur[s]["r"] == g.round:
                self.cur[s]["split"] = [before, plen, clen, child]

    def death(self, g, did, reason, length, body, actor):
        b = g.board
        s = g.teams[did]
        if reason == "headon" and actor is not None and actor != did:
            # in a head-on the dragon that was run into dies first: remember it for the mover's own record
            self.victim[actor] = [did, g.teams[did], length, body[0][0], body[0][1]]
        if did != b.queen[s]:
            return
        r = g.round
        rec = dict(round=r, reason=reason, len=length, pos=list(body[0]), own=int(actor == did))
        cur = self.cur[s]
        if actor == did:
            # her own action killed her: what did the fatal step run into?
            if g.act_kind == 0 and g.step_index < len(g.act_dirs):
                d = g.act_dirs[g.step_index]
                rec["step"] = g.step_index + 1
                rec["nsteps"] = len(g.act_dirs)
                rec["dir"] = "NESW"[d]
                ek = edge_key(b, body[0], d)
                rec["portal"] = int(ek in b.portal_pair)
                if ek in b.kelp:
                    rec["hit"] = ["K"]
                else:
                    c = b.step(body[0], d)
                    hit = None
                    for i, o in g.bodies.items():
                        for k, cc in enumerate(o):
                            if cc == c:
                                hit = [("o" if i == did else ("A" if k == 0 else "a") if g.teams[i] == s else ("E" if k == 0 else "e")),
                                       i, len(o), k, c[0], c[1]]
                                if i in self.parent:
                                    hit.append(list(self.parent[i]))
                                break
                        if hit:
                            break
                    if hit is None and reason == "headon" and did in self.victim:
                        v = self.victim[did]
                        hit = ["A" if v[1] == s else "E", v[0], v[2], 0, v[3], v[4]]
                    rec["hit"] = hit or ["?"]
            else:
                rec["act"] = "split" if g.act_kind == 1 else "suicide" if g.act_kind == 2 else "none" if g.act_kind is None else "move?"
        elif reason == "headon" and actor is not None:
            a_head, a_len = g.act_start
            start = self.round_heads.get(actor)
            k = dict(id=actor, team=g.teams[actor], len=a_len, steps=g.step_index + 1, nsteps=g.act_steps,
                     start=list(a_head), born=int(start is None), dirs="".join("NESW"[x] for x in g.act_dirs))
            if actor in self.parent:
                k["parent"] = list(self.parent[actor])
            k["cheb_now"] = b.cheb(a_head, body[0])
            # was its head in her view in her last turns (before this one)?
            hist = list(self.seen_hist[s])
            k["seen_last"] = int(bool(hist) and actor in hist[-1])
            k["seen_last3"] = int(any(actor in h for h in hist[-3:]))
            rec["killer"] = k
        if cur is not None:
            cur["fate"] = reason if actor == did else ("rammed" if g.teams.get(actor) != s else "ally")
        self.dth[s] = rec

    def end(self, g, rounds, winner, result):
        for s in "AB":
            self.close(s)
        self.rounds, self.winner = rounds, winner


def clean(rec):
    return {k: v for k, v in rec.items() if not k.startswith("_")}


def work(row):
    gid = row["game_id"]
    out = os.path.join(OUT, gid + ".json")
    try:
        if os.path.exists(out) and "--force" not in sys.argv:
            try:
                if json.load(open(out)).get("version") == VERSION:
                    return gid, None
            except ValueError:
                pass
        q = json.load(open(os.path.join(HERE, "q", gid + ".json")))
        deaths = {s: (q["sides"][s]["qdeath"]["round"] if q["sides"][s]["qdeath"] else None) for s in "AB"}
        h = H(deaths)
        g = lib.Walk(row["replay_path"])
        g.run(h)
        b = g.board
        data = dict(version=VERSION, game_id=int(gid), map=row["map"], w=b.w, h=b.h, rounds=h.rounds, winner=h.winner,
                    battle_id=row["battle_id"], end_type=row["end_type"],
                    sides={s: dict(team=int(row[f"team{s}Id"]), queen=b.queen[s], start=list(b.starts[b.queen[s]]),
                                   death=h.dth[s], turns=[clean(t) for t in h.turns[s]],
                                   enc=[clean(t) for t in h.enc[s] if "full" not in t]) for s in "AB"})
        tmp = out + ".tmp%d" % os.getpid()
        json.dump(data, open(tmp, "w"), separators=(",", ":"))
        os.replace(tmp, out)
        return gid, None
    except Exception as exc:  # noqa: BLE001
        import traceback
        return gid, traceback.format_exc()[-600:]


def wanted():
    rows = []
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if g[f"team{s}Id"] in TEAMS and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
                rows.append(g)
                break
    return rows


def show(gid, side):
    d = json.load(open(os.path.join(OUT, gid + ".json")))
    sd = d["sides"][side]
    print(f"game {gid} {d['map']} {d['w']}x{d['h']} run {d['battle_id']} winner {d['winner']} ({d['end_type']}); side {side} team {sd['team']} queen #{sd['queen']} start {sd['start']}")
    print("death:", json.dumps(sd["death"]))
    for t in sd["turns"]:
        print(f" r{t['r']:3d} L{t['len']} head {t['head']} {('move ' + t['dirs']) if t['kind'] == 0 else 'SPLIT' if t['kind'] == 1 else 'SUICIDE'} -> {t['end']} ate {t['ate']}"
              f" | free {t['nfree']} safe {t['nsafe']} (all {t['nsafe_all']}) paid-safe {t['nsafe_paid']} | vis {t['nvis']} reach0 {t['reach0']}/{t['reach0_all']} end_reach {t.get('end_reach')}/{t.get('end_reach_all')}"
              f" | froom {t.get('froom')} tree {t.get('tree')} deg {t.get('deg')} a3 {t['a3']} | fate {t['fate']}")
        print("      sides N,E,S,W:", t.get("sides"))
        if t["en"]:
            print("      enemies [id,len,x,y,cheb,path,inview,steps_to_her,reach,body_in_view]:", t["en"])


def main():
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "show":
        show(sys.argv[2], sys.argv[3])
        return
    rows = wanted()
    if "--only" in sys.argv:
        ids = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        rows = [r for r in rows if r["game_id"] in ids]
    if "--ownram" in sys.argv:
        # redo only the games in which a queen moved into a head herself (needs --force to overwrite)
        ids = set()
        for f in os.listdir(OUT):
            d = json.load(open(os.path.join(OUT, f)))
            if any(sd["death"] and sd["death"]["own"] and sd["death"]["reason"] == "headon" for sd in d["sides"].values()):
                ids.add(str(d["game_id"]))
        rows = [r for r in rows if r["game_id"] in ids]
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
    try:
        os.nice(10)
    except OSError:
        pass
    print("games:", len(rows), flush=True)
    errs = []
    with Pool(jobs) as pool:
        for i, (gid, err) in enumerate(pool.imap_unordered(work, rows, chunksize=4)):
            if err:
                errs.append((gid, err))
            if i % 200 == 0:
                print(i, flush=True)
    print("done; errors", len(errs))
    for e in errs[:10]:
        print(e[0], e[1])


if __name__ == "__main__":
    main()
