"""late-opus scan: our queen's turns (standing wait splits) and her deaths, one11..one17, all games. Writes data.json.
Usage (from ROOT): python3 -B data/codex/astra/late-opus/scan.py"""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../../../..')
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
SM = Path('data/online/smoke')
HERE = Path('data/codex/astra/late-opus')
VERS = dict(l.split() for l in (SM / 'versions.tsv').read_text().splitlines() if l.strip())
KEEP = ('one11', 'one12', 'one13', 'one14', 'one15', 'one16', 'one17')


def scan(path, own):
    root = replay.load(path).root()
    ver = VERS.get(str([root.text(1), root.text(2)][own]).strip())
    if ver not in KEEP:
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

    Q = min(i for i in bodies if side(i) == 0)
    EQ = min(i for i in bodies if side(i) == 1)

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
            return None
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def nfree(h):
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        n = 0
        for d in range(4):
            c = dest(h, d)
            if c is not None and c not in occ:
                n += 1
        return n

    def visible_foes():
        ours = [bb[0] for z, bb in bodies.items() if side(z) == 0]
        return [(z, bb[0], len(bb)) for z, bb in bodies.items() if side(z) == 1 and any(inview(o, bb[0]) for o in ours)]

    ql, el = [], []        # per round start
    turns = []             # queen turns
    deaths = []
    rnd, actor, used, dirs = -1, None, 0, []
    qt = None
    eq_dead = None
    last_vis = None        # visible foe ids at queen's last turn start
    last_qview = None
    act_L0 = 0

    def close():
        nonlocal qt
        if qt is not None and Q in bodies:
            qt['La'] = len(bodies[Q])
            qt['mv'] = int(bodies[Q][0] != qt.pop('h'))
            nh = qt.pop('nh')
            if nh is not None:
                g1 = gap(bodies[Q][0], nh)
                qt['tw'] = 1 if g1 < qt['ng'] else -1 if g1 > qt['ng'] else 0
        qt = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
            ql.append(len(bodies[Q]) if Q in bodies else 0)
            el.append(len(bodies[EQ]) if EQ in bodies else 0)
        elif k == 1:
            close()
            actor, dirs, used = p.i32(0), [], 0
            act_L0 = len(bodies[actor])
            if actor == Q:
                h = bodies[Q][0]
                vis = visible_foes()
                near = min(vis, key=lambda v: gap(h, v[1])) if vis else None
                qt = dict(r=rnd, L=len(bodies[Q]), h=h, f=nfree(h), sp=0, ak=-1, nd=0,
                          nh=near[1] if near else None, ng=gap(h, near[1]) if near else -1, nl=near[2] if near else 0,
                          eq=len(bodies[EQ]) if EQ in bodies else 0)
                turns.append(qt)
                last_vis = {v[0] for v in vis}
                last_qview = {v[0] for v in vis if inview(h, v[1])}
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used = 0
            if actor == Q and qt is not None:
                qt['ak'] = a.u16(0) if a else -1
                qt['nd'] = len(dirs)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if Q in (parent, child) and qt is not None:
                qt['sp'] = 1
                qt['ch'] = len(bodies[child if parent == Q else parent])
                qt['qpar'] = int(parent == Q)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if i == EQ and eq_dead is None:
                eq_dead = rnd
            if i != Q:
                bodies.pop(i)
                continue
            b = bodies[i]
            h = b[0]
            rec = dict(r=rnd, L=len(b), reason=reason, eq=len(bodies[EQ]) if EQ in bodies else 0, eq_dead=eq_dead,
                       mates5=sum(1 for z, bb in bodies.items() if z != Q and side(z) == 0 and gap(h, bb[0]) <= 5),
                       mates5b=sum(1 for z, bb in bodies.items() if z != Q and side(z) == 0 and min(gap(h, c) for c in bb) <= 5),
                       n_mates=sum(1 for z in bodies if z != Q and side(z) == 0),
                       maxmate=max((len(bb) for z, bb in bodies.items() if z != Q and side(z) == 0), default=0),
                       last3=[dict(r=t['r'], L=t['L'], mv=t.get('mv'), tw=t.get('tw'), ng=t['ng'], nl=t['nl'], sp=t['sp'], f=t['f'], nd=t['nd'])
                              for t in turns[-3:]])
            if actor == Q:
                rec['cause'] = 'own'
                rec['used'] = used
                rec['nd'] = len(dirs)
                if used < len(dirs):
                    c = dest(h, dirs[used])
                    if c is None:
                        rec['hit'] = ['wall']
                    else:
                        for z, bb in bodies.items():
                            if c in bb:
                                n = list(bb).index(c)
                                rec['hit'] = ['own' if z == Q else 'mate' if side(z) == 0 else 'foe', z, len(bb),
                                              'head' if n == 0 else 'tail' if n == len(bb) - 1 else 'body', int(z == EQ)]
            elif actor is None:
                rec['cause'] = 'none'
            elif side(actor) == 0:
                rec['cause'] = 'mate'
            else:
                seen = last_vis is not None and actor in last_vis
                rec['cause'] = 'ram_seen' if seen else 'ram_unseen'
                rec['qview'] = int(last_qview is not None and actor in last_qview)
                rec['attL'] = act_L0
                rec['att_steps'] = used + 1
                rec['att_is_q'] = int(actor == EQ)
            deaths.append(rec)
            bodies.pop(i)
    close()
    for t in turns:
        t.pop('h', None)
        t.pop('nh', None)
    return dict(ver=ver, W=W, H=H, last=rnd, ql=ql, el=el, turns=turns, deaths=deaths,
                qfin=len(bodies[Q]) if Q in bodies else 0, efin=len(bodies[EQ]) if EQ in bodies else 0,
                n_fin=sum(1 for z in bodies if side(z) == 0), en_fin=sum(1 for z in bodies if side(z) == 1))


def main():
    folders = sorted(SM.glob('one1[1-7]-*-old')) + sorted(Path('data/online/live-one1').glob('b*'))
    seen, games, skip = set(), [], defaultdict(int)
    for folder in folders:
        live = folder.parent.name == 'live-one1'
        for mp in sorted(folder.glob('game-*.json')):
            j = json.loads(mp.read_text())
            rp = folder / ('M%d.replay' % j['id'])
            if 1119 not in (j['teamAId'], j['teamBId']) or j.get('status') != 'completed' or not rp.exists():
                skip['team/status/file'] += 1
                continue
            if live and (j.get('completedAt') or '') < '2026-10-08T21:00':
                skip['time'] += 1
                continue
            if j['id'] in seen:
                skip['dup'] += 1
                continue
            seen.add(j['id'])
            own = 0 if j['teamAId'] == 1119 else 1
            try:
                g = scan(rp, own)
            except Exception as e:
                print('ERR', rp, repr(e)[:160])
                skip['err'] += 1
                continue
            if g is None:
                skip['ver'] += 1
                continue
            g.update(id=j['id'], src='ranked' if live else folder.name[:-4], map=j.get('mapName'), winner=j.get('winner'),
                     own=own, win=int(j.get('winner') == 'ab'[own]), opp=j.get('teamBName') if own == 0 else j.get('teamAName'),
                     done=j.get('completedAt'))
            games.append(g)
    json.dump(dict(games=games, skip=dict(skip)), open(HERE / 'data.json', 'w'), separators=(',', ':'))
    print(len(games), dict(skip))


main()
