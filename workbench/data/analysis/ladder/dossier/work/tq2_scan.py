"""Scratch (diag-topqueen): one record per queen turn for BOTH queens of a game; tq_scan.py's scan with pearl origin,
her side's longest other dragon and the act at death added, and job lists for the top-team folders.
side 0 = the studied team of the battle, side 1 = its opponent. queen = lowest starting id of a side.
Usage: python3 tq2_scan.py top3 <shard> <shards> | top1 <team> <shard> <shards> | online <label>   [limitN]
Writes tq2_scan-<tag>.jsonl (one JSON line per game), progress on stderr. Turn record = list, index names in tq2_lib (F)."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8
CHECK = (10, 25, 50, 75, 100, 150, 200, 250, 300, 400)
STUDIED = (454, 157, 306, 70)


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nxt, self.por, self.kelp = [], [], []
        for y in range(h):
            for x in range(w):
                four, pf, kc = [-1, -1, -1, -1], [0, 0, 0, 0], 0
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        kc += 1
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        four[d] = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                        pf[d] = 1
                    else:
                        four[d] = ((y + dy) % h) * w + (x + dx) % w
                self.nxt.append(four)
                self.por.append(pf)
                self.kelp.append(kc)
        self.balls = {}
        self.comp = self.components()

    def ball(self, src):
        s = self.balls.get(src)
        if s is None:
            s = {src: 0}
            q = deque([src])
            while q:
                c = q.popleft()
                if s[c] >= CAP:
                    continue
                for t in self.nxt[c]:
                    if t >= 0 and t not in s:
                        s[t] = s[c] + 1
                        q.append(t)
            self.balls[src] = s
        return s

    def components(self):
        n = self.w * self.h
        comp = [0] * n
        seen = [False] * n
        for root in range(n):
            if seen[root]:
                continue
            seen[root] = True
            cells = [root]
            q = deque([root])
            while q:
                c = q.popleft()
                for t in self.nxt[c]:
                    if t >= 0 and not seen[t]:
                        seen[t] = True
                        cells.append(t)
                        q.append(t)
            for c in cells:
                comp[c] = len(cells)
        return comp


def scan(path, own_letter, info, geos):
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
    key = (w, h, tuple(sorted(raw)))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    nxt = g.nxt

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    queen = [min(i for i in bodies if teams[i] == 0), min(i for i in bodies if teams[i] == 1)]
    start = [bodies[queen[0]][0], bodies[queen[1]][0]]
    startlen = [len(bodies[queen[0]]), len(bodies[queen[1]])]
    nstart = [sum(1 for i in teams if teams[i] == 0), sum(1 for i in teams if teams[i] == 1)]
    recs = [[], []]
    fate = [None, None]
    splits, attacks, bodykills = [[], []], [[], []], [[], []]
    snaps = {}
    present = {}
    st = dict(rnd=-1, actor=None, used=0, dirs=[], ate=[0, 0, 0], act=2, child=0, died=0, open=None, shead=0, slen=0,
              drops=0, dside=0, hit=0)

    def snap():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if teams[i] == s]
            out.append([len(bodies.get(queen[s], ())), len(ls), max(ls, default=0), sum(ls)])
        return out

    def close_turn():
        o = st['open']
        if o is None:
            return
        s, rec, threats = o
        q = queen[s]
        alive = q in bodies
        rec[19], rec[20], rec[25], rec[28] = st['act'], st['used'], st['died'], st['child']
        rec[22] = sum(st['ate'])
        rec[38], rec[39], rec[40] = st['ate'][0], st['ate'][1], st['ate'][2]
        rec[41] = st['hit']
        rec[21] = len(bodies[q]) if alive else 0
        rec[23] = bodies[q][0] if alive else -1
        if threats and alive:
            ball = g.ball(bodies[q][0])
            rec[24] = min(ball.get(t, 9) for t in threats)
        st['open'] = None

    def open_turn(s, q):
        b = bodies[q]
        head, L = b[0], len(b)
        ball = g.ball(head)
        occupied = set()
        ob2 = 0
        own_heads, en = [], []
        longest_other = 0
        for i, bb in bodies.items():
            occupied.update(bb)
            if teams[i] == s:
                if i != q:
                    own_heads.append(bb[0])
                    if len(bb) > longest_other:
                        longest_other = len(bb)
                    for c in bb:
                        if man(c, head) <= 2:
                            ob2 += 1
            else:
                en.append((i, bb[0], len(bb)))
        od = [man(head, x) for x in own_heads]
        o3 = sum(1 for x in od if x <= 3)
        o5 = sum(1 for x in od if x <= 5)
        nom = min(od, default=20)
        e3m = e5m = ep3 = ep3n = ep5n = inr = sep = ep3s = 0
        ne, neL, nem, nearest = 9, 0, 20, -1
        threats = []
        tmin, tmax = 0, 0
        eq = queen[1 - s]
        for i, eh, eL in en:
            m = man(head, eh)
            p = ball.get(eh, 9)
            if m <= 3:
                e3m += 1
                if p > 3:
                    sep += 1
            if m <= 5:
                e5m += 1
            if m < nem:
                nem, nearest = m, eh
            if p < ne:
                ne, neL = p, eL
            if p <= 3:
                ep3 += 1
                if i != eq:
                    ep3n += 1
                    threats.append(eh)
                    tmin = eL if tmin == 0 else min(tmin, eL)
                    tmax = max(tmax, eL)
                    if eL <= 4:
                        ep3s += 1
            if p <= 5 and i != eq:
                ep5n += 1
            if i != eq and p <= (eL + 3) // 4 + eL - 2:
                inr += 1
        mn = -1
        if nem <= 8:
            mn = int(any(man(x, nearest) < nem for x in own_heads))
        fx = sum(1 for t in nxt[head] if t >= 0 and t not in occupied)
        db = min((ball.get(t, 9) for t in threats), default=-1)
        pd, p3 = 9, 0
        for c in present:
            dd = ball.get(c, 9)
            if dd < pd:
                pd = dd
            if dd <= 3:
                p3 += 1
        eqd = ball.get(bodies[eq][0], 9) if eq in bodies else -1
        rec = [st['rnd'], head, L, man(head, start[s]), o3, o5, e3m, e5m, ep3, ne, neL, min(nem, 20), min(nom, 20), g.kelp[head], fx,
               0, mn, inr, ob2, 2, 0, 0, 0, -1, -1, 0, 0, ep3n, 0, sep, db, ep5n, 0, len(own_heads) + 1, len(en), pd, p3, ep3s,
               0, 0, 0, 0, longest_other, tmin, tmax, eqd]
        recs[s].append(rec)
        st['open'] = (s, rec, threats)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            if st['rnd'] in CHECK:
                snaps[st['rnd']] = snap()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            close_turn()
            a = p.i32(0)
            st['actor'], st['used'], st['dirs'], st['ate'], st['act'], st['child'], st['died'], st['hit'] = a, 0, [], [0, 0, 0], 2, 0, 0, 0
            st['shead'], st['slen'] = bodies[a][0], len(bodies[a])
            s = teams[a]
            if a == queen[s]:
                open_turn(s, a)
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            st['dirs'] = [int(x) for x in a.pointer(0)] if a and kind == 0 and a.pointer(0) is not None else []
            st['act'] = min(kind, 2)
        elif k == 3:
            c = tile(p.pointer(0))
            if p.u32(0):
                if st['drops'] > 0:
                    st['drops'] -= 1
                    present[c] = 1 + st['dside']
                else:
                    present[c] = 0
            else:
                origin = present.pop(c, 0)
                a = st['actor']
                if a is not None and a in teams:
                    s = teams[a]
                    if a == queen[s]:
                        st['ate'][0 if origin == 0 else 1 if origin - 1 == s else 2] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == st['actor']:
                    st['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
            teams[child] = 0 if 'AB'[p.u16(8)] == own_letter else 1
            s = teams[parent]
            if parent == queen[s]:
                splits[s].append([st['rnd'], st['slen'], len(bodies[parent]), len(bodies[child])])
                st['child'] = len(bodies[child])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            actor = st['actor']
            b = bodies[i]
            st['drops'] += (len(b) + 1) // 2
            st['dside'] = s
            if i == queen[s]:
                head = b[0]
                mates = [man(head, bb[0]) for j, bb in bodies.items() if teams[j] == s and j != i]
                f = dict(r=st['rnd'], L=len(b), reason=reason, own_move=int(i == actor), ds=man(head, start[s]), o3=sum(1 for x in mates if x <= 3),
                         o5=sum(1 for x in mates if x <= 5), kelp=g.kelp[head], head=head, act=st['act'], ndirs=len(st['dirs']),
                         used=st['used'], mates=len(mates), slen=st['slen'] if i == actor else len(b))
                if i != actor and actor is not None:
                    f.update(mover=actor, mside=teams[actor], mL=st['slen'], msteps=st['used'] + 1, mdist=man(st['shead'], head),
                             mqueen=int(actor == queen[teams[actor]]))
                    if recs[s]:
                        recs[s][-1][26] = 1
                elif i == actor:
                    st['died'] = (1, 2, 3, 4, 5)[min(reason, 4)]
                fate[s] = f
            if actor is not None and i != actor and reason == 3 and actor == queen[teams[actor]]:
                attacks[teams[actor]].append([st['rnd'], st['slen'], len(b), int(i == queen[s]), int(teams[actor] != s)])
                st['hit'] = len(b)
            if reason == 2 and i == actor and st['used'] < len(st['dirs']):
                dest = nxt[b[0]][st['dirs'][st['used']]]
                eq = queen[1 - s]
                if eq in bodies and dest in bodies[eq]:
                    bodykills[1 - s].append([st['rnd'], len(b), len(bodies[eq])])
            bodies.pop(i)
    close_turn()
    final = snap()
    res = root.pointer(4)
    winner = ('A', 'B')[res.u16(6)] if res.u16(4) == 1 else None
    win = None if winner is None else int(winner == own_letter)
    if not final[0][1] or not final[1][1]:
        decided = 'elimination'
    elif final[0][0] != final[1][0]:
        decided = 'queen'
    elif final[0][2] != final[1][2]:
        decided = 'longest'
    else:
        decided = 'total'
    out = dict(info)
    out.update(w=w, h=h, cells=w * h, win=win, decided=decided, last=st['rnd'], start=start, queen=queen, recs=recs, fate=fate,
               splits=splits, attacks=attacks, bodykills=bodykills, snaps=snaps, final=final, startlen=startlen, nstart=nstart,
               scomp=[g.comp[start[0]], g.comp[start[1]]])
    return out


def meta_job(rp, mp, team, src, battle):
    meta = json.loads(mp.read_text())
    if team is None:
        team = meta['teamAId'] if meta['teamAId'] in STUDIED else meta['teamBId']
    if meta['teamAId'] == team:
        own, other = 'A', 'B'
    elif meta['teamBId'] == team:
        own, other = 'B', 'A'
    else:
        return None
    return (rp, own, dict(game=meta['id'], src=src, battle=battle, map=meta['mapName'], t=[meta['team' + own + 'Id'], meta['team' + other + 'Id']],
                          names=[meta['team' + own + 'Name'], meta['team' + other + 'Name']],
                          elo=[meta.get('team' + own + 'Elo'), meta.get('team' + other + 'Elo')], meta_winner=meta.get('winner'),
                          ranked=meta.get('ranked')))


def folder_jobs(folder, team, src, battle):
    jobs = []
    for rp in sorted(folder.glob('M*.replay')):
        mp = folder / ('game-' + rp.stem[1:] + '.json')
        if not mp.exists():
            continue
        j = meta_job(rp, mp, team, src, battle)
        if j is not None:
            jobs.append(j)
    return jobs


def jobs_top3():
    base = Path('data/online/top3')
    who = {}
    upto = 0
    for a in sys.argv:
        if a.startswith('upto'):
            upto = int(a[4:])
    rows = [json.loads(line) for line in (base / 'index.jsonl').read_text().splitlines() if line.strip()]
    for r in (rows[:upto] if upto else rows):
        who[str(r['battle'])] = r['team']
    jobs = []
    for folder in sorted(x for x in base.iterdir() if x.is_dir()):
        if upto and folder.name not in who:
            continue
        jobs += folder_jobs(folder, who.get(folder.name), 'top3', folder.name)
    return jobs


def jobs_top1(team):
    base = Path('data/online/top1')
    jobs = []
    for line in Path('data/top1/index.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if (r['team'] != team) if team else (r['team'] in (91, 264, 306, 842, 454)):
            continue
        folder = base / str(r['battle'])
        if folder.is_dir():
            jobs += folder_jobs(folder, r['team'], 'top1', str(r['battle']))
    return jobs


def emit(tag, body):
    if tag == 'top3-0':
        Path(WORK + 'tq2_scan-top3-0.jsonl').write_text(body)
    elif tag == 'top3-1':
        Path(WORK + 'tq2_scan-top3-1.jsonl').write_text(body)
    elif tag == 't91-0':
        Path(WORK + 'tq2_scan-t91-0.jsonl').write_text(body)
    elif tag == 't91-1':
        Path(WORK + 'tq2_scan-t91-1.jsonl').write_text(body)
    elif tag == 't264-0':
        Path(WORK + 'tq2_scan-t264-0.jsonl').write_text(body)
    elif tag == 't264-1':
        Path(WORK + 'tq2_scan-t264-1.jsonl').write_text(body)
    elif tag == 't306-0':
        Path(WORK + 'tq2_scan-t306-0.jsonl').write_text(body)
    elif tag == 't306-1':
        Path(WORK + 'tq2_scan-t306-1.jsonl').write_text(body)
    elif tag == 't0-0':
        Path(WORK + 'tq2_scan-t0-0.jsonl').write_text(body)
    elif tag == 't0-1':
        Path(WORK + 'tq2_scan-t0-1.jsonl').write_text(body)
    elif tag == 't842-0':
        Path(WORK + 'tq2_scan-t842-0.jsonl').write_text(body)
    elif tag == 't454-0':
        Path(WORK + 'tq2_scan-t454-0.jsonl').write_text(body)
    elif tag == 'agg8-q1':
        Path(WORK + 'tq2_scan-q1.jsonl').write_text(body)
    elif tag == 'agg7-m1':
        Path(WORK + 'tq2_scan-m1.jsonl').write_text(body)
    elif tag == 'agg7-m2':
        Path(WORK + 'tq2_scan-m2.jsonl').write_text(body)
    elif tag == 'agg7-m3':
        Path(WORK + 'tq2_scan-m3.jsonl').write_text(body)
    elif tag == 'top-l1':
        Path(WORK + 'tq2_scan-l1.jsonl').write_text(body)
    elif tag == 'top-l2':
        Path(WORK + 'tq2_scan-l2.jsonl').write_text(body)
    else:
        Path(WORK + 'tq2_scan-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'top3':
        jobs = jobs_top3()
        shard, shards = int(sys.argv[2]), int(sys.argv[3])
        tag = 'top3-' + sys.argv[2]
    elif src == 'top1':
        jobs = jobs_top1(int(sys.argv[2]))
        shard, shards = int(sys.argv[3]), int(sys.argv[4])
        tag = 't' + sys.argv[2] + '-' + sys.argv[3]
    else:
        jobs = folder_jobs(Path('data/online/smoke') / (sys.argv[2] + ('-old' if sys.argv[2].startswith('top-l') else '-new')), 1119, sys.argv[2], sys.argv[2])
        shard, shards = 0, 1
        tag = sys.argv[2]
    seen = set()
    uniq = []
    for j in jobs:
        if j[2]['game'] not in seen:
            seen.add(j[2]['game'])
            uniq.append(j)
    jobs = [j for n, j in enumerate(uniq) if n % shards == shard]
    if sys.argv[-1].startswith('limit'):
        jobs = jobs[:int(sys.argv[-1][5:])]
        tag = 'test'
    geos, bad, out = {}, [], []
    for n, (path, own, info) in enumerate(jobs):
        try:
            rec = scan(path, own, info, geos)
            if info.get('meta_winner') in ('a', 'b'):
                assert (rec['win'] == 1) == (info['meta_winner'].upper() == own), (rec['win'], info['game'])
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((info['game'], repr(e)[:300]))
        if n % 20 == 19:
            sys.stderr.write('%d %d bad %d\n' % (n + 1, len(jobs), len(bad)))
            sys.stderr.flush()
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
