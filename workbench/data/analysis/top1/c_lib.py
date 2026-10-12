#!/usr/bin/env python3
"""c_lib.py: helpers for sub-session A3 (economy read). Read-only on replays.

Walk2 is lib.Walk with two more hook calls:
  hooks.pearl_new(g, cell, origin)   a pearl appears (origin ('natural',) or ('corpse', team, id, reason))
  hooks.turn(g, did)                 the dragon `did` is about to act (called before its action is applied)
Everything else is as in lib.py (coordinates x east, y south; directions 0=N 1=E 2=S 3=W).
"""
import csv
import sys
from collections import deque

sys.dont_write_bytecode = True
import lib  # noqa: E402
from lib import rp, REASONS  # noqa: E402

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
NAMES = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow", 19: "test4", 87: "WeHaveQuizzes"}


def tname(info, side):
    tid = int(info[f"team{side}Id"])
    return NAMES.get(tid, info[f"team{side}Name"][:16])


def battle_ok(g):
    """Build filter. `--battle a,b` keeps only games whose battle id (the run a game came from, the only trace of the
    bot build) contains one of the strings; `--notbattle a,b` drops those games. With neither option every game passes."""
    bid = g.get("battle_id", "")
    if "--battle" in sys.argv:
        if not any(k in bid for k in sys.argv[sys.argv.index("--battle") + 1].split(",")):
            return False
    if "--notbattle" in sys.argv:
        if any(k in bid for k in sys.argv[sys.argv.index("--notbattle") + 1].split(",")):
            return False
    return True


def battle_label():
    """Text for an output header that says which build filter was used."""
    out = ""
    if "--battle" in sys.argv:
        out += ", only runs " + sys.argv[sys.argv.index("--battle") + 1]
    if "--notbattle" in sys.argv:
        out += ", without runs " + sys.argv[sys.argv.index("--notbattle") + 1]
    return out


class Hooks2(lib.Hooks):
    def pearl_new(self, g, cell, origin):
        pass

    def turn(self, g, did):
        pass


class Stop(Exception):
    pass


class Walk2(lib.Walk):
    def run(self, hooks):
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
                    origin = ("corpse",) + last_dead if last_dead else ("natural",)
                    pearls[cell] = origin
                    if self.round >= 0:
                        hooks.pearl_new(self, cell, origin)
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
                    hooks.turn(self, did)
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


def multi_bfs(board, sources, limit=10 ** 9):
    """Path distance (kelp and portals respected, bodies ignored) from the nearest of several source cells."""
    dist = {}
    q = deque()
    for s in sources:
        if s not in dist:
            dist[s] = 0
            q.append(s)
    nb = board.nb
    while q:
        c = q.popleft()
        dc = dist[c]
        if dc >= limit:
            continue
        for n in nb(c):
            if n is not None and n not in dist:
                dist[n] = dc + 1
                q.append(n)
    return dist


def occupied(g):
    occ = set()
    for body in g.bodies.values():
        occ.update(body)
    return occ
