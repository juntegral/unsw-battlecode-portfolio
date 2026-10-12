#!/usr/bin/env python3
"""Replay walker for sub-session A5 (the longest-dragon race). Read-only on replays.

A copy of the event loop of lib.Walk (same board, same event meanings) with three additions:
  * `occ`     : cell -> dragon id for every body segment on the board, kept up to date after every event;
  * `turn`    : hook called at the START of each dragon's own turn (before its action is applied);
  * `drop`    : hook called for every pearl that appears (origin ('natural',) or ('corpse', team, id, reason)).
Everything else (hooks action, moved, split, death, eat, sonar, end) is as in lib.py.

Also here: decode() for our own bot's leader broadcast (see e_belief.py), the game list helpers and a tiny
"no-portal component" flood fill.
"""
import csv
import math
import os
import sys
from collections import deque

sys.dont_write_bytecode = True
import lib  # noqa: E402
from lib import rp, REASONS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ME, VIB, SSS, FORGOT, T4, WHQ, DEV1 = 1119, 306, 91, 264, 19, 87, 545
TOP3 = (VIB, SSS, FORGOT)
NAMES = {ME: "meow", VIB: "Vibing++", SSS: "SSS", FORGOT: "forgot", T4: "test4", WHQ: "WeHaveQuizzes", DEV1: "dev test 1"}
LIVE_SETS = ("dl-20261003", "dl-20261004")


def decode(v):
    """Fields of our bot's leader broadcast, or None (zero value, or another message kind: bit 63 set)."""
    if v == 0 or (v >> 63):
        return None
    return (v & 0x7FFF, (v >> 16) & 0xFFF, (v >> 28) & 0x1FF, (v >> 37) & 0x7F, (v >> 44) & 0x7F, (v >> 53) & 3, bool(v & 0x8000))


class Hooks(lib.Hooks):
    def turn(self, g, did):
        pass

    def drop(self, g, cell, origin):
        pass


class Walk:
    def __init__(self, path):
        self.root = rp.load(path).root()
        self.board = lib.Board(self.root.text(0))
        self.bodies = self.board.bodies
        self.teams = self.board.teams
        self.round = -1
        self.pearls = {}
        self.current = None
        self.act_start = None
        self.act_kind = None
        self.act_tle = False
        self.act_steps = 0
        self.act_dirs = []
        self.step_index = 0
        self.seq = 0
        self.occ = {}
        for d, body in self.bodies.items():
            for c in body:
                self.occ[c] = d

    def run(self, hooks):
        bodies, teams, pearls, occ = self.bodies, self.teams, self.pearls, self.occ
        last_dead = None
        for event in self.root.pointer(3):
            kind = event.u16(0)
            p = event.pointer(0)
            self.seq += 1
            is_drop = kind == 3 and p.bit(0)
            if not is_drop:
                last_dead = None
            if kind == 0:
                self.round = p.i32(0)
                self.current = None
                hooks.round_start(self, self.round)
            elif kind == 1:
                self.current = p.i32(0)
                self.act_kind, self.act_steps, self.step_index = None, 0, 0
                body = bodies.get(self.current)
                self.act_start = (body[0], len(body)) if body else None
                if body:
                    hooks.turn(self, self.current)
            elif kind == 3:
                cell = rp.point(p.pointer(0))
                if p.bit(0):
                    origin = ("corpse",) + last_dead if last_dead else ("natural",)
                    pearls[cell] = origin
                    hooks.drop(self, cell, origin)
                else:
                    origin = pearls.pop(cell, ("unknown",))
                    if self.current in teams and self.round >= 0:
                        hooks.eat(self, self.current, cell, origin)
            elif kind == 4:
                did = p.i32(0)
                a = p.pointer(0)
                self.current = did
                body = bodies.get(did)
                self.act_start = (body[0], len(body)) if body else None
                self.act_kind = a.u16(0) if a is not None else None
                self.act_tle = p.bit(32)
                self.step_index = 0
                self.act_steps = 0
                self.act_dirs = []
                if self.act_kind == 0:
                    steps = a.pointer(0)
                    self.act_dirs = list(steps) if steps is not None else []
                    self.act_steps = len(self.act_dirs)
                if body:
                    hooks.action(self, did, self.act_kind, self.act_steps)
            elif kind == 9:
                did = p.i32(0)
                head, tail = rp.point(p.pointer(0)), rp.point(p.pointer(1))
                body = bodies[did]
                before = len(body)
                grew = False
                if body[0] != head:
                    body.appendleft(head)
                    grew = True
                while len(body) > 1 and body[-1] != tail:
                    c = body.pop()
                    if occ.get(c) == did:
                        del occ[c]
                if grew:
                    occ[head] = did
                if did == self.current:
                    self.step_index += 1
                hooks.moved(self, did, head, self.step_index, len(body) > before)
            elif kind == 10:
                parent, child, side = p.i32(0), p.i32(4), "AB"[p.u16(8)]
                pb = deque(rp.point(v) for v in p.pointer(0))
                cb = deque(rp.point(v) for v in p.pointer(1))
                before = len(bodies[parent])
                for c in bodies[parent]:
                    if occ.get(c) == parent:
                        del occ[c]
                bodies[parent], bodies[child] = pb, cb
                teams[parent] = teams[child] = side
                for c in pb:
                    occ[c] = parent
                for c in cb:
                    occ[c] = child
                hooks.split(self, parent, child, before, len(pb), len(cb))
            elif kind == 11:
                did, reason = p.i32(0), p.u16(4)
                body = bodies[did]
                actor = self.current if self.current in bodies else None
                hooks.death(self, did, REASONS[reason] if reason < 5 else "other", len(body), body, actor)
                last_dead = (teams[did], did, REASONS[reason] if reason < 5 else "other")
                for c in body:
                    if occ.get(c) == did:
                        del occ[c]
                bodies.pop(did)
            elif kind == 12:
                hooks.sonar(self, p.i32(0), p.u64(16) if p.dwords >= 4 else p.u32(8), p)
        result = self.root.pointer(4)
        winner = "AB"[result.u16(6)] if result.u16(4) == 1 else None
        hooks.end(self, self.round + 1, winner, result)
        return self


def free_neighbours(g, cell):
    """Cells next to `cell` (kelp and portals respected) that hold no body segment."""
    occ = g.occ
    return [n for n in g.board.nb(cell) if n is not None and n not in occ]


def noportal_components(board):
    """Label every cell with the id of its region when portals are treated as walls."""
    w, h = board.w, board.h
    comp = {}
    k = 0
    for x0 in range(w):
        for y0 in range(h):
            if (x0, y0) in comp:
                continue
            comp[(x0, y0)] = k
            q = deque([(x0, y0)])
            while q:
                x, y = q.popleft()
                for d, key in ((0, (x, y, "N")), (2, (x, (y + 1) % h, "N")), (3, (x, y, "W")), (1, ((x + 1) % w, y, "W"))):
                    if key in board.kelp or key in board.portal_pair:
                        continue
                    n = ((x + lib.DX[d]) % w, (y + lib.DY[d]) % h)
                    if n not in comp:
                        comp[n] = k
                        q.append(n)
            k += 1
    return comp


def load_games():
    """Rows of games.csv as dicts with ints where useful."""
    out = []
    for r in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        out.append(dict(gid=int(r["game_id"]), set=r["battle_id"], path=r["replay_path"], map=r["map"], cells=int(r["cells"]),
                        w=int(r["width"]), h=int(r["height"]), rounds=int(r["rounds"]), winner=r["winner"], end_type=r["end_type"],
                        A=int(r["teamAId"]), An=r["teamAName"], Ae=float(r["teamAElo"] or 0),
                        B=int(r["teamBId"]), Bn=r["teamBName"], Be=float(r["teamBElo"] or 0)))
    return out


def other(side):
    return "B" if side == "A" else "A"


def in_study(g, side):
    """The study's filter for `side`: the opponent is rated 2000+, map Schooltime left out."""
    return g[other(side) + "e"] >= 2000 and g["map"] != "Schooltime"


def build(g):
    """'live' for ladder downloads and the -old halves of smoke pairs, else the test build's name."""
    s = g["set"]
    if s in LIVE_SETS or s.endswith("-old"):
        return "live"
    for k in ("-test-new", "-dev1b-new", "-dev1-new", "-new"):
        if s.endswith(k):
            return s[: -len(k)]
    return s


def study_games():
    """Games in which meow or a top-three team is a side that passes the study filter."""
    return [g for g in load_games()
            if any(g[s] in (ME,) + TOP3 and in_study(g, s) for s in "AB")]


def wilson(k, n, z=1.2816):
    """80% Wilson interval."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def med(v):
    v = sorted(v)
    n = len(v)
    if not n:
        return None
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
