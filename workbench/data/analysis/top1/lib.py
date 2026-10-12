#!/usr/bin/env python3
"""Replay walker for the top-team study (read-only on replays).

walk(path, hooks) streams one replay and keeps the full board state (every body,
every pearl with its origin). Coordinates: x east, y south, directions 0=N 1=E 2=S 3=W.
"""
import math
import sys
from collections import deque

sys.dont_write_bytecode = True
sys.path.insert(0, "~/01. Project/개인 프로젝트/battlecode")
import replay as rp  # noqa: E402

REASONS = ("wall", "self", "body", "headon", "noaction")
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


def reach(length):
    """Most steps a dragon can take in one turn: free ceil(L/4) plus paid L-2."""
    return math.ceil(length / 4) + max(0, length - 2)


class Board:
    def __init__(self, text):
        self.w = self.h = None
        self.name = "?"
        self.bodies, self.teams = {}, {}
        edges = {}
        for line in text.splitlines():
            p = line.split()
            if not p:
                continue
            if p[0] == "MAP":
                self.w, self.h = int(p[1]), int(p[2])
            elif p[0] == "MAP_NAME":
                self.name = " ".join(p[1:])
            elif p[0] == "DRAGON":
                did = len(self.bodies)
                self.teams[did] = "AB"[int(p[1])]
                self.bodies[did] = deque((int(p[3 + 2 * k]), int(p[4 + 2 * k])) for k in range(int(p[2])))
            elif p[0] == "EDGE":
                edges[int(p[1])] = (int(p[2]), int(p[3]) if len(p) > 3 else -1)
        w, h = self.w, self.h
        # canonical edge key: (x, y, 'N') = north side of tile, (x, y, 'W') = west side
        self.kelp, portal_of, by_id = set(), {}, {}
        for idx, (kind, pid) in edges.items():
            row, x = divmod(idx, w + 1)
            if row % 2 == 0:
                if x >= w:
                    continue
                key = (x, (row // 2) % h, "N")
            else:
                key = (x % w, (row // 2) % h, "W")
            if kind == 1:
                self.kelp.add(key)
            elif kind == 2:
                portal_of[key] = pid
                by_id.setdefault(pid, set()).add(key)
        self.portal_pair = {}
        for pid, keys in by_id.items():
            keys = list(keys)
            if len(keys) == 2:
                self.portal_pair[keys[0]] = keys[1]
                self.portal_pair[keys[1]] = keys[0]
        self.portal_cells = set()
        for (x, y, o) in self.portal_pair:
            self.portal_cells.add((x, y))
            self.portal_cells.add(((x - 1) % w, y) if o == "W" else (x, (y - 1) % h))
        self._nb = {}
        self._ball = {}
        self.starts = {d: b[0] for d, b in self.bodies.items()}
        self.queen = {s: min(d for d, t in self.teams.items() if t == s) for s in "AB"}

    def step(self, cell, d):
        """Destination of one step, None if kelp."""
        x, y = cell
        w, h = self.w, self.h
        if d == 0:
            key, side = (x, y, "N"), 0
        elif d == 2:
            key, side = (x, (y + 1) % h, "N"), 1
        elif d == 3:
            key, side = (x, y, "W"), 0
        else:
            key, side = ((x + 1) % w, y, "W"), 1
        if key in self.kelp:
            return None
        if key in self.portal_pair:
            px, py, o = self.portal_pair[key]
            if o == "N":
                return (px, (py - 1) % h) if side == 0 else (px, py)
            return ((px - 1) % w, py) if side == 0 else (px, py)
        return ((x + DX[d]) % w, (y + DY[d]) % h)

    def nb(self, cell):
        v = self._nb.get(cell)
        if v is None:
            v = self._nb[cell] = tuple(self.step(cell, d) for d in range(4))
        return v

    def bfs(self, src, limit):
        """Path distances (walls and portals respected, bodies ignored) up to limit."""
        dist = {src: 0}
        q = deque([src])
        while q:
            c = q.popleft()
            dc = dist[c]
            if dc >= limit:
                continue
            for n in self.nb(c):
                if n is not None and n not in dist:
                    dist[n] = dc + 1
                    q.append(n)
        return dist

    def ball(self, cell, r=4):
        """Cells within r steps: 41 in the open for r=4, small in corridors and nooks."""
        k = (cell, r)
        v = self._ball.get(k)
        if v is None:
            v = self._ball[k] = len(self.bfs(cell, r))
        return v

    def degree(self, cell):
        return sum(n is not None for n in self.nb(cell))

    def manhattan(self, a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return min(dx, self.w - dx) + min(dy, self.h - dy)

    def cheb(self, a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return max(min(dx, self.w - dx), min(dy, self.h - dy))


class Hooks:
    """Override what you need. `g` is the Walk object (g.board, g.bodies, g.teams, g.round)."""

    def round_start(self, g, r):
        pass

    def action(self, g, did, kind, nsteps):  # kind: 0 move, 1 split, 2 suicide
        pass

    def moved(self, g, did, head, step_index, ate):
        pass

    def split(self, g, parent, child, before, plen, clen):
        pass

    def death(self, g, did, reason, length, body, actor):
        pass

    def eat(self, g, did, cell, origin):  # origin: ('natural',) or ('corpse', team, id, reason)
        pass

    def sonar(self, g, sender, value, raw):  # one ping per direction; raw = the event struct
        pass

    def end(self, g, rounds, winner, result):
        pass


class Walk:
    def __init__(self, path):
        self.root = rp.load(path).root()
        self.board = Board(self.root.text(0))
        self.bodies = self.board.bodies
        self.teams = self.board.teams
        self.round = -1
        self.pearls = {}
        self.current = None
        self.act_start = None  # (head, length) of the acting dragon when its action began
        self.act_kind = None
        self.act_steps = 0
        self.act_dirs = []
        self.step_index = 0

    def run(self, hooks):
        b = self.board
        bodies, teams, pearls = self.bodies, self.teams, self.pearls
        last_dead = None
        for event in self.root.pointer(3):
            kind = event.u16(0)
            p = event.pointer(0)
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
            elif kind == 3:
                cell = rp.point(p.pointer(0))
                if p.bit(0):
                    pearls[cell] = ("corpse",) + last_dead if last_dead else ("natural",)
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
                if body[0] != head:
                    body.appendleft(head)
                while len(body) > 1 and body[-1] != tail:
                    body.pop()
                if did == self.current:
                    self.step_index += 1
                hooks.moved(self, did, head, self.step_index, len(body) > before)
            elif kind == 10:
                parent, child, side = p.i32(0), p.i32(4), "AB"[p.u16(8)]
                pb = deque(rp.point(v) for v in p.pointer(0))
                cb = deque(rp.point(v) for v in p.pointer(1))
                before = len(bodies[parent])
                bodies[parent], bodies[child] = pb, cb
                teams[parent] = teams[child] = side
                hooks.split(self, parent, child, before, len(pb), len(cb))
            elif kind == 11:
                did, reason = p.i32(0), p.u16(4)
                body = bodies[did]
                actor = self.current if self.current in bodies else None
                hooks.death(self, did, REASONS[reason] if reason < 5 else "other", len(body), body, actor)
                last_dead = (teams[did], did, REASONS[reason] if reason < 5 else "other")
                bodies.pop(did)
            elif kind == 12:
                sender = p.i32(0)
                hooks.sonar(self, sender, p.u64(16) if p.dwords >= 4 else p.u32(8), p)
        result = self.root.pointer(4)
        winner = "AB"[result.u16(6)] if result.u16(4) == 1 else None
        hooks.end(self, self.round + 1, winner, result)
        return self
