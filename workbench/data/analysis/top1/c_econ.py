#!/usr/bin/env python3
"""c_econ.py <game_id> [upto=150] [from=0]: economy of both teams per 10 rounds (sub-session A3).

Writes plain-text tables to stdout and the same numbers to c_out/ec_<game_id>_<from>_<upto>.json.
All "path" distances respect kelp, wrap and portals and ignore dragon bodies. "In view" = Chebyshev distance 3 or less
(the 7x7 square), wrapped.

Tables (one line per 10-round block, side A then side B):
 T1 economy : units and total length at block start; natural pearls eaten; corpse pearls eaten (own corpses / enemy
              corpses); natural pearls that appeared on the whole board in the block; natural pearls lying on the board
              at block start and how many of them are nearer (path) to an own head than to an enemy head.
 T2 units   : new dragons made by splits; deaths as: rammed by an enemy (victim), rammed an enemy (mover), ram between
              team-mates, non-ram with no free cell next to the head (boxed), non-ram with a free cell; segments lost.
 T3 spread  : board squares (8x8 grid) holding an own head; cells ever visited by an own head; mean / max path
              distance of heads from the own queen's spawn; share of heads with another own head within 6 path steps
              (mean over the rounds of the block); own heads standing on a "tight" cell (20 or fewer cells within 4 steps).
 T4 turns   : what every dragon-turn was: eat (ate a pearl), split, die, approach (a pearl in view, ended nearer to it),
              pass (a pearl in view, did not end nearer), new (no pearl in view, ended on a cell no own head had visited),
              old (no pearl in view, ended on a visited cell). Then: dragons that have not eaten for 20 rounds, and
              dragons whose head stood on 8 or fewer different cells at the last 16 round starts (loop), at block start.
 T5 pearls  : natural pearls that appeared within 6 path steps of an own head: how many, eaten by own team within 20
              rounds (mean rounds waited, mean distance at appearance), eaten by the enemy within 20, not eaten for 20;
              the same for the pearls where no enemy head was within 6 steps (uncontested); eats with another own head
              within 2 steps of the pearl (two heads on one pearl).
 T6 sprints : move orders with 2 or more steps: free ones and paid ones (segments paid), by purpose: pearl (ate),
              ram (ended in a head-on), flee (an enemy head in view at the start, further away at the end), other.
 T7 contact : dragon-turns with an enemy head in view; turns that began with an enemy head on a neighbouring cell
              and what the dragon did (ram / stepped away / died otherwise); of those that stepped away, how many were
              rammed within the next two rounds; pearls from ram corpses eaten by each side.
Then: splits (length before -> parent + child) with the wait since the dragon became 4 long, parent-child distance
5 and 10 rounds later, how far the child and the parent got from the split point, the share of the child's and the
parent's steps in the next 10 rounds that went to cells no own head had visited; non-ram deaths (cells, blockers);
natural pearls eaten by eater length; first contact round.
"""
import json
import math
import sys
from collections import Counter, defaultdict, deque

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import GAMES, Hooks2, Stop, Walk2, multi_bfs, tname  # noqa: E402

gid = sys.argv[1]
upto = int(sys.argv[2]) if len(sys.argv) > 2 else 150
start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 0
info = GAMES[gid]
HOT_RATE = 10       # a tile is a fountain ("hot") if it gave this many natural pearls per 500 rounds over all games read
LOOK = 20           # rounds a pearl is followed after it appears
VIEW_BFS = 8        # a pearl "in view" must also be within this many path steps
TIGHT = 20


def other(s):
    return "B" if s == "A" else "A"


class E(Hooks2):
    def __init__(self):
        self.c = Counter()                    # (block, side, key) -> n
        self.c2 = Counter()                   # (side, key) -> n
        self.rows = {}
        self.spawn = {}
        self.dspawn = {}
        self.visited = {"A": set(), "B": set()}
        self.lasteat = {}
        self.born = {}
        self.hist = defaultdict(lambda: deque(maxlen=16))
        self.reach4 = {}
        self.cur = None
        self.headcell = {}
        self.cellhead = {}
        self.pearl = {}                       # cell -> [round, dA, dB, flagged]
        self.splits = {"A": Counter(), "B": Counter()}
        self.wait = {"A": defaultdict(list), "B": defaultdict(list)}
        self.pend = []
        self.sep = {"A": defaultdict(list), "B": defaultdict(list)}
        self.child = {}
        self.parent = {}
        self.cells = {"A": Counter(), "B": Counter()}
        self.walls = {"A": Counter(), "B": Counter()}
        self.free_deaths = {"A": [], "B": []}
        self.eat_len = {"A": Counter(), "B": Counter()}
        self.first_contact = None
        self.declined = {}
        self.last_victim_team = None
        self.crowd = {"A": defaultdict(list), "B": defaultdict(list)}
        self.tight = {"A": defaultdict(list), "B": defaultdict(list)}
        self.age = {"A": defaultdict(list), "B": defaultdict(list)}
        self.half = {}
        # fountain ("hot") tiles: 10 or more natural pearls per 500 rounds in the pooled supply map of this map
        self.hot = set()
        try:
            sup = json.load(open("c_out/supply_%s.json" % info["map"].lower().replace(" ", "_")))
            for key, v in sup["cells"].items():
                if v / sup["games"] >= HOT_RATE:
                    x, y = key.split(",")
                    self.hot.add((int(x), int(y)))
        except FileNotFoundError:
            pass
        self.hot_half = {"A": set(), "B": set()}
        self.hot_seen = {"A": set(), "B": set()}
        self.hot_first_eat = {"A": {}, "B": {}}
        self._hotview = {}
        self.near_hot = set()
        self.adj_examples = {"A": [], "B": []}

    # ------------------------------------------------------------------ helpers
    def blk(self, g):
        return g.round // 10 * 10

    def on(self, g):
        return start_from <= g.round <= upto

    def hotview(self, b, cell):
        v = self._hotview.get(cell)
        if v is None:
            v = self._hotview[cell] = tuple(c for c in self.hot if b.cheb(cell, c) <= 3)
        return v

    def sync_heads(self, g):
        self.headcell = {d: body[0] for d, body in g.bodies.items()}
        self.cellhead = {c: d for d, c in self.headcell.items()}

    # ------------------------------------------------------------------ rounds
    def round_start(self, g, r):
        b = g.board
        self.finish(g)
        if r == 0 or not self.spawn:
            for s in "AB":
                self.spawn[s] = b.starts[b.queen[s]]
                self.dspawn[s] = b.bfs(self.spawn[s], 10 ** 9)
            for d, body in g.bodies.items():
                self.born.setdefault(d, 0)
                self.lasteat.setdefault(d, 0)
                if len(body) >= 4:
                    self.reach4.setdefault(d, 0)
            for c in self.hot:
                da = self.dspawn["A"].get(c, 10 ** 6)
                db = self.dspawn["B"].get(c, 10 ** 6)
                if da < db:
                    self.hot_half["A"].add(c)
                elif db < da:
                    self.hot_half["B"].add(c)
            self.near_hot = set(multi_bfs(b, list(self.hot), 3)) if self.hot else set()
        if r > upto + LOOK:
            raise Stop
        self.sync_heads(g)
        for d, body in g.bodies.items():
            self.visited[g.teams[d]].add(body[0])
            self.hist[d].append(body[0])
            hv = self.hotview(b, body[0])
            if hv:
                self.hot_seen[g.teams[d]].update(hv)
        if r == 0:
            for s in "AB":
                self.visited[s].update(body[0] for d, body in g.bodies.items() if g.teams[d] == s)
        # pearls not eaten for LOOK rounds
        for cell, rec in self.pearl.items():
            if not rec[3] and r - rec[0] >= LOOK:
                rec[3] = True
                if start_from <= rec[0] <= upto:
                    k = rec[0] // 10 * 10
                    for s, d in (("A", rec[1]), ("B", rec[2])):
                        if d is not None:
                            self.c[(k, s, "p_left")] += 1
                            if (rec[2] if s == "A" else rec[1]) is None:
                                self.c[(k, s, "pu_left")] += 1
        # split separation
        keep = []
        for rr, gap, parent, child, ph, ch in self.pend:
            if rr == r:
                if parent in g.bodies and child in g.bodies:
                    s = g.teams[parent]
                    dist = b.bfs(g.bodies[parent][0], 40)
                    self.sep[s][gap].append(dist.get(g.bodies[child][0], 41))
                    if gap == 10:
                        self.sep[s]["child from birth"].append(b.bfs(ch, 40).get(g.bodies[child][0], 41))
                        self.sep[s]["parent from split"].append(b.bfs(ph, 40).get(g.bodies[parent][0], 41))
                else:
                    s = g.teams.get(parent)
                    if s:
                        self.sep[s]["dead by +%d" % gap].append(1)
            else:
                keep.append((rr, gap, parent, child, ph, ch))
        self.pend = keep
        if not self.on(g):
            return
        heads = {s: [(d, body[0]) for d, body in g.bodies.items() if g.teams[d] == s] for s in "AB"}
        if self.first_contact is None:
            for d, c in heads["A"]:
                if any(b.cheb(c, c2) <= 3 for _, c2 in heads["B"]):
                    self.first_contact = r
                    break
        # crowding and tight cells, every round
        k = r // 10 * 10
        for s in "AB":
            hs = heads[s]
            cells = {c for _, c in hs}
            n = 0
            for d, c in hs:
                near = b.bfs(c, 6)
                if any(c2 in cells for c2 in near if c2 != c):
                    n += 1
            if hs:
                self.crowd[s][k].append(n / len(hs))
                self.tight[s][k].append(sum(1 for d, c in hs if b.ball(c, 4) <= TIGHT))
            self.c[(k, s, "heads_rounds")] += len(hs)
            self.c[(k, s, "heads_at_hot")] += sum(1 for d, c in hs if c in self.near_hot)
            self.c[(k, s, "heads_own_half")] += sum(1 for d, c in hs if self.dspawn[s].get(c, 10 ** 6) < self.dspawn[other(s)].get(c, 10 ** 6))
        if self.hot:
            occ = c_lib.occupied(g)
            for s in "AB":
                for c in self.hot_half[s]:
                    self.c[(k, s, "hot_lying" if c in g.pearls else "hot_body" if c in occ else "hot_empty")] += 1
        if r % 10 == 0:
            row = {}
            nat = [c for c, v in g.pearls.items() if v[0] == "natural"]
            dist = {s: multi_bfs(b, [c for _, c in heads[s]]) for s in "AB"}
            for s in "AB":
                o = other(s)
                ls = [(d, body) for d, body in g.bodies.items() if g.teams[d] == s]
                ds = [self.dspawn[s].get(body[0], 0) for d, body in ls]
                sq = {(body[0][0] * 8 // b.w, body[0][1] * 8 // b.h) for d, body in ls}
                lens = Counter(min(len(x[1]), 6) for x in ls)
                hungry = sum(1 for d, body in ls if r - max(self.lasteat.get(d, 0), self.born.get(d, 0)) >= 20)
                loop = sum(1 for d, body in ls if len(self.hist[d]) >= 16 and len(set(self.hist[d])) <= 8)
                nearer = sum(1 for c in nat if dist[s].get(c, 10 ** 6) < dist[o].get(c, 10 ** 6))
                row[s] = dict(units=len(ls), total=sum(len(x[1]) for x in ls), squares=len(sq),
                              visited=len(self.visited[s]), dmean=round(sum(ds) / max(1, len(ds)), 1),
                              dmax=max(ds) if ds else 0, lens=dict(sorted(lens.items())), hungry=hungry, loop=loop,
                              nearer=nearer, hot_own=len(self.hot_half[s]),
                              hot_seen=len(self.hot_seen[s] & self.hot_half[s]),
                              hot_seen_by_enemy=len(self.hot_seen[o] & self.hot_half[s]),
                              hot_eaten=len(set(self.hot_first_eat[s]) & self.hot_half[s]))
            row["nat"] = len(nat)
            self.rows[r] = row

    # ------------------------------------------------------------------ pearls
    def pearl_new(self, g, cell, origin):
        if origin[0] != "natural":
            return
        b = g.board
        near = b.bfs(cell, 6)
        d = {"A": None, "B": None}
        for did, c in self.headcell.items():
            if did in g.bodies and c in near:
                s = g.teams[did]
                if d[s] is None or near[c] < d[s]:
                    d[s] = near[c]
        self.pearl[cell] = [g.round, d["A"], d["B"], False]
        if self.on(g):
            k = self.blk(g)
            self.c[(k, "-", "spawned")] += 1
            for s in "AB":
                if d[s] is not None:
                    self.c[(k, s, "p_n")] += 1
                    if d[other(s)] is None:
                        self.c[(k, s, "pu_n")] += 1
            da = self.dspawn["A"].get(cell, 10 ** 6)
            db = self.dspawn["B"].get(cell, 10 ** 6)
            self.c[(k, "A" if da < db else "B" if db < da else "-", "spawn_half")] += 1

    def eat(self, g, did, cell, origin):
        s = g.teams[did]
        self.lasteat[did] = g.round
        cur = self.cur
        if cur and cur["did"] == did:
            cur["ate"] += 1
        k = self.blk(g)
        if origin[0] == "natural":
            rec = self.pearl.pop(cell, None)
            if self.on(g):
                self.c[(k, s, "nat")] += 1
                self.eat_len[s][min(g.act_start[1] if g.act_start else 0, 6)] += 1
                da = self.dspawn["A"].get(cell, 10 ** 6)
                db = self.dspawn["B"].get(cell, 10 ** 6)
                half = "A" if da < db else "B" if db < da else "-"
                self.c[(k, s, "nat_own_half" if half == s else "nat_enemy_half" if half == other(s) else "nat_mid")] += 1
                if cell in self.hot:
                    self.c[(k, s, "nat_hot")] += 1
                    self.c[(k, s, "nat_hot_own" if cell in self.hot_half[s] else "nat_hot_enemy")] += 1
                    self.hot_first_eat[s].setdefault(cell, g.round)
                # two heads on one pearl
                near = g.board.bfs(cell, 2)
                if any(d2 != did and g.teams.get(d2) == s and d2 in g.bodies and c2 in near
                       for d2, c2 in self.headcell.items()):
                    self.c[(k, s, "dup")] += 1
            if rec is not None:
                if self.on(g):
                    self.age[s][k].append(g.round - rec[0])
                if not rec[3] and start_from <= rec[0] <= upto:
                    kk = rec[0] // 10 * 10
                    wait = g.round - rec[0]
                    for side, d in (("A", rec[1]), ("B", rec[2])):
                        if d is None:
                            continue
                        unc = (rec[2] if side == "A" else rec[1]) is None
                        if side == s:
                            self.c[(kk, side, "p_own")] += 1
                            self.c[(kk, side, "p_wait")] += wait
                            self.c[(kk, side, "p_dist")] += d
                            if unc:
                                self.c[(kk, side, "pu_own")] += 1
                                self.c[(kk, side, "pu_wait")] += wait
                                self.c[(kk, side, "pu_dist")] += d
                        else:
                            self.c[(kk, side, "p_enemy")] += 1
                            if unc:
                                self.c[(kk, side, "pu_enemy")] += 1
        elif self.on(g):
            own = origin[0] == "corpse" and origin[1] == s
            self.c[(k, s, "corpse_own" if own else "corpse_enemy")] += 1
            if origin[0] == "corpse" and origin[3] == "headon":
                self.c[(k, s, "ramcorpse_own" if own else "ramcorpse_enemy")] += 1

    # ------------------------------------------------------------------ turns
    def turn(self, g, did):
        self.finish(g)
        body = g.bodies[did]
        s = g.teams[did]
        o = other(s)
        b = g.board
        head = body[0]
        rec = dict(did=did, s=s, L=len(body), head=head, round=g.round, ate=0, died=None, steps=0, new=0,
                   kind=None, nsteps=0, target=None, d0=None, adj=None, eview=[], on=self.on(g))
        if rec["on"]:
            # enemy heads in view / adjacent
            for d2, c2 in self.headcell.items():
                if d2 in g.bodies and g.teams[d2] == o and b.cheb(head, c2) <= 3:
                    rec["eview"].append((d2, c2))
            if rec["eview"]:
                for n in b.nb(head):
                    d2 = self.cellhead.get(n) if n is not None else None
                    if d2 is not None and d2 in g.bodies and g.teams[d2] == o and g.bodies[d2][0] == n:
                        rec["adj"] = (d2, len(g.bodies[d2]))
                        break
            # nearest pearl in view
            if g.pearls:
                dist = b.bfs(head, VIEW_BFS)
                best = None
                for c, dd in dist.items():
                    if c in g.pearls and b.cheb(head, c) <= 3 and (best is None or dd < best[0]):
                        best = (dd, c)
                if best:
                    rec["d0"], rec["target"] = best
                    # who else can get to that pearl: an own head strictly nearer, an enemy head as near or nearer
                    td = b.bfs(best[1], VIEW_BFS)
                    rec["tdist"] = td
                    mate = enemy = False
                    for d2, c2 in self.headcell.items():
                        if d2 == did or d2 not in g.bodies:
                            continue
                        dd = td.get(c2)
                        if dd is None:
                            continue
                        if g.teams[d2] == s:
                            if dd < best[0]:
                                mate = True
                        elif dd <= best[0]:
                            enemy = True
                    rec["rival"] = "enemy" if enemy else "mate" if mate else "free"
        self.cur = rec

    def action(self, g, did, kind, nsteps):
        cur = self.cur
        if cur and cur["did"] == did:
            cur["kind"], cur["nsteps"] = kind, nsteps

    def moved(self, g, did, head, step_index, ate):
        s = g.teams[did]
        old = self.headcell.get(did)
        if old is not None and self.cellhead.get(old) == did:
            del self.cellhead[old]
        self.headcell[did] = head
        self.cellhead[head] = did
        new = head not in self.visited[s]
        cur = self.cur
        if cur and cur["did"] == did:
            cur["steps"] += 1
            if new:
                cur["new"] += 1
        for label, table in (("child", self.child), ("parent", self.parent)):
            t = table.get(did)
            if t is not None and g.round <= t + 10:
                self.c2[(s, label + ("_new" if new else "_old"))] += 1
        self.visited[s].add(head)
        hv = self.hotview(g.board, head)
        if hv:
            self.hot_seen[s].update(hv)
        if ate and len(g.bodies[did]) >= 4:
            self.reach4.setdefault(did, g.round)
        if len(g.bodies[did]) < 4:
            self.reach4.pop(did, None)

    def split(self, g, parent, child, before, plen, clen):
        s = g.teams[parent]
        self.born[child] = g.round
        self.lasteat[child] = g.round
        ch = g.bodies[child][0]
        ph = g.bodies[parent][0]
        self.headcell[child] = ch
        self.cellhead[ch] = child
        cur = self.cur
        if cur and cur["did"] == parent:
            cur["split"] = True
        if self.on(g):
            k = self.blk(g)
            self.c[(k, s, "split")] += 1
            self.splits[s][(before, plen, clen)] += 1
            if parent in self.reach4:
                self.wait[s][before].append(g.round - self.reach4[parent])
            self.pend.append((g.round + 5, 5, parent, child, ph, ch))
            self.pend.append((g.round + 10, 10, parent, child, ph, ch))
            self.child[child] = g.round
            self.parent[parent] = g.round
        if plen >= 4:
            self.reach4[parent] = g.round
        else:
            self.reach4.pop(parent, None)
        if clen >= 4:
            self.reach4[child] = g.round

    def death(self, g, did, reason, length, body, actor):
        s = g.teams[did]
        b = g.board
        cur = self.cur
        if cur and cur["did"] == did:
            cur["died"] = reason
        c = self.headcell.pop(did, None)
        if c is not None and self.cellhead.get(c) == did:
            del self.cellhead[c]
        if reason == "headon" and did != actor:
            self.last_victim_team = s
            if did in self.declined and g.round - self.declined[did] <= 2 and self.on(g):
                self.c[(self.declined[did] // 10 * 10, s, "adj_then_rammed")] += 1
        if not self.on(g):
            return
        k = self.blk(g)
        if reason == "headon":
            if did == actor:
                friendly = self.last_victim_team == s
                key = "ram_friend" if friendly else "rammer"
            else:
                key = "ram_friend" if (actor is not None and g.teams.get(actor) == s) else "rammed"
            self.c[(k, s, key)] += 1
            self.c[(k, s, key + "_seg")] += length
        else:
            occ = set()
            for o2 in g.bodies.values():
                occ.update(o2)
            head = body[0]
            free = sum(1 for n in b.nb(head) if n is not None and n not in occ)
            key = "boxed" if free == 0 else "freedeath"
            self.c[(k, s, key)] += 1
            self.c[(k, s, key + "_seg")] += length
            nk = sum(1 for n in b.nb(head) if n is None)
            mine = set(body)
            na = sum(1 for n in b.nb(head) if n is not None and n in occ and n not in mine
                     and any(n in o2 for i2, o2 in g.bodies.items() if g.teams[i2] == s and i2 != did))
            ne = sum(1 for n in b.nb(head) if n is not None and n in occ and n not in mine) - na
            self.walls[s][f"kelp {nk}, own body {4 - nk - na - ne - free}, team-mate {na}, enemy {ne}, free {free}"] += 1
            self.cells[s][head] += 1
            if free:
                self.free_deaths[s].append((g.round, did, length, reason, head))

    # ------------------------------------------------------------------ end of a turn
    def finish(self, g):
        r = self.cur
        self.cur = None
        if not r or not r["on"]:
            return
        b = g.board
        s, did = r["s"], r["did"]
        k = r["round"] // 10 * 10
        alive = did in g.bodies
        head1 = g.bodies[did][0] if alive else None
        if r["died"]:
            state = "die"
        elif r["ate"]:
            state = "eat"
        elif r["kind"] == 1:
            state = "split"
        elif r["target"] is not None:
            d1 = r["tdist"].get(head1, 99) if alive else 99
            state = "approach" if d1 < r["d0"] else "pass"
            self.c[(k, s, f"t_{state}_{r['rival']}")] += 1
        else:
            state = "new" if r["new"] else "old"
        self.c[(k, s, "t_" + state)] += 1
        self.c[(k, s, "turns")] += 1
        if r["target"] is not None:
            self.c[(k, s, "turns_pearl_in_view")] += 1
            if state in ("eat", "die", "split"):
                self.c[(k, s, f"t_{state}_view_{r['rival']}")] += 1
        if r["eview"]:
            self.c[(k, s, "t_enemy_in_view")] += 1
            if alive and not r["died"]:
                e0 = min(b.cheb(r["head"], c2) for _, c2 in r["eview"])
                e1 = min(b.cheb(head1, c2) for _, c2 in r["eview"])
                self.c[(k, s, "ev_farther" if e1 > e0 else "ev_nearer" if e1 < e0 else "ev_same")] += 1
                # the same for small dragons facing an enemy that is not longer than they are
                if r["L"] <= 4:
                    self.c[(k, s, "evs_farther" if e1 > e0 else "evs_nearer" if e1 < e0 else "evs_same")] += 1
            elif r["died"] == "headon":
                self.c[(k, s, "ev_rammed_it")] += 1
            else:
                self.c[(k, s, "ev_died")] += 1
        # sprints
        if r["kind"] == 0 and r["nsteps"] >= 2:
            free = -(-r["L"] // 4)
            paid = max(0, r["steps"] - free)      # steps really taken; a step that ends in a death is not paid
            if r["died"] == "headon":
                why = "ram"
            elif r["ate"]:
                why = "pearl"
            elif r["eview"] and alive and min(b.cheb(head1, c2) for _, c2 in r["eview"]) > min(b.cheb(r["head"], c2) for _, c2 in r["eview"]):
                why = "flee"
            else:
                why = "other"
            self.c[(k, s, "multi")] += 1
            self.c[(k, s, "multi_" + why)] += 1
            if paid:
                self.c[(k, s, "paidmoves")] += 1
                self.c[(k, s, "paidsegs")] += paid
                self.c[(k, s, "paid_" + why)] += paid
        # adjacent enemy head
        if r["adj"]:
            if r["died"] == "headon":
                out = "ram"
            elif r["died"]:
                out = "died"
            else:
                out = "away"
                self.declined[did] = r["round"]
            self.c[(k, s, "adj")] += 1
            self.c[(k, s, "adj_" + out)] += 1
            cls = "le" if r["L"] <= r["adj"][1] else "gt"
            self.c[(k, s, f"adj_{out}_{cls}")] += 1
            if len(self.adj_examples[s]) < 400:
                self.adj_examples[s].append((r["round"], did, r["L"], r["head"], r["adj"][0], r["adj"][1], out,
                                             "split" if r["kind"] == 1 else "move"))

    def end(self, g, rounds, winner, result):
        self.finish(g)


e = E()
g = Walk2(info["replay_path"])
try:
    g.run(e)
except Stop:
    pass
c = e.c
nm = {s: tname(info, s) for s in "AB"}
print(f"=== ECON {gid} {info['map']} ({info['width']}x{info['height']}) | A = {nm['A']} ({info['teamAId']}, {info['teamAElo']}) "
      f"B = {nm['B']} ({info['teamBId']}, {info['teamBElo']}) | winner {info['winner']} by {info['end_type']} | "
      f"queen spawns {e.spawn} | first contact (heads in view of each other) round {e.first_contact}")
blocks = [r for r in sorted(e.rows) if start_from <= r <= upto]


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


out = {"gid": gid, "map": info["map"], "names": nm, "first_contact": e.first_contact, "blocks": {}}
for r in blocks:
    out["blocks"][r] = {}
    for s in "AB":
        d = dict(e.rows[r][s])
        for (k, s2, key), v in c.items():
            if k == r and s2 == s:
                d[key] = v
        d["crowd"] = round(mean(e.crowd[s][r]), 3)
        d["tight"] = round(mean(e.tight[s][r]), 2)
        d["age"] = round(mean(e.age[s][r]), 2)
        d["board_nat"] = e.rows[r]["nat"]
        d["spawned"] = c[(r, "-", "spawned")]
        d["spawn_half_own"] = c[(r, s, "spawn_half")]
        out["blocks"][r][s] = d

print("\nT1 economy | units total | ate: natural, corpse (own corpses / enemy corpses) | natural eaten in own half / enemy half | "
      "natural pearls that appeared: board total, in own half | lying at block start: board total, nearer to own heads | mean age of the natural pearls eaten")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        parts.append(f"{s}: {d['units']:2d}u {d['total']:3d}t | nat {d.get('nat', 0):3d} cor {d.get('corpse_own', 0):2d}/{d.get('corpse_enemy', 0):2d} | "
                     f"half {d.get('nat_own_half', 0):3d}/{d.get('nat_enemy_half', 0):2d} | app {d['spawned']:3d},{d['spawn_half_own']:3d} | "
                     f"lying {d['board_nat']:3d},{d['nearer']:3d} | age {d['age']:4.1f}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT2 units | new dragons (splits) | rammed by enemy n/segments | rammed an enemy n/seg | team-mate ram n | boxed non-ram n/seg | non-ram with a free cell n/seg")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        parts.append(f"{s}: {d['units']:2d}u | +{d.get('split', 0):2d} | hit {d.get('rammed', 0):2d}/{d.get('rammed_seg', 0):2d} | "
                     f"rams {d.get('rammer', 0):2d}/{d.get('rammer_seg', 0):2d} | fr {d.get('ram_friend', 0):2d} | "
                     f"boxed {d.get('boxed', 0):2d}/{d.get('boxed_seg', 0):2d} | free {d.get('freedeath', 0):2d}/{d.get('freedeath_seg', 0):2d}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT3 spread | squares of 64 with an own head | cells visited | mean / max path distance of heads from own queen spawn | "
      "share of heads with another own head within 6 steps | own heads on tight cells (mean per round)")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        parts.append(f"{s}: sq {d['squares']:2d} | vis {d['visited']:4d} | dist {d['dmean']:5.1f}/{d['dmax']:3d} | crowd {d['crowd']:.2f} | tight {d['tight']:4.1f}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT4 turns | dragon-turns | eat / split / die / approach / pass / new / old (share of turns, %) | turns with a pearl in view % | "
      "not eaten for 20 rounds | loop (at block start)")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        t = max(1, d.get("turns", 0))
        sh = [100 * d.get("t_" + x, 0) / t for x in ("eat", "split", "die", "approach", "pass", "new", "old")]
        parts.append(f"{s}: {d.get('turns', 0):4d} | " + "/".join(f"{x:2.0f}" for x in sh) +
                     f" | view {100 * d.get('turns_pearl_in_view', 0) / t:3.0f} | hungry {d['hungry']:2d} | loop {d['loop']:2d}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT5 pearls that appeared within 6 steps of an own head | n | eaten by own within 20 rounds (mean wait, mean distance at appearance) | "
      "eaten by enemy | left for 20 rounds || uncontested (no enemy head within 6): n | own (wait, dist) | enemy | left || two own heads within 2 steps of an eaten pearl")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        po, pu = d.get("p_own", 0), d.get("pu_own", 0)
        parts.append(f"{s}: {d.get('p_n', 0):3d} | own {po:3d} ({d.get('p_wait', 0) / max(1, po):4.1f}, {d.get('p_dist', 0) / max(1, po):3.1f}) | "
                     f"en {d.get('p_enemy', 0):2d} | left {d.get('p_left', 0):2d} || unc {d.get('pu_n', 0):3d} | own {pu:3d} "
                     f"({d.get('pu_wait', 0) / max(1, pu):4.1f}, {d.get('pu_dist', 0) / max(1, pu):3.1f}) | en {d.get('pu_enemy', 0):2d} | left {d.get('pu_left', 0):2d} || dup {d.get('dup', 0):2d}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT6 sprints | move orders of 2+ steps | by purpose pearl / ram / flee / other | paid moves / segments paid | segments paid by purpose pearl / ram / flee / other")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        parts.append(f"{s}: multi {d.get('multi', 0):3d} | {d.get('multi_pearl', 0):3d}/{d.get('multi_ram', 0):2d}/{d.get('multi_flee', 0):2d}/{d.get('multi_other', 0):3d} | "
                     f"paid {d.get('paidmoves', 0):2d}/{d.get('paidsegs', 0):2d} | {d.get('paid_pearl', 0):2d}/{d.get('paid_ram', 0):2d}/{d.get('paid_flee', 0):2d}/{d.get('paid_other', 0):2d}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\nT7 contact | turns with an enemy head in view (% of turns) | turns that began with an enemy head on a neighbouring cell: n -> rammed it / stepped away / died otherwise | "
      "stepped away and was rammed within 2 rounds | by length: own <= enemy rammed/away, own > enemy rammed/away | pearls of ram corpses eaten: own corpses / enemy corpses")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        t = max(1, d.get("turns", 0))
        parts.append(f"{s}: view {100 * d.get('t_enemy_in_view', 0) / t:3.0f}% | adj {d.get('adj', 0):2d} -> {d.get('adj_ram', 0):2d}/{d.get('adj_away', 0):2d}/{d.get('adj_died', 0):2d} | "
                     f"then hit {d.get('adj_then_rammed', 0):2d} | le {d.get('adj_ram_le', 0):2d}/{d.get('adj_away_le', 0):2d} gt {d.get('adj_ram_gt', 0):2d}/{d.get('adj_away_gt', 0):2d} | "
                     f"ramcorpse {d.get('ramcorpse_own', 0):2d}/{d.get('ramcorpse_enemy', 0):2d}")
    print(f"  r{r:3d} | " + " || ".join(parts))

print(f"\nT8 fountains (tiles with {HOT_RATE}+ natural pearls per 500 rounds over all games on this map: {len(e.hot)} tiles, {len(e.hot_half['A'])} nearer to A's spawn, {len(e.hot_half['B'])} nearer to B's) | "
      "own-half fountains: seen so far by own team / eaten from by own team / seen by the enemy | own-half fountain tile-rounds in the block: a pearl lying % / a body on it % / empty % | "
      "natural pearls eaten on own-half fountains / on enemy-half fountains / on other tiles | share of own heads within 3 steps of a fountain % | share of own heads in own half %")
for r in blocks:
    parts = []
    for s in "AB":
        d = out["blocks"][r][s]
        tr = max(1, d.get("hot_lying", 0) + d.get("hot_body", 0) + d.get("hot_empty", 0))
        hr = max(1, d.get("heads_rounds", 0))
        parts.append(f"{s}: seen {d['hot_seen']:2d} ate {d['hot_eaten']:2d} en {d['hot_seen_by_enemy']:2d} of {d['hot_own']:2d} | "
                     f"lying {100 * d.get('hot_lying', 0) / tr:3.0f} body {100 * d.get('hot_body', 0) / tr:3.0f} empty {100 * d.get('hot_empty', 0) / tr:3.0f} | "
                     f"nat {d.get('nat_hot_own', 0):3d}/{d.get('nat_hot_enemy', 0):3d}/{d.get('nat', 0) - d.get('nat_hot', 0):3d} | "
                     f"at {100 * d.get('heads_at_hot', 0) / hr:3.0f}% | home {100 * d.get('heads_own_half', 0) / hr:3.0f}%")
    print(f"  r{r:3d} | " + " || ".join(parts))

print("\n  length histogram of living dragons at each block start (6 = 6 or longer):")
for r in blocks:
    print(f"    r{r:3d} A {e.rows[r]['A']['lens']} | B {e.rows[r]['B']['lens']}")

tot = {}
for s in "AB":
    t = Counter()
    for r in blocks:
        for key, v in out["blocks"][r][s].items():
            if isinstance(v, (int, float)) and key not in ("units", "total", "squares", "visited", "dmean", "dmax", "hungry", "loop", "nearer", "board_nat", "crowd", "tight", "age"):
                t[key] += v
    tot[s] = t
    out.setdefault("totals", {})[s] = dict(t)
    name = nm[s]
    turns = max(1, t["turns"])
    print(f"\n  {s} ({name}) totals rounds {start_from}-{upto}: natural {t['nat']} (own half {t['nat_own_half']}, enemy half {t['nat_enemy_half']}), "
          f"corpse own/enemy {t['corpse_own']}/{t['corpse_enemy']}, splits {t['split']}, rammed {t['rammed']} ({t['rammed_seg']} seg), "
          f"rammer {t['rammer']} ({t['rammer_seg']} seg), boxed {t['boxed']} ({t['boxed_seg']} seg), free-cell deaths {t['freedeath']} ({t['freedeath_seg']} seg)")
    print(f"     turns {t['turns']}: eat {100 * t['t_eat'] / turns:.1f}% split {100 * t['t_split'] / turns:.1f}% die {100 * t['t_die'] / turns:.1f}% "
          f"approach {100 * t['t_approach'] / turns:.1f}% pass {100 * t['t_pass'] / turns:.1f}% new {100 * t['t_new'] / turns:.1f}% old {100 * t['t_old'] / turns:.1f}% | "
          f"pearl in view {100 * t['turns_pearl_in_view'] / turns:.1f}% | enemy head in view {100 * t['t_enemy_in_view'] / turns:.1f}% | natural pearls per 100 turns {100 * t['nat'] / turns:.2f}")
    po, pu = max(1, t["p_own"]), max(1, t["pu_own"])
    print(f"     pearls appearing within 6 steps: {t['p_n']}: own {t['p_own']} (wait {t['p_wait'] / po:.1f}, dist {t['p_dist'] / po:.1f}), enemy {t['p_enemy']}, left {t['p_left']} | "
          f"uncontested {t['pu_n']}: own {t['pu_own']} (wait {t['pu_wait'] / pu:.1f}, dist {t['pu_dist'] / pu:.1f}), enemy {t['pu_enemy']}, left {t['pu_left']} | two heads on one pearl {t['dup']}")
    print(f"     2+ step moves {t['multi']} (pearl {t['multi_pearl']}, ram {t['multi_ram']}, flee {t['multi_flee']}, other {t['multi_other']}); paid segments {t['paidsegs']} "
          f"(pearl {t['paid_pearl']}, ram {t['paid_ram']}, flee {t['paid_flee']}, other {t['paid_other']})")
    print(f"     enemy head on a neighbouring cell at turn start: {t['adj']} -> rammed {t['adj_ram']}, stepped away {t['adj_away']} (then rammed within 2 rounds: {t['adj_then_rammed']}), died otherwise {t['adj_died']}; "
          f"own<=enemy: ram {t['adj_ram_le']} away {t['adj_away_le']}; own>enemy: ram {t['adj_ram_gt']} away {t['adj_away_gt']}")
    print(f"     ram-corpse pearls eaten: from own corpses {t['ramcorpse_own']}, from enemy corpses {t['ramcorpse_enemy']}")
    sp = e.splits[s]
    print("     splits (before -> parent + child: n; mean rounds since the dragon became 4+): " +
          ", ".join(f"{a}->{p}+{ch}: {n}" for (a, p, ch), n in sorted(sp.items())) + " | wait by length before: " +
          ", ".join(f"L{a}: {mean(v):.1f} (n {len(v)})" for a, v in sorted(e.wait[s].items())))
    sep = e.sep[s]
    print(f"     parent-child path distance after 5 rounds: n {len(sep[5])} mean {mean(sep[5]):.1f}; after 10: n {len(sep[10])} mean {mean(sep[10]):.1f}; "
          f"child from its birth cell after 10: {mean(sep['child from birth']):.1f}; parent from the split cell after 10: {mean(sep['parent from split']):.1f}; "
          f"pairs with one dead by +5: {len(sep['dead by +5'])}, by +10: {len(sep['dead by +10'])}")
    cn, co = e.c2[(s, "child_new")], e.c2[(s, "child_old")]
    pn, pold = e.c2[(s, "parent_new")], e.c2[(s, "parent_old")]
    print(f"     steps in the 10 rounds after a split onto cells no own head had visited: child {cn} of {cn + co} ({100 * cn / max(1, cn + co):.0f}%), parent {pn} of {pn + pold} ({100 * pn / max(1, pn + pold):.0f}%)")
    rep = sum(n for cc, n in e.cells[s].items() if n >= 2)
    print(f"     non-ram deaths: {sum(e.cells[s].values())} on {len(e.cells[s])} cells; {rep} on cells used twice or more; most used {e.cells[s].most_common(6)}")
    print(f"     blockers in those deaths: {dict(e.walls[s].most_common(6))}")
    print(f"     non-ram deaths with a free cell: {e.free_deaths[s][:12]}")
    print(f"     natural pearls eaten by eater length (6 = 6+): {dict(sorted(e.eat_len[s].items()))}")
    out["totals"][s]["splits"] = {f"{a}->{p}+{ch}": n for (a, p, ch), n in sp.items()}
    out["totals"][s]["sep5"] = round(mean(sep[5]), 2)
    out["totals"][s]["sep10"] = round(mean(sep[10]), 2)
    out["totals"][s]["child_new_share"] = round(cn / max(1, cn + co), 3)
    out["totals"][s]["parent_new_share"] = round(pn / max(1, pn + pold), 3)
    out["totals"][s]["adj_examples"] = e.adj_examples[s][:400]
json.dump(out, open(f"c_out/ec_{gid}_{start_from}_{upto}.json", "w"))
