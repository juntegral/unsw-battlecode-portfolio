"""Scratch (diag-topaah): steps per turn by dragon length, what a sprint is for, length histograms, and a plain
timeline of one game. Side 0 = the studied team.
Usage: python3 ta_s2.py scan <tag> [limit]     tags as ta_scan.py (a a0 l c1 g q m t cs = every 6th of 306 old)
       python3 ta_s2.py view <gid> <team> [last_round] [grid rounds, comma separated]"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own body', 'another body', 'head-on', 'no valid action')


def geo(w, h, raw):
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    moves = []
    for y in range(h):
        for x in range(w):
            row = []
            for d in range(4):
                dx, dy = STEP[d]
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                row.append((kind, dest))
            moves.append(row)
    return moves


def process(path, meta, focus, view=0, grids=()):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    moves = geo(w, h, raw)
    fteam = 0 if meta['a'] == focus else 1
    side = lambda i: 0 if teams[i] == fteam else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    qstart = [bodies[queens[s]][0] for s in (0, 1)]

    def tman(a, b):
        ay, ax = divmod(a, w)
        by, bx = divmod(b, w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, w - dx) + min(dy, h - dy)

    T = [[Counter() for _ in range(3)] for _ in (0, 1)]
    hist = {}
    rams = []
    pearls = set()
    rnd, actor, W = 0, None, 0
    dirs, used, nsteps, akind = [], 0, 0, 2
    cur = None
    dec = [Counter(), Counter()]
    notes = []
    turn_deaths = []
    started = False
    out = []

    def close_turn():
        nonlocal cur
        hs = [d for d in turn_deaths if d[2] == 3]
        if len(hs) == 2:
            mv = [d for d in hs if d[0] == actor][0]
            ht = [d for d in hs if d[0] != actor][0]
            if mv[1] != ht[1]:
                longest = max([len(b) for i, b in bodies.items() if side(i) == ht[1]] + [ht[3]])
                rams.append([rnd, mv[1], mv[3], ht[3], nsteps, max(0, nsteps - (mv[3] + 3) // 4), int(ht[4]), int(ht[3] >= longest)])
                dec[mv[1]]['ram'] += 1
                if view and ht[4]:
                    notes.append('r%d: %s queen (len %d) rammed and killed by a %d-long' % (rnd, 'THEIR' if ht[1] else 'OUR', ht[3], mv[3]))
        turn_deaths.clear()
        if cur is not None:
            s, L, n, eat, died = cur
            c = T[s][W]
            Lc = min(L, 15)
            c['t%d_%d' % (Lc, min(n, 4))] += 1
            if n > 1:
                c['sp_eat' if eat else 'sp_ram' if died == 3 else 'sp_die' if died >= 0 else 'sp_plain'] += 1
                c['sp_straight'] += int(len(set(dirs)) == 1)
                c['paid%d' % Lc] += max(0, n - (L + 3) // 4)
                c['sp_paid_turns'] += int(n > (L + 3) // 4)
                if n > (L + 3) // 4:
                    c['paid_eat' if eat else 'paid_ram' if died == 3 else 'paid_die' if died >= 0 else 'paid_plain'] += 1
            c['e%d_%d' % (Lc, int(n > 1))] += eat
            cur = None

    def line():
        row = []
        for s in (0, 1):
            ls = sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)
            q = bodies.get(queens[s])
            qtxt = 'dead' if not q else '(%d,%d) len %d, %d from start, %d own/%d enemy heads within 5' % (
                q[0] % w, q[0] // w, len(q), tman(q[0], qstart[s]),
                sum(1 for i, b in bodies.items() if side(i) == s and i != queens[s] and tman(b[0], q[0]) <= 5),
                sum(1 for i, b in bodies.items() if side(i) != s and tman(b[0], q[0]) <= 5))
            d = dec[s]
            row.append('%s n=%d total=%d top=%s | queen %s | last 10 rounds: splits %d, pearls %d, sprints %d (paid %d), deaths %d [%s], rams started %d' % (
                ('US  ', 'THEM')[s], len(ls), sum(ls), ls[:8], qtxt, d['split'], d['eat'], d['sprint'], d['paidturn'], d['death'],
                ' '.join('%s %d' % (k[2:], v) for k, v in sorted(d.items()) if k.startswith('d_')), d['ram']))
        out.append('--- after round %d' % rnd)
        out.extend(row)
        out.extend('    ' + n for n in notes)
        notes.clear()
        dec[0].clear()
        dec[1].clear()

    def grid():
        g = [['.'] * w for _ in range(h)]
        for t in pearls:
            g[t // w][t % w] = '*'
        for i, b in bodies.items():
            s = side(i)
            for z, t in enumerate(b):
                ch = ('o', 'x')[s] if z else (('Q' if i == queens[0] else 'A') if s == 0 else ('K' if i == queens[1] else 'X'))
                g[t // w][t % w] = ch
        out.append('grid after round %d (A/o = studied team, Q its queen; X/x = opponent, K its queen; * pearl)' % rnd)
        out.extend(''.join(r) for r in g)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            close_turn()
        if k == 0:
            if started:
                if rnd in (100, 150, 200, 300):
                    hist[str(rnd)] = [dict(Counter(min(len(b), 20) for i, b in bodies.items() if side(i) == s)) for s in (0, 1)]
                if view and rnd <= view and (rnd % 10 == 9 or rnd in grids):
                    if rnd % 10 == 9:
                        line()
                    if rnd in grids:
                        grid()
            started = True
            rnd, actor = p.i32(0), None
            W = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
            if view and rnd > view:
                break
        elif k == 1:
            actor = p.i32(0)
            dirs, used, nsteps, akind = [], 0, 0, 2
            s = side(actor)
            cur = [s, len(bodies[actor]), 0, 0, -1]
            c = T[s][W]
            alive = sum(1 for i in bodies if side(i) == s)
            c['turns'] += 1
            c['cap_turns'] += int(alive >= 60)
        elif k == 4:
            a = p.pointer(0)
            akind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and akind == 0 and a.pointer(0) is not None else []
            nsteps = len(dirs)
            if cur is not None:
                cur[2] = nsteps
                if nsteps > 1:
                    dec[cur[0]]['sprint'] += 1
                    dec[cur[0]]['paidturn'] += int(nsteps > (cur[1] + 3) // 4)
        elif k == 3:
            pt = replay.point(p.pointer(0))
            t = pt[1] * w + pt[0]
            if p.u32(0):
                pearls.add(t)
            else:
                pearls.discard(t)
                if cur is not None:
                    cur[3] += 1
                    dec[cur[0]]['eat'] += 1
        elif k == 9:
            i = p.i32(0)
            a, z = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = a[1] * w + a[0], z[1] * w + z[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            lp = len(bodies[parent])
            bodies[parent] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(0)))
            bodies[child] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(1)))
            teams[child] = p.u16(8)
            dec[s]['split'] += 1
            if view and parent == queens[s]:
                notes.append('r%d: %s queen splits %d -> %d + %d' % (rnd, ('OUR', 'THEIR')[s], lp, len(bodies[parent]), len(bodies[child])))
            elif view and lp >= 6:
                notes.append('r%d: %s %d-long splits -> %d + %d' % (rnd, ('our', 'their')[s], lp, len(bodies[parent]), len(bodies[child])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            L = len(bodies[i])
            turn_deaths.append((i, s, reason, L, i == queens[s]))
            if cur is not None and i == actor:
                cur[4] = reason
            dec[s]['death'] += 1
            dec[s]['d_' + CAUSE[reason]] += 1
            if view and (i == queens[s] or L >= 6):
                notes.append('r%d: %s %s (len %d) dies: %s' % (rnd, ('our', 'their')[s], 'QUEEN' if i == queens[s] else 'dragon', L, CAUSE[reason]))
            bodies.pop(i)
    close_turn()
    if view:
        return out
    return dict(gid=meta['gid'], map=meta['map'], T=[[dict(c) for c in cs] for cs in T], hist=hist, rams=rams)


def pick(tag):
    rows = [json.loads(x) for x in Path(WORK + 'ta_index.jsonl').read_text().splitlines()]
    def sel(src, team):
        return [(r, team) for r in rows if src in r['src'] and team in (r['a'], r['b'])]
    if tag == 'a':
        return sel('online/top3', 454)
    if tag == 'a0':
        return sel('online/top1', 454)
    if tag == 'l':
        return sel('online/top3', 157)
    if tag == 'c1':
        return sel('online/top3', 306)
    if tag == 'g':
        return sel('online/top3', 70)
    if tag == 'q':
        return sel('agg8-q1-new', 1119)
    if tag == 'm':
        return sel('agg7-m1', 1119)
    if tag == 't':
        return sel('smoke/top-l', 1119)
    if tag == 'cs':
        return [x for z, x in enumerate(sel('online/top1', 306)) if z % 6 == 0]
    return []


def save(tag, body):
    if tag == 'a':
        Path(WORK + 'ta_s2-a.jsonl').write_text(body)
    elif tag == 'a0':
        Path(WORK + 'ta_s2-a0.jsonl').write_text(body)
    elif tag == 'l':
        Path(WORK + 'ta_s2-l.jsonl').write_text(body)
    elif tag == 'c1':
        Path(WORK + 'ta_s2-c1.jsonl').write_text(body)
    elif tag == 'g':
        Path(WORK + 'ta_s2-g.jsonl').write_text(body)
    elif tag == 'q':
        Path(WORK + 'ta_s2-q.jsonl').write_text(body)
    elif tag == 'm':
        Path(WORK + 'ta_s2-m.jsonl').write_text(body)
    elif tag == 't':
        Path(WORK + 'ta_s2-t.jsonl').write_text(body)
    elif tag == 'cs':
        Path(WORK + 'ta_s2-cs.jsonl').write_text(body)


def main():
    if sys.argv[1] == 'view':
        gid, team = int(sys.argv[2]), int(sys.argv[3])
        last = int(sys.argv[4]) if len(sys.argv) > 4 else 150
        grids = tuple(int(x) for x in sys.argv[5].split(',')) if len(sys.argv) > 5 else ()
        rows = [json.loads(x) for x in Path(WORK + 'ta_index.jsonl').read_text().splitlines()]
        r = [x for x in rows if x['gid'] == gid][0]
        print(gid, r['map'], 'A', r['an'], r['ae'], 'B', r['bn'], r['be'], 'winner', r['win'], 'studied team', team)
        for x in process(Path(r['path']), r, team, view=last, grids=grids):
            print(x)
        return
    tag = sys.argv[2]
    todo = pick(tag)
    if len(sys.argv) > 3:
        todo = todo[:int(sys.argv[3])]
    out = []
    for n, (r, team) in enumerate(todo):
        try:
            out.append(json.dumps(process(Path(r['path']), r, team), separators=(',', ':')))
        except Exception as e:
            print('FAILED', r['gid'], type(e).__name__, e, flush=True)
    save(tag, '\n'.join(out) + '\n')
    print(tag, 'done', len(out))


main()
