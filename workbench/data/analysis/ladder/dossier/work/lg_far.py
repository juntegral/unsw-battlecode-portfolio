"""Scratch (diag-longest): where each side's other dragons are relative to its longest, and beside whom the by-choice deaths fall.
Usage: python3 lg_far.py <tag>    tag = m1 m2 m3 b1 b2 q1 (online labels) | T (60 rank-1 games)
marks[r][s] = [top, alive, total, then for dragons other than the longest: count and length in distance bands to its head
(0-5, 6-15, 16-30, 31+), each split into may-feed (2 x length at most the longest) and too long].
feeds = by-choice deaths [round, side, length, distance to nearest mate at least twice as long, that mate's length, is that mate
the longest, distance to the longest, longest length, enemy heads within 4]."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
MARKS = (200, 250, 300, 350, 400, 425, 450, 475, 499)
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def scan(path, own_letter, info):
    root = replay.load(Path(path)).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 0 if 'AB'[int(q[1])] == own_letter else 1
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)

    def blocked(c, d):
        return edges.get(edge_id(w, h, c % w, c // w, d), (0, -1))[0] == 1

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    marks, feeds = {}, []
    rnd, actor, act = 0, None, 2

    def mark():
        out = []
        for s in (0, 1):
            mine = [(len(b), i, b[0]) for i, b in bodies.items() if teams[i] == s]
            if not mine:
                out.append(None)
                continue
            tl, ti, th = max(mine, key=lambda m: (m[0], -m[1]))
            row = [tl, len(mine), sum(m[0] for m in mine)] + [0] * 16
            for L, i, hd in mine:
                if i == ti:
                    continue
                d = man(hd, th)
                band = 0 if d <= 5 else 1 if d <= 15 else 2 if d <= 30 else 3
                k = 3 + band * 4 + (0 if 2 * L <= tl else 2)
                row[k] += 1
                row[k + 1] += L
            out.append(row)
        return out

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd in MARKS:
                marks[rnd] = mark()
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            act = 2
        elif k == 4:
            a = p.pointer(0)
            act = min(a.u16(0), 2) if a else 2
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
            teams[child] = teams[parent]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if reason == 4:
                s = teams[i]
                b = bodies[i]
                head, L = b[0], len(b)
                free = 0
                for d in range(4):
                    if blocked(head, d):
                        continue
                    dx, dy = STEP[d]
                    t = ((head // w + dy) % h) * w + (head % w + dx) % w
                    if not any(t in bb for bb in bodies.values()):
                        free = 1
                        break
                if free:
                    mates = [(man(head, bb[0]), len(bb), j) for j, bb in bodies.items() if teams[j] == s and j != i]
                    tl = max((m[1] for m in mates), default=0)
                    big = sorted(m for m in mates if m[1] >= 2 * L)
                    dtop = min((m[0] for m in mates if m[1] >= tl), default=99)
                    en4 = sum(1 for j, bb in bodies.items() if teams[j] != s and man(head, bb[0]) <= 4)
                    feeds.append([rnd, s, L, big[0][0] if big else 99, big[0][1] if big else 0, int(bool(big) and big[0][1] >= tl), dtop, tl, en4, act])
            bodies.pop(i)
    marks[499] = mark()
    out = dict(info)
    out.update(cells=w * h, w=w, h=h, last=rnd, marks=marks, feeds=feeds)
    return out


def main():
    tag = sys.argv[1]
    labels = dict(m1='agg7-m1', m2='agg7-m2', m3='agg7-m3', b1='agg7-b1', b2='agg7-b2', q1='agg8-q1')
    jobs = []
    if tag in labels:
        folder = Path('data/online/smoke') / (labels[tag] + '-new')
        for rp in sorted(folder.glob('M*.replay')):
            gid = int(rp.stem[1:])
            meta = json.loads((folder / ('game-%d.json' % gid)).read_text())
            own = 'A' if meta['teamAId'] == 1119 else 'B'
            other = 'B' if own == 'A' else 'A'
            jobs.append((rp, own, dict(game=gid, label=tag, map=meta['mapName'], opp=meta['team' + other + 'Name'], win=int(meta.get('winner', '').upper() == own))))
    elif tag == 'L':
        for line in Path('data/analysis/ladder/dossier/per-game.jsonl').read_text().splitlines():
            r = json.loads(line)
            if r['relation'] == 'us':
                jobs.append((r['replay'], r['our_side'], dict(game=r['game'], label='ladder', map=r['map_name'], opp=None, win=int(r['result'] == 'win'))))
    else:
        n = 0
        for line in Path('data/analysis/ladder/dossier/target/per-game-top1.jsonl').read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            n += 1
            if n % 10 == 0:
                jobs.append((r['replay'], r['our_side'], dict(game=r['game'], label='top1', map=r['map_name'], opp=None, win=int(r['result'] == 'win'))))
    out = []
    for n, (path, own, info) in enumerate(jobs):
        out.append(json.dumps(scan(path, own, info), separators=(',', ':')))
        if n % 10 == 9:
            print(n + 1, len(jobs), flush=True)
    body = '\n'.join(out) + '\n'
    if tag == 'm1':
        Path(WORK + 'lg_far-m1.jsonl').write_text(body)
    elif tag == 'm2':
        Path(WORK + 'lg_far-m2.jsonl').write_text(body)
    elif tag == 'm3':
        Path(WORK + 'lg_far-m3.jsonl').write_text(body)
    elif tag == 'b1':
        Path(WORK + 'lg_far-b1.jsonl').write_text(body)
    elif tag == 'b2':
        Path(WORK + 'lg_far-b2.jsonl').write_text(body)
    elif tag == 'q1':
        Path(WORK + 'lg_far-q1.jsonl').write_text(body)
    elif tag == 'L':
        Path(WORK + 'lg_far-L.jsonl').write_text(body)
    else:
        Path(WORK + 'lg_far-T.jsonl').write_text(body)
    print('done', tag, len(out))


main()
