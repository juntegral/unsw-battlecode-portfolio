#!/usr/bin/env python3
"""No-argument room counts for completed ladder Stripes/Portals local replays.

Ports work/st_scan.py, st_known.py, st_rooms.py, st_open.py, st_pergame.py.
Only writes beside this script; never starts games or accesses the network.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from replay_format import load, point
from count_local import Geo as LocalGeo, STEP

HERE = Path(__file__).resolve().parent
RUNS = Path('~/meow-redteam/solo/runs')
LAYOUTS = ('ladder_stripes_1', 'ladder_portals_1')
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'no action')


def event_value(k, p):
    if k in (0, 1):
        return [k, p.i32(0)]
    if k == 3:
        return [k, p.u32(0), point(p.pointer(0))]
    if k == 9:
        return [k, p.i32(0), point(p.pointer(0)), point(p.pointer(1))]
    if k == 10:
        return [k, p.i32(0), p.i32(4), p.u16(8),
                [point(c) for c in p.pointer(0)], [point(c) for c in p.pointer(1)]]
    return [k, p.i32(0), p.u16(4)]


class Geo(LocalGeo):
    def __init__(self, w, h, raw):
        super().__init__(w, h, raw)
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
    root = load(Path(rec['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = (w, h, tuple(raw))
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
    turns, snaps, deaths, events = [], [], [], []
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
        events.append(event_value(k, p))
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
            c = tile(point(p.pointer(0)))
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
            hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
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
                bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
                teams[i] = p.u16(8)
            parent[c2] = a
            if cur is not None:
                cur['split'] = [c2, list(bodies[c2]), list(bodies[a])]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            deaths.append(dict(r=rnd, id=i, s=side(i), head=bodies[i][0], L=len(bodies[i]), cause=CAUSE[reason], actor=i == actor))
            if cur is not None:
                if i == actor:
                    cur['died'] = CAUSE[reason]
                else:
                    cur['kills'] += 1
            bodies.pop(i)
    finish()
    snapshot(rnd)
    result = root.pointer(4)
    assert result is not None and result.bit(0), 'unfinished replay'
    winner = result.u16(6) if result.u16(4) == 1 else None
    for z in (0, 1):
        s = 'u' if z == ours else 't'
        st = result.pointer(z)
        ls = [len(b) for i, b in bodies.items() if side(i) == s]
        assert (len(ls), sum(ls), max(ls, default=0)) == (st.i32(0), st.i32(8), st.i32(4)), 'standings mismatch'
        queen = min(i for i in starts if side(i) == s)
        assert len(bodies.get(queen, ())) == st.i32(12), 'queen mismatch'
    return dict(**rec, result='draw' if winner is None else 'win' if winner == ours else 'loss',
                winner=winner, last_round=rnd, w=w, h=h, comp=g.comp, size=g.size, loop=g.loop,
                turns=turns, snaps=snaps, deaths=deaths,
                gameplay_hash=hashlib.sha256(json.dumps([w,h,raw,events,winner], separators=(',', ':')).encode()).hexdigest(),
                pearls=[[q['c'], q['b'], q['o'], q['by'], q['er'], q['eid'], q['eL'], q['eq']] for q in pearls])

def room_class(g, c):
    cp = g['comp'][c]
    return 'main' if g['size'][cp] >= 48 else ('loop%d' if g['loop'][cp] else 'dead%d') % g['size'][cp]


def visits_of(g):
    # st_rooms: turn-end pearl attribution and first-turn births are intentional.
    comp, size = g['comp'], g['size']
    where, openv, visits = {}, {}, []
    for t in g['turns']:
        i = t['id']
        if i not in where:
            where[i] = comp[t['head']]
            if size[where[i]] < 48 and i not in openv:
                openv[i] = dict(s=t['s'], id=i, r=t['r'], L=t['L'], k=room_class(g, t['head']),
                                born=1, ate=0, splits=0, out=None, turns=0, kids_out=0)
        v = openv.get(i)
        if v is not None:
            v['turns'] += 1
        for c in t['steps']:
            cp = comp[c]
            if cp != where[i]:
                if v is not None:
                    v.update(out='left', rout=t['r'], Lout=t['L']+t['ate'])
                    visits.append(v)
                    v = None
                    openv.pop(i)
                if size[cp] < 48:
                    v = dict(s=t['s'], id=i, r=t['r'], L=t['L'], k=room_class(g, c),
                             born=0, ate=0, splits=0, out=None, turns=1, kids_out=0)
                    openv[i] = v
                where[i] = cp
        if v is not None:
            v['ate'] += t['ate']
            if t['split'] is not None:
                v['splits'] += 1
                v['kids_out'] += size[comp[t['split'][1][0]]] >= 48
            if t['died'] is not None:
                v.update(out=t['died'], rout=t['r'])
                visits.append(v)
                openv.pop(i)
        if t['died'] is not None:
            where.pop(i, None)
            openv.pop(i, None)
    for v in openv.values():
        v['out'] = 'open at end'
        visits.append(v)
    return visits


def measure(g):
    dec, eats = Counter(), Counter()
    seen, first, door = {}, {}, {}
    for t in g['turns']:
        i, s = t['id'], t['s']
        y, x = divmod(t['head'], g['w'])
        win = {((y+dy)%g['h'])*g['w']+(x+dx)%g['w'] for dy in range(-3,4) for dx in range(-3,4)}
        seen.setdefault(i, set()).update(win)
        fd = t['dirs'][0][0] if t['dirs'] else None
        for d, o in enumerate(t['opts']):
            if o is None or o[0] != 2 or o[2] >= 48 or o[6] != 0:
                continue
            if t['r'] <= 60 and o[5] > 0:
                door.setdefault(s, t['r'])
                if fd == d:
                    first.setdefault(s, t['r'])
            if t['hs'] < 48 or not o[4]:
                continue
            if o[3] and o[1] in seen[i] and t['L'] <= 3:
                lb = 2 if t['L'] <= 2 else 3  # st_known's "2" bucket includes L<=2.
                dec[s, f'loop_L{lb}_chances'] += 1
                dec[s, f'loop_L{lb}_taken'] += fd == d
            elif not o[3] and o[2] == 3:
                dec[s, 'dead3_chances'] += 1
                dec[s, 'dead3_taken'] += fd == d
    for c, b, o, by, er, eid, eL, eq in g['pearls']:
        if by is None:
            continue
        for lim in (50, 100):
            if er <= lim:
                eats[by, f'pearls_r{lim}'] += 1
                eats[by, room_class(g, c), lim] += 1
    visits = visits_of(g)
    out = {}
    for s, name in (('u','ours'), ('t','theirs')):
        m = {f'pearls_r{lim}': eats[s, f'pearls_r{lim}'] for lim in (50,100)}
        snap = next(v for v in reversed(g['snaps']) if v[0] <= 100)
        z = 1 if s == 'u' else 4
        m.update(dragons_r100=snap[z], total_length_r100=snap[z+1],
                 first_pearl_door_r60=door.get(s,999), first_pearl_entry_r60=first.get(s,999),
                 no_pearl_entry_by_r60=s not in first)
        for f in ('loop_L2_taken','loop_L2_chances','loop_L3_taken','loop_L3_chances','dead3_taken','dead3_chances'):
            m[f] = dec[s,f]
        for k in ('loop','dead3','dead1'):
            select = lambda v: v['k'].startswith('loop') if k == 'loop' else v['k'] == k
            vs = [v for v in visits if v['s'] == s and select(v)]
            ds = [d for d in g['deaths'] if d['s'] == s and
                  (room_class(g,d['head']).startswith('loop') if k == 'loop' else room_class(g,d['head']) == k)]
            actual_eat = sum(1 for p in g['pearls'] if p[3] == s and
                            (room_class(g,p[0]).startswith('loop') if k == 'loop' else room_class(g,p[0]) == k))
            deadlen = sum(d['L'] for d in ds)
            # st_pergame proxy retained separately: start head, turn-start L + total turn pearls.
            ladder_deadlen = sum(t['L']+t['ate'] for t in g['turns'] if t['s'] == s and t['died'] is not None and
                                (room_class(g,t['head']).startswith('loop') if k == 'loop' else room_class(g,t['head']) == k))
            m.update({k+'_visits':len(vs), k+'_left':sum(v['out']=='left' for v in vs),
                      k+'_visit_pearls':sum(v['ate'] for v in vs),
                      k+'_split_child_outside_visits':sum(v['kids_out']>0 for v in vs),
                      k+'_pearls_r100':sum(n for (ss,kk,*ll),n in eats.items() if ll == [100] and ss == s and
                                             (str(kk).startswith('loop') if k == 'loop' else kk == k)),
                      k+'_death_length':deadlen, k+'_area_pearls_all':actual_eat,
                      k+'_net':actual_eat-deadlen, k+'_ladder_death_length_proxy':ladder_deadlen})
        m['room_deaths_by_cause'] = {c:sum(d['s']==s and g['size'][g['comp'][d['head']]]<48 and d['cause']==c for d in g['deaths']) for c in CAUSE}
        out[name] = m
    return out


def fmt(x):
    return '—' if x is None else f'{x:.3f}'.rstrip('0').rstrip('.')


def table(rows, arms, skipped, inventories):
    lines = ['# 로컬 작은 포털 방 집계', '',
             '작성: '+datetime.now().astimezone().isoformat(timespec='seconds')+'; 아래 일반 값은 경기 평균, 각 칸은 우리 / 상대. 0경기는 —.',
             '진주·개체·길이는 원시 라운드 끝 기준(포함), 조기 종료는 최종 상태. 방 행동·사망은 전체 경기.', '']
    def avg(rs, s, f):
        return mean(r['measures'][s][f] for r in rs) if rs else None
    def cell(rs, f):
        return ' / '.join(fmt(avg(rs,s,f)) for s in ('ours','theirs'))
    def ratio(rs, s, num, den):
        return sum(r['measures'][s][num] for r in rs)/max(1,sum(r['measures'][s][den] for r in rs)) if rs else None
    def rc(rs,num,den):
        return ' / '.join(fmt(ratio(rs,s,num,den)) for s in ('ours','theirs'))
    def chance(rs,stem):
        return ' / '.join(fmt(avg(rs,s,stem+'_taken'))+' : '+fmt(avg(rs,s,stem+'_chances')) for s in ('ours','theirs'))
    for layout in LAYOUTS:
        lines += ['## '+layout, '',
          '| arm | 경기 | 승 우리/상대 | P50 | P100 | D100 | L100 | loop L2 취함:기회 | loop L3 취함:기회 | loop 방문 | 생환 비율 | P/방문 | loop P100 | dead3 취함:기회 | dead3 방문 | P/방문 | 밖 새끼 분열 방문 | 순길이/방문 | dead3 P100 | dead1 방문 | 순길이/경기 | 순길이/방문 | 첫 진주문 중앙값 | 첫 진주방 중앙값 | r60 무진입 | 우리 방 사망 원인 |',
          '|'+ '---|'*26]
        for arm in arms:
            rs = [r for r in rows if r['layout']==layout and r['arm']==arm]
            vals = [arm,str(len(rs)),f'{sum(r["result"]=="win" for r in rs)} / {sum(r["result"]=="loss" for r in rs)}']
            vals += [cell(rs,f) for f in ('pearls_r50','pearls_r100','dragons_r100','total_length_r100')]
            vals += [chance(rs,'loop_L2'),chance(rs,'loop_L3'),cell(rs,'loop_visits'),rc(rs,'loop_left','loop_visits'),rc(rs,'loop_visit_pearls','loop_visits'),cell(rs,'loop_pearls_r100'),chance(rs,'dead3'),cell(rs,'dead3_visits'),rc(rs,'dead3_visit_pearls','dead3_visits'),cell(rs,'dead3_split_child_outside_visits'),rc(rs,'dead3_net','dead3_visits'),cell(rs,'dead3_pearls_r100'),cell(rs,'dead1_visits'),cell(rs,'dead1_net'),rc(rs,'dead1_net','dead1_visits')]
            vals += [fmt(median(r['measures']['ours'][f] for r in rs)) if rs else '—' for f in ('first_pearl_door_r60','first_pearl_entry_r60')]
            vals += [str(sum(r['measures']['ours']['no_pearl_entry_by_r60'] for r in rs)), ', '.join(c+' '+fmt(mean(r['measures']['ours']['room_deaths_by_cause'][c] for r in rs)) for c in CAUSE) if rs else '—']
            lines.append('| '+' | '.join(vals)+' |')
    lines += ['', '## 같은 지도·시드·우리 편의 base 쌍', '',
              '| 지도 | arm | 쌍 | 행동 기보 다름 | ΔP100 | ΔD100 | Δloop 방문 | Δdead3 방문 | Δ승 |', '|'+ '---|'*9]
    base = {(r['layout'],r['seed'],r['our_side']):r for r in rows if r['arm']=='base'}
    for layout in LAYOUTS:
        for arm in arms:
            if arm == 'base':
                continue
            ps = [(base[(r['layout'],r['seed'],r['our_side'])],r) for r in rows if r['layout']==layout and r['arm']==arm and (r['layout'],r['seed'],r['our_side']) in base]
            ds = [fmt(mean(r['measures']['ours'][f]-b['measures']['ours'][f] for b,r in ps)) if ps else '—' for f in ('pearls_r100','dragons_r100','loop_visits','dead3_visits')]
            ds += [fmt(mean(int(r['result']=='win')-int(b['result']=='win') for b,r in ps)) if ps else '—']
            lines.append('| '+' | '.join([layout,arm,str(len(ps)),str(sum(b['gameplay_hash']!=r['gameplay_hash'] for b,r in ps))]+ds)+' |')
    lines += ['',
      '정의: st_known 그대로 열린 큰 영역(≥48)에서 비점유 진주 입구로 가는 첫 포털 걸음; loop는 본 개체의 누적 7×7 관측에 목적지가 있을 때만. L2는 원본처럼 L≤2. 새끼 관측은 별도 시작.',
      '방: 일반 열린 변으로만 연결한 성분 <48; loop는 성분 내부 포털 변이 밖으로 연결됨. Stripes는 stripes-rooms.json과 일치 검증; Portals도 같은 방식. 방 크기별 개수: '+json.dumps(inventories,ensure_ascii=False,sort_keys=True)+'.',
      '방문·생환·P/방문·밖 새끼는 st_rooms 그대로: 첫 턴 방 안 출생 포함, 성분 변경마다 방문; 최종 방에 턴 전체 섭취 귀속, 밖 새끼는 큰 영역(≥48). 비율은 전체 방문 합으로 나눔; 방문 0이면 0.',
      '원본 한계 유지: st_rooms는 다른 개체 턴에 죽은 방문자를 open at end로 남김. 방문 생환/섭취는 이 정의를 보존. st_open처럼 r0–60 첫 문/첫 진입, 미진입=999를 포함한 중앙값.',
      '순길이/방문은 실제 방 타일 섭취−사망 직전 실제 길이(비행동 개체 사망 포함)를 방문 수로 나눔. st_pergame의 턴 시작 위치·L+턴 섭취 사망 근사와 다르며 JSON에 그 근사도 별도 보존. 사망 원인은 모든 실제 방 내부 사망.',
      '쌍 차이는 arm−base, 동일 라운드/턴/진주/몸 이동/분열/사망 순서와 결과를 비교. CPU·로그·제출 이름은 제외; 전체 행동 상태 사건의 해시를 사용. 행 JSON은 경기별 원시 분자·분모 포함.',
      '대상 폴더: '+', '.join(arms)+'. '+str(len(rows))+'경기 집계; 건너뜀 '+str(len(skipped))+'개. 상세: '+ ('; '.join(skipped) if skipped else '없음')+'.']
    assert len(lines)<=70, f'table exceeds 70 lines: {len(lines)}'
    return '\n'.join(lines)+'\n'


def main():
    arms = ['base','pl','hp','plhp']
    folders = []
    if RUNS.exists():
        for a in sorted(RUNS.iterdir()):
            if not a.is_dir():
                continue
            for d in sorted(a.iterdir()):
                mt = re.fullmatch(r'(ladder_(?:stripes|portals)_1)-seed(\d+)-side([01])',d.name)
                if d.is_dir() and mt:
                    if a.name not in arms:
                        arms.append(a.name)
                    folders.append((a.name,d,mt.groups()))
    geos, inventories = {}, {}
    for layout in LAYOUTS:
        text = (HERE/'maps3/structure'/f'{layout}.map').read_text()
        w,h = map(int,text.splitlines()[0].split()[1:3])
        raw = [tuple(map(int,q[1:4])) for line in text.splitlines() if (q:=line.split()) and q[0]=='EDGE']
        g = Geo(w,h,raw)
        inventories[layout] = dict(Counter(('loop' if g.loop[i] else 'dead')+str(sz) for i,sz in enumerate(g.size) if sz<48))
        if layout == 'ladder_stripes_1':
            for r in json.loads((HERE/'maps3/stripes-rooms.json').read_text()):
                cs = [t['y']*w+t['x'] for t in r['tiles']]
                cp = g.comp[cs[0]]
                assert set(cs)=={c for c in range(w*h) if g.comp[c]==cp}
                assert g.size[cp]==r['size'] and bool(g.loop[cp])==(r['kind']=='loop')
    version = hashlib.sha256(Path(__file__).read_bytes()+(HERE/'replay_format.py').read_bytes()+(HERE/'count_local.py').read_bytes()).hexdigest()
    cache = {}
    if (HERE/'rooms-rows.jsonl').exists():
        for line in (HERE/'rooms-rows.jsonl').read_text().splitlines():
            r = json.loads(line)
            cache[r['replay']] = r
    rows, skipped = [], []
    for arm,folder,(layout,seed,side) in folders:
        path=folder/'game.replay'
        label=arm+'/'+folder.name
        if not path.exists():
            skipped.append(label+': 아직 기보 없음')
            continue
        try:
            meta=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {}
            if meta.get('bot_errors') or meta.get('crash') or meta.get('error'):
                skipped.append(label+': bot error/crash')
                continue
            st=path.stat()
            signature=[version,st.st_size,st.st_mtime_ns]
            row=cache.get(str(path))
            if not row or row.get('_signature')!=signature:
                rec=dict(arm=arm,layout=layout,seed=int(seed),our_side=int(side),replay=str(path))
                game=scan(rec,geos)
                row={**rec, 'result':game['result'], 'winner':game['winner'], 'last_round':game['last_round'],
                     'gameplay_hash':game['gameplay_hash'], 'measures':measure(game), '_signature':signature}
            assert (path.stat().st_size,path.stat().st_mtime_ns)==(st.st_size,st.st_mtime_ns), 'replay changed; rerun'
            if meta:
                assert meta.get('winner',row['winner'])==row['winner'], 'result winner mismatch'
                assert meta.get('rounds',row['last_round']+1)==row['last_round']+1, 'result rounds mismatch'
            rows.append(row)
        except Exception as err:
            skipped.append(label+': '+type(err).__name__+': '+str(err))
    report=table(rows,arms,skipped,inventories)
    (HERE/'rooms-rows.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows))
    (HERE/'rooms-table.md').write_text(report)
    print(f'{len(rows)} games; {len(skipped)} skipped; {len(report.splitlines())} table lines')
    (HERE/'rooms-done.txt').write_text(datetime.now().astimezone().isoformat(timespec='seconds')+f' 완료: {len(rows)}경기, {len(skipped)}건 건너뜀; rooms-table.md\n')


if __name__=='__main__':
    main()
