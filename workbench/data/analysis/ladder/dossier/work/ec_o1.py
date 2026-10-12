# Scratch (diag-economy): prints sample turns of one game where a pearl beside the head sits on a tile that is
# cramped only when the dragon's own body is counted (class O1 of ec_tight.py), with a 7 by 7 picture.
# Picture: H own head, o own body, m team mate, M mate head, e enemy, E enemy head, * pearl, . free; a wall or
# portal between two tiles is not drawn, so the list "pearl tile exits" names where the pearl's tile leads.
# Usage: python3 data/analysis/ladder/dossier/work/ec_o1.py <O|R> <game> [max] [first round] [took 0/1/2=any]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def main():
    who, game = sys.argv[1], int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    first = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    want = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    row = [r for r in rows if r['who'] == who and r['game'] == game][0]
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    N = w * h
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    adj = []
    for y in range(h):
        for x in range(w):
            rowm = []
            for d in range(4):
                dx, dy = STEP[d]
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    rowm.append(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                else:
                    rowm.append(((y + dy) % h) * w + (x + dx) % w)
            adj.append(sorted(set(rowm)))
    focal = row['side']
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    cell = {}
    for i, b in bodies.items():
        for c in b:
            cell[c] = i
    present = {}
    expected = deque()
    rnd, actor, shown = 0, None, 0
    pend = None
    log = []

    def room(start, cap, own, others):
        seen = {start}
        q = [start]
        k = 0
        while k < len(q) and len(q) < cap:
            for t in adj[q[k]]:
                if t in seen:
                    continue
                j = cell.get(t)
                if j is not None and ((j == own[0] and own[1]) or (j != own[0] and others)):
                    continue
                seen.add(t)
                q.append(t)
            k += 1
        return len(q)

    def picture(head, a):
        hy, hx = divmod(head, w)
        out = []
        for dy in range(-3, 4):
            s = ''
            for dx in range(-3, 4):
                t = ((hy + dy) % h) * w + (hx + dx) % w
                j = cell.get(t)
                if t in present:
                    s += '*'
                elif j is None:
                    s += '.'
                elif j == a:
                    s += 'H' if bodies[j][0] == t else 'o'
                elif sd[j] == 0:
                    s += 'M' if bodies[j][0] == t else 'm'
                else:
                    s += 'E' if bodies[j][0] == t else 'e'
            out.append(s)
        return out

    def flush():
        nonlocal pend, shown
        if pend is None:
            return
        took = int(pend['ate'])
        if want in (2, took) and shown < limit:
            shown += 1
            print('r%d #%d L%d head (%d,%d) pearl (%d,%d) kind %d: room with own body %d, without %d; pearl tile exits %s; %s' % (
                pend['rnd'], pend['a'], pend['L'], pend['head'] % w, pend['head'] // w, pend['q'] % w, pend['q'] // w, pend['kind'],
                pend['ro'], pend['rb'], pend['exits'], 'TOOK' if took else ' '.join(log) or 'no move'))
            for s in pend['pic']:
                print('     ' + s)
            watch[pend['a']] = [pend['rnd'], 4]
        pend = None

    watch = {}
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            flush()
            rnd, actor = p.i32(0), None
            if shown >= limit and not watch:
                break
        elif k == 1:
            flush()
            actor = p.i32(0)
            log = []
            b = bodies.get(actor)
            if b is None or sd[actor] != 0 or rnd > 300 or rnd < first:
                continue
            L, head = len(b), b[0]
            if actor in watch:
                watch[actor][1] -= 1
                if watch[actor][1] <= 0:
                    del watch[actor]
            if L > 3:
                continue
            best = None
            for q in adj[head]:
                if q not in present:
                    continue
                lo = L + 2
                rb = room(q, 3 * L + 8, (actor, False), True)
                ro = room(q, 3 * L + 8, (actor, True), True)
                o1 = rb >= lo and ro < lo
                sc = (0 if not o1 else 1, q)
                if best is None or sc < best[0]:
                    best = (sc, q, rb, ro, o1)
            if best is None or not best[4]:
                continue
            q = best[1]
            ex = []
            for t in adj[q]:
                j = cell.get(t)
                ex.append('(%d,%d)%s' % (t % w, t // w, '' if j is None else 'own' if j == actor else 'mate' if sd[j] == 0 else 'enemy'))
            pend = dict(rnd=rnd, a=actor, L=L, head=head, q=q, kind=present[q], rb=best[2], ro=best[3], exits=' '.join(ex), ate=False,
                        pic=picture(head, actor))
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present[c] = expected.popleft() if expected else 0
            else:
                present.pop(c)
                if pend is not None and pend['a'] == actor:
                    pend['ate'] = True
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                cell[hd] = i
                if i == actor:
                    log.append('to(%d,%d)' % (hd % w, hd // w))
                    if i in watch and pend is None:
                        print('        then r%d #%d L%d to (%d,%d)' % (rnd, i, len(b), hd % w, hd // w))
            while len(b) > 1 and b[-1] != tl:
                c = b.pop()
                if cell.get(c) == i and c not in b:
                    del cell[c]
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            for x in bodies[a]:
                cell.pop(x, None)
            sd[c] = sd[a]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for x in bodies[i]:
                    cell[x] = i
            if a == actor:
                log.append('split')
                if a in watch:
                    print('        then r%d #%d splits (child #%d)' % (rnd, a, c))
        elif k == 11:
            i = p.i32(0)
            b = bodies.pop(i)
            for seg, x in enumerate(b):
                if cell.get(x) == i:
                    del cell[x]
                if seg % 2 == 0:
                    expected.append(1 if sd[i] == 0 else 2)
            if i == actor:
                log.append('DIES')
            if i in watch:
                print('        then r%d #%d DIES (reason %d) L%d' % (rnd, i, p.u16(4), len(b)))
                del watch[i]
    flush()


main()
