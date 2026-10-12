# Scratch (diag-stripes): per-turn, per-pearl and per-round rows for every game of one layout, whole game, both sides.
# Reads replays only. Writes st_rows-<tag>.jsonl (one JSON line per game) next to this script.
# Usage: python3 data/analysis/ladder/dossier/work/st_scan.py <layout prefix> <tag: stripes|portals|other>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
OUT_S = WORK + 'st_rows-stripes.jsonl'
OUT_P = WORK + 'st_rows-portals.jsonl'
OUT_O = WORK + 'st_rows-other.jsonl'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'no action')


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                    row.append((kind, dest))
                self.moves.append(row)
        # components without portals (kelp-bounded), the bot's "pocket"
        self.comp = [-1] * (w * h)
        self.size = []
        for c0 in range(w * h):
            if self.comp[c0] >= 0:
                continue
            n = len(self.size)
            self.comp[c0] = n
            q = deque([c0])
            k = 0
            while q:
                c = q.popleft()
                k += 1
                for kind, dest in self.moves[c]:
                    if kind == 0 and self.comp[dest] < 0:
                        self.comp[dest] = n
                        q.append(dest)
            self.size.append(k)
        # a component is a "loop" pocket when some portal edge has both of its tiles inside it and leads outside
        self.loop = [0] * len(self.size)
        for c in range(w * h):
            y, x = divmod(c, w)
            for d in range(4):
                kind, dest = self.moves[c][d]
                if kind != 2:
                    continue
                plain = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                if self.comp[plain] == self.comp[c] and self.comp[dest] != self.comp[c]:
                    self.loop[self.comp[c]] = 1


def scan(rec, geos):
    root = replay.load(Path(rec['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = rec['layout_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = rec['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    queens = {min(i for i in bodies if side(i) == s) for s in 'ut'}
    starts = set(bodies)
    parent = {}
    present = {}
    pearls = []
    turns, snaps = [], []
    rnd, actor, cur, started = 0, None, None, False

    def snapshot(n):
        row = [n]
        for s in 'ut':
            ls = [len(b) for i, b in bodies.items() if side(i) == s]
            row += [len(ls), sum(ls), max(ls, default=0)]
        snaps.append(row)

    def finish():
        nonlocal cur
        if cur is not None:
            turns.append(cur)
            cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            if started:
                snapshot(rnd)
            started = True
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            head = bodies[actor][0]
            occupied = {}
            for i, b in bodies.items():
                for n, c in enumerate(b):
                    occupied[c] = (i, n)
            opts = []
            for d in range(4):
                kind, dest = g.moves[head][d]
                if kind == 1:
                    opts.append(None)
                    continue
                cp = g.comp[dest]
                o = occupied.get(dest)
                opts.append([kind, dest, g.size[cp], g.loop[cp], int(dest in present),
                             sum(1 for c in present if g.comp[c] == cp) if g.size[cp] < 48 else -1,
                             0 if o is None else (1 if o[0] == actor else 2 if side(o[0]) == side(actor) else 3),
                             sum(1 for i, b in bodies.items() if i != actor and g.comp[b[0]] == cp) if g.size[cp] < 48 else -1])
            hc = g.comp[head]
            cur = dict(r=rnd, s=side(actor), id=actor, L=len(bodies[actor]), q=int(actor in queens), st=int(actor in starts),
                       head=head, hs=g.size[hc], hl=g.loop[hc], opts=opts, steps=[], dirs=[], ate=0, died=None, split=None,
                       kills=0, body=list(bodies[actor]),
                       nu=sum(side(i) == 'u' for i in bodies), nt=sum(side(i) == 't' for i in bodies))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                pr = dict(c=c, b=rnd, o='n' if actor is None else 'd', by=None, er=None, eid=None, eL=None, eq=None)
                present[c] = pr
                pearls.append(pr)
            else:
                pr = present.pop(c)
                pr['by'], pr['er'], pr['eid'] = side(actor), rnd, actor
                pr['eL'] = len(bodies[actor])
                pr['eq'] = int(actor in queens)
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != hd
            if moved and i == actor and cur is not None:
                old = b[0]
                dd = [d for d in range(4) if g.moves[old][d][0] != 1 and g.moves[old][d][1] == hd]
                cur['steps'].append(hd)
                cur['dirs'].append([dd[0] if dd else -1, int(bool(dd) and g.moves[old][dd[0]][0] == 2)])
            if moved:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c2 = p.i32(0), p.i32(4)
            for z, i in enumerate((a, c2)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            parent[c2] = a
            if cur is not None:
                cur['split'] = [c2, list(bodies[c2]), list(bodies[a])]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if cur is not None:
                if i == actor:
                    cur['died'] = CAUSE[reason]
                else:
                    cur['kills'] += 1
            bodies.pop(i)
    finish()
    snapshot(rnd)
    return dict(game=rec['game'], battle=rec['battle'], layout=key, result=rec['our_result'], rating=rec['opponent_rating'],
                ended_by=rec['ended_by'], last_round=rec['last_round'], our_side=ours, w=w, h=h,
                comp=g.comp, size=g.size, loop=g.loop, turns=turns, snaps=snaps, parent=parent,
                pearls=[[q['c'], q['b'], q['o'], q['by'], q['er'], q['eid'], q['eL'], q['eq']] for q in pearls])


def main():
    prefix, tag = sys.argv[1], sys.argv[2]
    recs = {}
    with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
        for line in f:
            r = json.loads(line)
            if r['relation'] == 'us' and r['layout_key'].startswith(prefix):
                recs[r['game']] = r
    geos = {}
    if tag == 'stripes':
        f = open(OUT_S, 'w')
    elif tag == 'portals':
        f = open(OUT_P, 'w')
    else:
        f = open(OUT_O, 'w')
    for n, gid in enumerate(sorted(recs)):
        f.write(json.dumps(scan(recs[gid], geos), separators=(',', ':')) + '\n')
    f.close()
    print('done', prefix, len(recs))


main()
