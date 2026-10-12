#!/usr/bin/env python3
"""Show the board at the START OF ONE DRAGON'S OWN TURN (not the start of the round), so that a counted case can be
checked by eye. Own renderer on lib.Walk.

  python3 x_eye.py <game_id> <round> <dragon_id> [radius]
  python3 x_eye.py --list file.json        (a JSON list of [game_id, round, dragon_id, note])

Legend: X = the dragon's head, x = its body; Q = enemy queen head, q = her body; O/o = other own head/body;
E/e = other enemy head/body; * pearl; . empty; | and - kelp; P portal edge. The 7x7 view is the inner square
(marked by the corner brackets). Columns are x (east), rows are y (south)."""
import json
import sys

import lib


class Stop(Exception):
    pass


class H(lib.Hooks):
    def __init__(self, rnd, did, radius):
        self.rnd, self.did, self.radius = rnd, did, radius
        self.text = None
        self.after = []
        self.armed = False

    def action(self, g, did, kind, nsteps):
        if self.armed:
            raise Stop()
        if g.round == self.rnd and did == self.did:
            self.text = render(g, did, self.radius)
            self.armed = True
            self.after.append("action: %s %s" % (("move", "split", "suicide")[kind] if kind is not None else "none",
                                                 "".join("NESW"[d] for d in g.act_dirs)))

    def moved(self, g, did, head, step_index, ate):
        if self.armed and did == self.did:
            self.after.append("  step %d -> %s%s" % (step_index, head, " (ate a pearl)" if ate else ""))

    def death(self, g, did, reason, length, body, actor):
        if self.armed:
            self.after.append("  DEATH of #%d (%s, team %s, length %d) reason %s" % (
                did, "QUEEN" if did in g.board.queen.values() else "dragon", g.teams[did], length, reason))

    def split(self, g, parent, child, before, plen, clen):
        if self.armed and parent == self.did:
            self.after.append("  split: keeps %d, child #%d gets %d" % (plen, child, clen))

    def round_start(self, g, r):
        if self.armed:
            raise Stop()


def render(g, did, radius):
    b = g.board
    body = g.bodies[did]
    side = g.teams[did]
    es = "B" if side == "A" else "A"
    hx, hy = body[0]
    cell = {}
    for d2, bd in g.bodies.items():
        own = g.teams[d2] == side
        isq = d2 == b.queen[g.teams[d2]]
        for i, c in enumerate(bd):
            if d2 == did:
                ch = "X" if i == 0 else "x"
            elif not own and isq:
                ch = "Q" if i == 0 else "q"
            elif own and isq:
                ch = "W" if i == 0 else "w"
            elif own:
                ch = "O" if i == 0 else "o"
            else:
                ch = "E" if i == 0 else "e"
            cell[c] = ch
    lines = []
    R = radius
    xs = [(hx + dx) % b.w for dx in range(-R, R + 1)]
    ys = [(hy + dy) % b.h for dy in range(-R, R + 1)]
    lines.append("      " + " ".join("%2d" % x for x in xs))
    for yi, y in enumerate(ys):
        # edge row above
        row = "      "
        for x in xs:
            key = (x, y, "N")
            row += (" - " if key in b.kelp else " P " if key in b.portal_pair else "   ")
        lines.append(row)
        row = "  %2d  " % y
        for x in xs:
            key = (x, y, "W")
            left = "|" if key in b.kelp else "P" if key in b.portal_pair else " "
            c = (x, y)
            ch = cell.get(c)
            if ch is None:
                ch = "*" if c in g.pearls else "."
            inview = b.cheb((hx, hy), c) <= 3
            row += left + ch + (" " if inview else "'")
        lines.append(row)
    heads = []
    for d2, bd in g.bodies.items():
        if b.cheb(body[0], bd[0]) <= R and d2 != did:
            heads.append("#%d%s L%d head%s%s" % (d2, g.teams[d2], len(bd), bd[0], " QUEEN" if d2 in b.queen.values() else ""))
    lines.append("  cells marked ' are outside the 7x7 view. Dragon #%d team %s length %d head %s, reach %d" % (
        did, side, len(body), body[0], lib.reach(len(body))))
    lines.append("  heads near: " + "; ".join(heads))
    return "\n".join(lines)


def show(gid, rnd, did, radius=4, note=""):
    games = {g["gid"]: g for g in json.load(open("x_out/games.json"))}
    g0 = games[gid]
    h = H(rnd, did, radius)
    w = lib.Walk(g0["path"])
    try:
        w.run(h)
    except Stop:
        pass
    print("=== game %d %s | A=%s B=%s | winner %s | round %d dragon #%d %s" % (gid, g0["map"], g0["An"], g0["Bn"], g0["winner"], rnd, did, note))
    print(h.text or "  (turn not found)")
    for a in h.after:
        print("  " + a)
    print()


if __name__ == "__main__":
    if sys.argv[1] == "--list":
        for item in json.load(open(sys.argv[2])):
            show(item[0], item[1], item[2], 4, item[3] if len(item) > 3 else "")
    else:
        show(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 4)
