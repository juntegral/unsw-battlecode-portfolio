"""qexit-opus: every death of our queen, with her free cells at her last turn starts, who closed them, and the killer.
Usage (repo root): python3 -B data/codex/astra/qexit-opus/qdeath.py online | local <arm> ..."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
SM = Path('data/online/smoke')
HERE = Path('data/codex/astra/qexit-opus')
RADIUS = 4
VERS = dict(l.split() for l in (SM / 'versions.tsv').read_text().splitlines() if l.strip())


def scan(path, own, only=None):
    root = replay.load(path).root()
    if only is not None and VERS.get(str([root.text(1), root.text(2)][own])) not in only:
        return None
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    Q = queens[0]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def inview(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None, 0
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H), 1
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H), 0

    def sides_of(h, bd):
        """per direction: ('free',) / ('wall',) / (kind, id, length, 'head'|'body'|'tail', portal)"""
        occ = {}
        for i, bb in bd.items():
            for n, c in enumerate(bb):
                occ[c] = (i, len(bb), 'head' if n == 0 else 'tail' if n == len(bb) - 1 else 'body')
        out = []
        for d in range(4):
            c, viap = dest(h, d)
            if c is None:
                out.append(('wall',))
            elif c in occ:
                i, L, part = occ[c]
                kind = 'own' if i == Q else 'mate' if side(i) == 0 else 'foe'
                out.append((kind, i, L, part, viap, c))
            else:
                out.append(('free', c, viap))
        return out

    def nfree(s):
        return sum(1 for x in s if x[0] == 'free')

    stats = [0, 0, 0]
    condlist = []
    hist = []          # queen turns: dict(r, L, start sides, after sides, dirs, split, heads at start)
    out = []
    rnd, actor, dirs, used = -1, None, [], 0
    qturn = None
    tstart = None
    their_q_dead = None

    def close():
        nonlocal qturn
        if qturn is not None and Q in bodies:
            qturn['after'] = sides_of(bodies[Q][0], bodies)
            qturn['La'] = len(bodies[Q])
            qturn['ha'] = bodies[Q][0]
            qturn['bd_after'] = {i: list(b) for i, b in bodies.items()}
            fs = [x for x in qturn['start'] if x[0] == 'free']
            fa = [x for x in qturn['after'] if x[0] == 'free']
            cond = 0
            if not qturn['split'] and len(qturn['dirs']) == 1 and len(fs) >= 2 and len(fa) == 1 and qturn['ha'] != qturn['h']:
                foes = [bb[0] for z, bb in qturn['bd'].items() if side(z) == 1 and inview(qturn['h'], bb[0])]
                if any(gap(fa[0][1], fh) <= RADIUS for fh in foes):
                    cond = 1
                    for x in fs:
                        if x[1] == qturn['ha']:
                            continue
                        on = [y for y in sides_of(x[1], qturn['bd']) if y[0] == 'free']
                        if len(on) >= 2 or (len(on) == 1 and not any(gap(on[0][1], fh) <= RADIUS for fh in foes)):
                            cond = 2
            qturn['cond'] = cond
            stats[cond] += 1
            if cond:
                condlist.append([cond, qturn['r'], qturn['L'], list(qturn['h']), list(qturn['ha']), [list(x) for x in foes], qturn['start'], qturn['after']])
        qturn = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close()
            actor, dirs, used = p.i32(0), [], 0
            tstart = dict(h0=bodies[actor][0], L0=len(bodies[actor]), path=[bodies[actor][0]])
            if actor == Q:
                qturn = dict(r=rnd, L=len(bodies[Q]), h=bodies[Q][0], start=sides_of(bodies[Q][0], bodies), dirs=[], split=0,
                             bd={i: list(b) for i, b in bodies.items()})
                hist.append(qturn)
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used = 0
            if actor == Q and qturn is not None:
                qturn['dirs'] = list(dirs)
                qturn['akind'] = a.u16(0) if a else -1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
                    tstart['path'].append(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if parent == Q and qturn is not None:
                qturn['split'] = 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if i == queens[1] and their_q_dead is None:
                their_q_dead = rnd
            if i != Q:
                bodies.pop(i)
                continue
            b = bodies[i]
            L, h = len(b), b[0]
            rec = dict(r=rnd, L=L, reason=reason, h=list(h), actor=actor, own_turn=int(actor == Q), their_q_dead=their_q_dead,
                       maxlen_mate=max((len(bb) for z, bb in bodies.items() if z != Q and side(z) == 0), default=0),
                       n_mates=sum(1 for z in bodies if z != Q and side(z) == 0))
            last = hist[-1] if hist else None
            prev = hist[-2] if len(hist) > 1 else None
            rec['cond_hist'] = [x.get('cond', 0) for x in hist[-9:]]
            if actor == Q:
                # she died on her own move
                rec['f1'] = nfree(last['start'])
                rec['start1'] = last['start']
                rec['dirs'] = last['dirs']
                rec['used'] = used
                rec['split1'] = last['split']
                tgt = None
                if used < len(dirs):
                    c, viap = dest(h, dirs[used])
                    tgt = c
                    rec['viap'] = viap
                    if c is not None:
                        for z, bb in bodies.items():
                            if c in bb:
                                n = list(bb).index(c)
                                rec['hit'] = ['own' if z == Q else 'mate' if side(z) == 0 else 'foe', z, len(bb),
                                              'head' if n == 0 else 'tail' if n == len(bb) - 1 else 'body']
                if prev is not None:
                    rec['f0'] = nfree(prev['start'])
                    rec['f0a'] = nfree(prev['after']) if 'after' in prev else None
                    rec['split0'] = prev['split']
                    rec['L0'] = prev['L']
                    rec['dirs0'] = prev['dirs']
                    # cells free after her previous move and taken at her last turn start
                    if 'after' in prev:
                        closers = []
                        freed = {x[1] for x in prev['after'] if x[0] == 'free'}
                        for x in last['start']:
                            if x[0] not in ('free', 'wall') and x[5] in freed:
                                closers.append([x[0], x[1], x[2], x[3]])
                        rec['closers'] = closers
                        rec['moved_between'] = int(prev['ha'] != last['h'])
                    if len(hist) > 2:
                        rec['f00'] = nfree(hist[-3]['start'])
                        rec['f00a'] = nfree(hist[-3]['after']) if 'after' in hist[-3] else None
            else:
                # killed on someone else's turn
                a = actor
                rec['att'] = ['mate' if side(a) == 0 else 'foe', a, tstart['L0'], used + 1]
                rec['att_free'] = -(-tstart['L0'] // 4)
                rec['att_paid'] = int(used + 1 > rec['att_free'])
                path = tstart['path'] + [h]
                rec['att_portal'] = int(any(gap(path[n], path[n + 1]) != 1 for n in range(len(path) - 1)))
                rec['att_gap'] = gap(tstart['h0'], h)
                rec['att_is_queen'] = int(a == queens[1])
                if last is not None:
                    rec['Lstart1'] = last['L']
                    rec['La1'] = last.get('La')
                    opts = []
                    foes = [(z, bb[0], len(bb)) for z, bb in last['bd'].items() if side(z) == 1 and inview(last['h'], bb[0])]
                    for dd, x in enumerate(last['start']):
                        if x[0] != 'free':
                            opts.append([dd, x[0], -1])
                            continue
                        risk = 0
                        for z, fh, fl in foes:
                            g = gap(x[1], fh)
                            fr = -(-fl // 4)
                            if g <= fr:
                                risk = 2
                            elif g <= min(4, fr + fl - 2):
                                risk = max(risk, 1)
                        opts.append([dd, 'free', risk])
                    rec['opts'] = opts
                    rec['n_foe_view'] = len(foes)
                    rec['f1'] = nfree(last['start'])
                    rec['f1a'] = nfree(last['after']) if 'after' in last else None
                    rec['split1'] = last['split']
                    rec['dirs'] = last['dirs']
                    rec['same_round'] = int(last['r'] == rnd)
                    ah = last['bd'].get(a)
                    if ah is not None:
                        rec['seen_q'] = int(inview(last['h'], ah[0]))
                        rec['seen_mate'] = int(any(inview(bb[0], ah[0]) for z, bb in last['bd'].items() if z != Q and side(z) == 0))
                        rec['gap_at_start'] = gap(last['h'], ah[0])
                        rec['attL_at_start'] = len(ah)
                    else:
                        rec['seen_q'] = -1
                    if 'after' in last:
                        rec['after1'] = last['after']
                        # was a non-free side of hers after her move held by a mate
                        rec['mate_sides'] = [[x[0], x[1], x[2], x[3]] for x in last['after'] if x[0] in ('mate', 'own')]
                        aa = last['bd_after'].get(a)
                        if aa is not None:
                            rec['gap_after'] = gap(last['ha'], aa[0])
                    if prev is not None:
                        rec['f0'] = nfree(prev['start'])
                        rec['f0a'] = nfree(prev['after']) if 'after' in prev else None
            out.append(rec)
            bodies.pop(i)
    close()
    alive = Q in bodies
    snaps = len(bodies.get(Q, ()))
    return dict(condlist=condlist, stats=stats, bot=[root.text(1), root.text(2)][own], W=W, H=H, last=rnd, qalive=int(alive), qlen=snaps, deaths=out)


def online(part):
    rows, seen = [], set()
    folders = sorted(SM.glob('one1[1-4]-*-old'), reverse=True) if part == 'smoke' else sorted(Path('data/online/live-one1').glob('b*'), reverse=True)
    games = Counter()
    f = open(HERE / ('qcond-%s.jsonl' % part), 'w')
    for folder in folders:
        for mp in sorted(folder.glob('game-*.json')):
            j = json.loads(mp.read_text())
            rp = folder / ('M%d.replay' % j['id'])
            if not rp.exists() or j['id'] in seen or 1119 not in (j['teamAId'], j['teamBId']):
                continue
            seen.add(j['id'])
            own = 0 if j['teamAId'] == 1119 else 1
            try:
                g = scan(rp, own, ('one11', 'one12', 'one13', 'one14'))
            except Exception as e:
                print('ERR', rp, repr(e)[:120])
                continue
            if g is None:
                continue
            ver = VERS.get(str(g['bot']), str(g['bot']))
            if ver not in ('one11', 'one12', 'one13', 'one14'):
                continue
            src = folder.name[:-4] if folder.name.endswith('-old') else 'ranked'
            games[ver, src] += 1
            for d in g['deaths']:
                d.update(gid=j['id'], ver=ver, src=src, map=j['mapName'], cells=g['W'] * g['H'], last=g['last'],
                         opp=j['teamBName'] if own == 0 else j['teamAName'])
                rows.append(d)
                f.write(json.dumps(d, separators=(',', ':')) + '\n')
            f.write(json.dumps(dict(game=j['id'], ver=ver, src=src, qalive=g['qalive'], qlen=g['qlen'], last=g['last'], stats=g['stats']), separators=(',', ':')) + '\n')
            f.flush()
    print('games', sum(games.values()), dict(games))
    print('queen deaths', len(rows))


def local(arms):
    RUNS = Path.home() / 'meow-redteam/solo/runs'
    for arm in arms:
        rows, n = [], 0
        for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
            if not (folder / 'result.txt').exists() or not (folder / 'game.replay').exists():
                continue
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
            g = scan(folder / 'game.replay', int(m[3]))
            n += 1
            for d in g['deaths']:
                d.update(gid=folder.name, ver=arm, src='local', map=m[1], cells=g['W'] * g['H'], last=g['last'], opp='')
                rows.append(d)
        with open(HERE / ('qdeath-%s.jsonl' % arm), 'w') as f:
            for d in rows:
                f.write(json.dumps(d, separators=(',', ':')) + '\n')
        print(arm, 'games', n, 'queen deaths', len(rows))


if __name__ == '__main__':
    if sys.argv[1] in ('smoke', 'live'):
        online(sys.argv[1])
    else:
        local(sys.argv[2:])
