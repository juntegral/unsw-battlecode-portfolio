"""watch17-opus: per-game health lines and the queen>=10 / enemy within 3 mechanism table.
Usage (from ROOT): python3 -B data/codex/astra/watch17-opus/w.py   (scans everything on disk, caches per game in cache.json)"""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque, Counter
from pathlib import Path

HERE = Path('data/codex/astra/watch17-opus')
VER = {'21583': 'one15', '21651': 'one16', '21693': 'one17', '21761': 'one18', '21827': 'one19', '21843': 'one20', '21857': 'one21'}
NAMES = replay.EVENT_NAMES


def gap(W, H, a, b):
    ax, ay, bx, by = a % W, a // W, b % W, b // W
    dx, dy = abs(ax - bx), abs(ay - by)
    return min(dx, W - dx) + min(dy, H - dy)


def run(rp, j):
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(rp).root()
    bot = root.text(1 if ours == 0 else 2).strip()
    if bot not in VER:
        return dict(id=j['id'], ver=None, bot=bot)
    G = geometry(root.text(0))
    W, H = G['W'], G['H']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    EQ = min(i for i in teams if teams[i] != ours)
    rnd = -1
    actor = None
    qturn = {}
    qlen = {}
    qsplits = []
    qdead = None
    eqdead = None
    cur = None
    acts = [Counter(), Counter()]
    lasth = {}
    still = {}
    stillmax = [(0, -1, -1), (0, -1, -1)]
    alive_prev = None
    collapse = []
    deaths = [Counter(), Counter()]
    alive_hist = {}

    for ev in root.pointer(3):
        k = NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
            al = [sum(1 for i in bodies if teams[i] == s) for s in (0, 1)]
            if alive_prev:
                for s in (0, 1):
                    if alive_prev[s] >= 3 and al[s] == 0:
                        collapse.append((rnd, s == ours, alive_prev[s]))
            alive_prev = al
            if rnd % 50 == 0:
                alive_hist[rnd] = [al[ours], al[1 - ours], sum(len(b) for i, b in bodies.items() if teams[i] == ours),
                                   sum(len(b) for i, b in bodies.items() if teams[i] != ours)]
            for i, b in bodies.items():
                h = b[0]
                if lasth.get(i) == h:
                    still[i] = still.get(i, 0) + 1
                    s = 0 if teams[i] == ours else 1
                    if still[i] > stillmax[s][0]:
                        stillmax[s] = (still[i], i, rnd)
                else:
                    still[i] = 0
                lasth[i] = h
            cur = None
            if Q in bodies:
                h = bodies[Q][0]
                ql = len(bodies[Q])
                qlen[rnd] = ql
                foes = sorted((gap(W, H, h, b[0]), len(b), i) for i, b in bodies.items() if teams[i] != ours)
                nd, nl = (foes[0][0], foes[0][1]) if foes else (99, 0)
                cur = dict(r=rnd, ql=ql, nd=nd, nl=nl, n3=sum(1 for f in foes if f[0] <= 3), mv=0, split=0, after=ql)
                qturn[rnd] = cur
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'dragonAction':
            try:
                a = p.pointer(0)
                used_up = p.pointer(1)
                to = p.bit(32) or (used_up is not None and used_up.bit(64))
                kind = a.u16(0) if a else 9
            except Exception:
                to, kind = False, -1
            s = 0 if teams.get(p.i32(0)) == ours else 1
            acts[s]['timeout' if to else ('move', 'split', 'none')[kind] if 0 <= kind < 3 else 'none']+= 1
        elif k == 'dragonUpdate':
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == Q and cur and actor == Q:
                    cur['mv'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if i == Q and cur:
                cur['after'] = len(b)
        elif k == 'dragonSplit':
            par, ch = p.i32(0), p.i32(4)
            qinv = Q in (par, ch)
            before = len(bodies[Q]) if qinv else 0
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            if qinv:
                after = len(bodies[Q])
                if cur:
                    cur['split'] = 1
                    cur['after'] = after
                qsplits.append(dict(r=rnd, before=before, after=after, nd=cur['nd'] if cur else -1))
        elif k == 'dragonDeath':
            i = p.i32(0)
            s = 0 if teams[i] == ours else 1
            deaths[s][p.u16(4)] += 1
            if i == Q:
                qdead = (rnd, len(bodies[i]), p.u16(4))
            if i == EQ:
                eqdead = (rnd, len(bodies[i]), p.u16(4))
            bodies.pop(i)
    al = [sum(1 for i in bodies if teams[i] == s) for s in (0, 1)]
    if alive_prev:
        for s in (0, 1):
            if alive_prev[s] >= 3 and al[s] == 0:
                collapse.append((rnd, s == ours, alive_prev[s]))
    fin = len(bodies[Q]) if Q in bodies else 0
    efin = len(bodies[EQ]) if EQ in bodies else 0
    st = root.pointer(4)
    # mechanism turns: queen >= 10 at round start, an enemy head within 3
    mech = []
    for r, t in qturn.items():
        if t['ql'] >= 10 and t['nd'] <= 3:
            d = dict(t)
            for dr in (3, 5, 20):
                rr = r + dr
                d['a%d' % dr] = 'over' if rr > rnd else ('dead' if (qdead and qdead[0] < rr) or rr not in qlen else qlen[rr])
                if d['a%d' % dr] == 'over' and qdead and qdead[0] >= r:
                    d['a%d' % dr] = 'dead'
            mech.append(d)
    win = None if j.get('winner') not in ('a', 'b') else j['winner'] == 'ab'[ours]
    return dict(id=j['id'], ver=VER[bot], bot=bot, map=j.get('mapName'), opp=j['teamBName'] if ours == 0 else j['teamAName'],
                oppid=j['teamBId'] if ours == 0 else j['teamAId'], ranked=bool(j.get('ranked')), win=win, winner=j.get('winner'),
                ours=ours, last=rnd, end_reason=st.u16(2), qdead=qdead, qfin=fin, eqdead=eqdead, eqfin=efin,
                alive=[al[ours], al[1 - ours]], tot=[sum(len(b) for i, b in bodies.items() if teams[i] == ours),
                                                     sum(len(b) for i, b in bodies.items() if teams[i] != ours)],
                longest=[max((len(b) for i, b in bodies.items() if teams[i] == ours), default=0),
                         max((len(b) for i, b in bodies.items() if teams[i] != ours), default=0)],
                qsplits=qsplits, mech=mech, acts=[dict(acts[0]), dict(acts[1])], still=stillmax, collapse=collapse,
                deaths=[dict(deaths[0]), dict(deaths[1])], hist=alive_hist, done=j.get('completedAt'),
                scores=[j.get('scoresA'), j.get('scoresB')], serverLog=j.get('serverLog'), W=W, H=H)


def main():
    cp = HERE / 'cache.json'
    cache = json.loads(cp.read_text()) if cp.exists() else {}
    files = []
    for lab in ('one19-c1', 'one19-s1', 'one19-p1', 'one18-c1', 'one18-s1', 'one18-p1', 'one18-w1', 'one17-c1', 'one17-s1', 'one17-p1', 'one16-c1', 'one16-p1', 'one15-c1', 'one15-s1', 'one15-p1'):
        files += [(lab, f) for f in sorted(glob.glob('data/online/smoke/%s-old/game-*.json' % lab))]
    files += [('live', f) for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json'))]
    new = 0
    for lab, f in files:
        j = json.load(open(f))
        key = str(j['id'])
        if key in cache:
            continue
        if 1119 not in (j['teamAId'], j['teamBId']) or j.get('status') != 'completed':
            continue
        if lab == 'live' and (j.get('completedAt') or '') < '2026-10-09T02:00':
            continue
        rp = Path(f).parent / ('M%d.replay' % j['id'])
        if not rp.exists():
            continue
        try:
            r = run(rp, j)
        except Exception as ex:
            print('ERR', lab, j['id'], repr(ex)[:200])
            continue
        r['set'] = lab
        cache[key] = r
        new += 1
    cp.write_text(json.dumps(cache))
    print('new', new, 'cached', len(cache), Counter((g.get('ver'), g.get('set')) for g in cache.values()))


main()
