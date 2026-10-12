# Scratch (diag-feeding): how our longest dragon gets rammed. For every game in fd_games.jsonl with a leader death,
# replays it and writes one line per head-on death of our longest dragon (8+) in which it was the one hit.
# With a game id and two rounds as arguments it prints that window round by round instead (the viewer).
# Usage: python3 .../fd_ram.py <shard> <shards>      or      python3 .../fd_ram.py view <game> <r0> <r1>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(row, view=None):
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    ours = 'A' if 0 in teams and row['queen_us'] in teams and teams[row['queen_us']] == 'A' else 'B'
    side = lambda i: 'u' if teams[i] == ours else 't'
    man = lambda a, c: torus(a % w, c % w, w) + torus(a // w, c // w, h)
    cheb = lambda a, c: max(torus(a % w, c % w, w), torus(a // w, c // w, h))
    xy = lambda c: (c % w, c // w)
    ts, last, out = {}, {}, []
    noact = deque()
    rnd, actor, used, ate = 0, None, 0, 0
    pres = set()
    lines = []

    def top_len(s, skip=-1):
        return max([len(b) for i, b in bodies.items() if i != skip and side(i) == s], default=0)

    def focus():
        best = -1
        for i, b in bodies.items():
            if side(i) == 'u' and (best < 0 or len(b) > len(bodies[best])):
                best = i
        return best

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if view and view[0] <= rnd <= view[1]:
                f = focus()
                if f >= 0:
                    fh = bodies[f][0]
                    en = sorted((man(fh, b[0]), i, len(b)) for i, b in bodies.items() if side(i) == 't' and man(fh, b[0]) <= 8)
                    ow = sorted((man(fh, b[0]), i, len(b)) for i, b in bodies.items() if side(i) == 'u' and i != f and man(fh, b[0]) <= 6)
                    lines.append('r%d ours %d theirs %d | leader #%d len %d at %s | enemies<=8: %s | ours<=6: %s' % (
                        rnd, sum(side(i) == 'u' for i in bodies), sum(side(i) == 't' for i in bodies), f, len(bodies[f]), xy(fh),
                        ' '.join('d%d:#%d(L%d)' % e for e in en) or '-', ' '.join('d%d:L%d' % (o[0], o[2]) for o in ow) or '-'))
        elif k == 1:
            actor = p.i32(0)
            used, ate = 0, 0
            b = bodies[actor]
            ts[actor] = dict(r=rnd, head=b[0], L=len(b))
            if side(actor) == 'u' and len(b) >= 8 and len(b) >= top_len('u', actor):
                hd = b[0]
                last[actor] = dict(r=rnd, head=hd, L=len(b), steps=0, ate=0,
                                   enemies=dict((i, (cheb(hd, bb[0]), man(hd, bb[0]), len(bb))) for i, bb in bodies.items()
                                                if side(i) == 't' and cheb(hd, bb[0]) <= 8),
                                   own5=sum(1 for i, bb in bodies.items() if side(i) == 'u' and i != actor and man(hd, bb[0]) <= 5))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                pres.add(c)
            else:
                pres.discard(c)
                if actor in last and last[actor]['r'] == rnd:
                    last[actor]['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
                    if i in last and last[i]['r'] == rnd:
                        last[i]['steps'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, hd = len(b), b[0]
            if view and view[0] <= rnd <= view[1]:
                f = focus()
                if f >= 0 and (i == f or man(bodies[f][0], hd) <= 8):
                    lines.append('    death r%d #%d %s L%d %s at %s%s' % (rnd, i, side(i), L, ('wall', 'own', 'body', 'headon', 'noact')[min(reason, 4)], xy(hd),
                                                                     ' (actor #%d L%d from %s, %d steps)' % (actor, ts[actor]['L'], xy(ts[actor]['head']), used) if actor != i and actor in ts else ''))
            if side(i) == 'u' and reason == 4 and i == actor:
                noact.append((rnd, hd))
            if side(i) == 'u' and reason == 3 and i != actor and L >= 8 and L >= top_len('u', i) and rnd > 200 and side(actor) == 't':
                lt = last.get(i)
                a = ts[actor]
                e = lt['enemies'].get(actor) if lt else None
                out.append(dict(game=row['game'], r=rnd, id=i, L=L, q=int(i == row['queen_us']), ram=actor, ram_L=a['L'], ram_steps=used + 1,
                                ram_from=man(a['head'], hd), free=(a['L'] + 3) // 4,
                                seen=None if lt is None else int(e is not None and e[0] <= 3), then_cheb=e[0] if e else None, then_man=e[1] if e else None,
                                lead_steps=lt['steps'] if lt else None, lead_ate=lt['ate'] if lt else None, lead_turn=lt['r'] if lt else None,
                                in_view=sum(1 for v in lt['enemies'].values() if v[0] <= 3) if lt else None,
                                near8=len(lt['enemies']) if lt else None, own5=lt['own5'] if lt else None,
                                own5_now=sum(1 for z, bb in bodies.items() if side(z) == 'u' and z != i and man(hd, bb[0]) <= 5),
                                en5_now=sum(1 for z, bb in bodies.items() if side(z) == 't' and man(hd, bb[0]) <= 5),
                                fed10=sum(1 for rr, c in noact if rnd - rr <= 10 and man(c, hd) <= 10),
                                n_us=sum(side(z) == 'u' for z in bodies) - 1, n_them=sum(side(z) == 't' for z in bodies)))
            bodies.pop(i)
    if view:
        print('\n'.join(lines))
    return out


def main():
    R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
    rows = dict((r['game'], r) for r in R)
    scans = {}
    for k in range(4):
        for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open():
            g = json.loads(l)
            if g['game'] in rows:
                rows[g['game']]['queen_us'] = g['queen']['u']
    if sys.argv[1] == 'view':
        r = rows[int(sys.argv[2])]
        print(r['game'], r['layout'], r['rating'], r['result'], r['ended_by'], 'S', r['S'], r['kind'], 'U', r['U'], 'T', r['T'], 'end', r['Ue'], r['Te'])
        scan(r, (int(sys.argv[3]), int(sys.argv[4])))
        return
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    todo = sorted([r for r in R if r['lead_deaths']], key=lambda r: r['game'])
    todo = [r for n, r in enumerate(todo) if n % shards == shard]
    out = []
    for n, r in enumerate(todo):
        out += scan(r)
        if n % 20 == 19:
            print(n + 1, len(todo), flush=True)
    body = '\n'.join(json.dumps(x, separators=(',', ':')) for x in out) + '\n'
    if shard == 0:
        Path(OUT + 'fd_ram-0.jsonl').write_text(body)
    else:
        Path(OUT + 'fd_ram-1.jsonl').write_text(body)
    print('done', shard, len(todo), len(out))


main()
