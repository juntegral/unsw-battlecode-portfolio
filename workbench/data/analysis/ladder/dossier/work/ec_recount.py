# Scratch (diag-economy): recount of the card's rate by another method. Every 4th game of each team, dragons of 2
# and 3, rounds up to the leader round (150 above 1200 cells, else 300). A plain flood, no timing:
# room behind a pearl tile = free tiles reachable from it with every other dragon's body and the dragon's own head
# tile as walls (the rest of its own body free), capped at 3L+8. With two pearls beside the head the roomier is used.
# Class: room (3L+8 or more), tight (L+2 to 3L+7), trapped (under L+2). alt = another free tile beside the head, not
# a pearl tile of this turn, whose flood by the same rule reaches 3L+8. Each class is counted twice: every turn
# (key class|alt|0) and turns with no flag on the chosen pearl (class|alt|1; flags as in ec_alt.py: pocket rule or
# portal-only step, an enemy head or a team mate's head beside the pearl).
# Usage: python3 data/analysis/ladder/dossier/work/ec_recount.py <O|R>     then     ec_recount.py show
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def build(w, h, raw):
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    adj, oadj, padj = [], [], []
    for y in range(h):
        for x in range(w):
            row = set()
            orow, prow = set(), set()
            for d in range(4):
                dx, dy = STEP[d]
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    row.add(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                    prow.add(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                else:
                    row.add(((y + dy) % h) * w + (x + dx) % w)
                    orow.add(((y + dy) % h) * w + (x + dx) % w)
            adj.append(sorted(row))
            oadj.append(sorted(orow))
            padj.append(prow - orow)
    return adj, oadj, padj


def scan(row, geos, acc):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    gk = (row['layout'], w, h)
    if gk not in geos:
        geos[gk] = build(w, h, raw)
    adj, oadj, padj = geos[gk]
    pockets = geos.setdefault(('pk',) + gk, {})
    focal = row['side']
    last = 300 if w * h <= 1200 else 150
    owner = {}
    for i, b in bodies.items():
        for c in b:
            owner[c] = i
    present = set()
    rnd, actor, cur = 0, None, None

    def flood(start, a, head, cap):
        seen = {start}
        q = [start]
        k = 0
        while k < len(q) and len(q) < cap:
            for t in adj[q[k]]:
                if t in seen or t == head:
                    continue
                j = owner.get(t)
                if j is not None and j != a:
                    continue
                seen.add(t)
                q.append(t)
            k += 1
        return len(q)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, None
            if rnd > last:
                break
        elif k == 1:
            actor = p.i32(0)
            cur = None
            b = bodies.get(actor)
            if b is None or teams[actor] != focal or len(b) > 3:
                continue
            L, head = len(b), b[0]
            pearls = [t for t in adj[head] if t in present]
            if not pearls:
                continue
            cap = 3 * L + 8
            room, q = max((flood(t, actor, head, cap), t) for t in pearls)
            cls = 'room' if room >= cap else 'tight' if room >= L + 2 else 'trapped'
            pk = pockets.get(q)
            if pk is None:
                seen = {q}
                stack = [q]
                z = 0
                while z < len(stack) and len(stack) < 48:
                    for u in oadj[stack[z]]:
                        if u not in seen and len(stack) < 48:
                            seen.add(u)
                            stack.append(u)
                    z += 1
                pk = pockets[q] = len(stack)
            flag = (pk < 48 and L + 1 > pk // 2) or q in padj[head]
            for u in adj[q]:
                j = owner.get(u)
                if u != head and j is not None and bodies[j][0] == u:
                    flag = True
            clean = 0 if flag else 1
            alt = 0
            for t in adj[head]:
                if t not in present and t not in owner and flood(t, actor, head, cap) >= cap:
                    alt = 1
                    break
            cur = [cls, alt, 0, clean]
            acc[(cls, alt, 0)][0] += 1
            if clean:
                acc[(cls, alt, 1)][0] += 1
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if cur is not None and not cur[2]:
                    cur[2] = 1
                    acc[(cur[0], cur[1], 0)][1] += 1
                    if cur[3]:
                        acc[(cur[0], cur[1], 1)][1] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                owner[hd] = i
            while len(b) > 1 and b[-1] != tl:
                c = b.pop()
                if owner.get(c) == i and c not in b:
                    del owner[c]
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            for x in bodies[a]:
                if owner.get(x) == a:
                    del owner[x]
            teams[c] = teams[a]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for x in bodies[i]:
                    owner[x] = i
        elif k == 11:
            i = p.i32(0)
            for x in bodies.pop(i):
                if owner.get(x) == i:
                    del owner[x]


def show():
    data = {}
    for who, name in (('O', 'ec_recount-O.json'), ('R', 'ec_recount-R.json')):
        data[who] = json.loads(Path(OUT + name).read_text())
    lays = sorted(set(data['O']) | set(data['R']))
    for key in ('room|1|0', 'tight|1|0', 'trapped|1|0', 'room|1|1', 'tight|1|1', 'trapped|1|1', 'tight|0|1', 'trapped|0|1'):
        vals, hi, n, pool = [[], []], 0, 0, [[0, 0], [0, 0]]
        for l in lays:
            o = data['O'].get(l, {}).get(key, [0, 0])
            r = data['R'].get(l, {}).get(key, [0, 0])
            for wi, x in enumerate((o, r)):
                pool[wi][0] += x[0]
                pool[wi][1] += x[1]
            if o[0] >= 30 and r[0] >= 30:
                n += 1
                hi += r[1] / r[0] > o[1] / o[0]
                vals[0].append(100 * o[1] / o[0])
                vals[1].append(100 * r[1] / r[0])
        cls, alt, cl = key.split('|')
        print(('no flag  ' if cl == '1' else 'all      ') + '%-8s %s: taken %.1f%% %.1f%% (rank-1 higher on %d of %d layouts); pooled %d of %d, %d of %d' % (
            cls, 'another step has room' if alt == '1' else 'no other step with room', sum(vals[0]) / max(1, len(vals[0])),
            sum(vals[1]) / max(1, len(vals[1])), hi, n, pool[0][1], pool[0][0], pool[1][1], pool[1][0]))


def main():
    who = sys.argv[1]
    if who == 'show':
        show()
        return
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))[::4]
    geos, out, bad = {}, {}, []
    for n, r in enumerate(rows):
        acc = defaultdict(lambda: [0, 0])
        try:
            scan(r, geos, acc)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
            continue
        d = out.setdefault(r['layout'], {})
        for (cls, alt, cl), v in acc.items():
            x = d.setdefault('%s|%d|%d' % (cls, alt, cl), [0, 0])
            x[0] += v[0]
            x[1] += v[1]
        if n % 20 == 19:
            print(n + 1, len(rows), 'bad', len(bad), flush=True)
    if who == 'O':
        Path(OUT + 'ec_recount-O.json').write_text(json.dumps(out))
    else:
        Path(OUT + 'ec_recount-R.json').write_text(json.dumps(out))
    print('done', who, len(rows), 'bad', bad)


main()
