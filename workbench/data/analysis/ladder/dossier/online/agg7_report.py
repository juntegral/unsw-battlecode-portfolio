#!/usr/bin/env python3
"""Offline agg7 smoke report. Existing inputs are read-only; all outputs stay here."""
import sys
sys.dont_write_bytecode = True
import hashlib
import ast
import json
import math
import re
import struct
import subprocess
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOS = HERE.parent
ROOT = DOS.parents[3]
SMOKE = ROOT / 'data/online/smoke'
sys.path.insert(0, str(DOS / 'local'))
import scoreboard as sb
import spawn
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2', 'sr51-bob1')
ARMS = ('MAIN', 'B7', 'B7Q', 'B10')
COMMAND = 'nice -n 10 python3 -B data/analysis/ladder/dossier/online/agg7_report.py'


def size(cells):
    return '<=700' if cells <= 700 else '701-1200' if cells <= 1200 else '>1200'


def fmt(x):
    return 'NA' if x is None else f'{x:.3f}'


def ratio(n, d):
    return n / d if d else None


def inventory():
    found, missing, jobs, notes = [], [], [], []
    seen = set()
    for label in (*LABELS, *sorted({'agg9-a1'} | {p.stem for p in SMOKE.glob('agg9-a*.json')})):
        path = SMOKE / (label + '.json')
        if not path.exists():
            missing.append(label)
            continue
        found.append(label)
        try:
            state = json.loads(path.read_text())
            half = state['halves']['new']
            ids = half['battle_ids']
            if not isinstance(ids,list) or not all(isinstance(gid,int) for gid in ids):
                raise TypeError('pending battle ids')
        except (json.JSONDecodeError, KeyError, TypeError):
            if not label.startswith('agg9-a'):
                raise
            notes.append(f'{label}: pending state file')
            continue
        assert len(ids) == len(set(ids)), (label, 'duplicate battle ids')
        folder = SMOKE / (label + '-new')
        available = {int(p.stem[1:]) for p in folder.glob('M*.replay')}
        assert label.startswith('agg9-a') or not available - set(ids), (label, 'unlisted replay', available - set(ids))
        for gid in ids:
            rp, mp = folder / f'M{gid}.replay', folder / f'game-{gid}.json'
            if not rp.exists() or not mp.exists():
                notes.append(f'{label}: pending game {gid}')
                continue
            assert gid not in seen, ('game appears in multiple labels', gid)
            seen.add(gid)
            try:
                meta = json.loads(mp.read_text())
                if label.startswith('agg9-a') and (not isinstance(meta,dict) or not all(k in meta for k in ('id', 'teamAId', 'teamBId', 'winner', 'scoresA', 'scoresB', 'mapName', 'mapId', 'teamAName', 'teamBName'))):
                    raise ValueError('incomplete metadata')
            except (json.JSONDecodeError, ValueError, TypeError, IndexError, AssertionError, OSError, EOFError, struct.error, AttributeError):
                if not label.startswith('agg9-a'):
                    raise
                seen.remove(gid)
                notes.append(f'{label}: pending input game {gid}')
                continue
            assert meta['id'] == gid and 1119 in (meta['teamAId'], meta['teamBId'])
            jobs.append((label, rp, meta))
        if len(ids) < state.get('planned_total', len(ids)):
            notes.append(f'{label}: requested {len(ids)}/{state["planned_total"]}')
    return found, missing, jobs, notes


def supplement(root, meta, geo):
    text = root.text(0)
    w, h = geo.w, geo.h
    bodies, teams = {}, {}
    cap = 64
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w + int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'UNIT_LIMIT':
            cap = int(q[1])
    own = int(meta['teamAId'] != 1119)
    side = lambda i: int(teams[i] != own)
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    def gap(a, b):
        dx, dy = abs(a % w-b % w), abs(a // w-b // w)
        return min(dx, w-dx)+min(dy, h-dy)
    start_components = {geo.component[b[0]] for b in bodies.values()}
    reach = geo.bfs([b[0] for b in bodies.values()])
    rooms = {c for c in range(w*h) if geo.component[c] not in start_components and reach[c] < 65535}
    c = Counter()
    present, deaths, late, snaps = {}, [], [], {}
    drop_pending, recent_eats, feed_candidates, fed = deque(), defaultdict(list), {}, set()
    paid_pearls = 0
    for key in ('trade_short_L3', 'trade_short_L4', 'trade_short_L5plus', 'trade_equal', 'trade_short_2plus', 'lunge_pearl', 'paid_sprint_hits', 'feeder_eat'):
        c[key] = 0
    rnd, actor, turn, used, dirs = -1, None, {}, 0, []
    action_cause = None
    first10 = None
    queen_splits = []
    def state():
        return [dict(alive=sum(side(i) == s for i in bodies),
                     longest=max((len(b) for i,b in bodies.items() if side(i) == s), default=0),
                     queen_length=len(bodies.get(queens[s], ()))) for s in (0, 1)]
    def crossing():
        nonlocal first10
        if rnd >= 0 and first10 is None and w*h > 1200:
            st = state()[0]
            if st['longest'] > 10 and st['alive'] < 56:
                first10 = rnd
    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        tile = lambda z: sb.replay_format.point(z)[1]*w+sb.replay_format.point(z)[0]
        if k == 0:
            if rnd >= 0:
                snaps[rnd] = state()
            rnd, actor = p.i32(0), None
            crossing()
        elif k == 1:
            actor, used, dirs = p.i32(0), 0, []
            action_cause = None
            paid_pearls = 0
            assert actor in bodies
            turn = {i: (len(b), b[0]) for i,b in bodies.items()}
            if side(actor) == 0:
                c['turns'] += 1
                c['small_turns'] += int(2 <= len(bodies[actor]) <= 3)
                if actor == queens[0] and 0 <= rnd <= 300:
                    c['queen_turns_0_300'] += 1
                    L = len(bodies[actor])
                    c['queen_turns_L' + ('4+' if L >= 4 else str(L))] += 1
            turn_alive = sum(side(i) == side(actor) for i in bodies)
            turn_longest = {s: max((len(b) for i,b in bodies.items() if side(i) == s), default=0) for s in (0,1)}
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            fuel = p.pointer(1)
            action_cause = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)] if a and a.u16(0) < 3 else 'no action')
        elif k == 3:
            cell = tile(p.pointer(0))
            if p.u32(0):
                origin = None
                if drop_pending:
                    expected_cell, origin = drop_pending.popleft()
                    assert cell == expected_cell
                present[cell] = (rnd, actor is None, origin)
                if actor is None:
                    c['natural_born'] += 1
            else:
                birth, natural, origin = present.pop(cell)
                if side(actor) == 0:
                    c['eaten'] += 1
                    paid_pearls += int(used+1 > (turn[actor][0]+3)//4)
                    if actor != queens[0] and turn[actor][0] < turn_longest[0]:
                        recent_eats[actor].append((idx, rnd))
                    if origin in feed_candidates and rnd <= feed_candidates[origin]['round']+3 and turn[actor][0] == turn_longest[0]:
                        fed.add(origin)
                    c['small_eaten'] += int(2 <= turn[actor][0] <= 3)
                    c['natural_eaten'] += natural
                    c['wait_sum'] += rnd-birth
                    c['room100'] += int(rnd <= 100 and cell in rooms)
                    leader = min((i for i in bodies if side(i) == 0), key=lambda i: (-len(bodies[i]), i))
                    leader_round = 300 if w*h <= 1200 else 150
                    if rnd > leader_round and len(bodies[actor]) < len(bodies[leader]):
                        c['zone_nearer'] += int(gap(cell, bodies[leader][0]) <= 9 and gap(cell, turn[actor][1]) < gap(cell, bodies[leader][0]))
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            assert b[-1] == tl
            crossing()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            if side(parent) == 0:
                c['splits'] += 1
            for z,i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
                teams[i] = p.u16(8)
            if parent == queens[0]:
                queen_splits.append(dict(round=rnd, child=child, before_length=turn[parent][0],
                                         after_length=len(bodies[parent]), child_length=len(bodies[child])))
            crossing()
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            L, hd = len(bodies[i]), bodies[i][0]
            cause = ('wall', 'own body', 'another body', 'head-on mover' if i == actor else 'head-on hit',
                     action_cause or 'no action')[reason]
            d = dict(id=i, round=rnd, length=L, cause=cause, side=side(i), queen=i == queens[side(i)],
                     allies5=sum(j != i and side(j) == side(i) and gap(hd,b[0]) <= 5 for j,b in bodies.items()),
                     other=None)
            if reason == 3:
                if i != actor:
                    d['other'] = dict(id=actor, side=side(actor), length=len(bodies[actor]), start_length=turn[actor][0],
                                      steps=used+1, distance=geo.bfs([turn[actor][1]])[hd])
                    victim = d
                    if side(actor) == 0 and side(i) != 0:
                        ours = len(bodies[actor])
                        if actor != queens[0]:
                            if ours-L == 1 and ours >= 3:
                                c['trade_short_'+('L5plus' if ours >= 5 else f'L{ours}')] += 1
                            c['trade_equal'] += int(ours == L)
                            c['trade_short_2plus'] += int(ours-L >= 2)
                        paid = used+1 > (turn[actor][0]+3)//4
                        c['paid_sprint_hits'] += int(paid)
                        c['lunge_pearl'] += int(paid and paid_pearls > 0)
                        c['trade_even'] += int(L == len(bodies[actor]) and turn_alive < cap)
                        c['hunt_small'] += int(turn[actor][0] <= 4 and L >= 2*turn[actor][0])
                    if side(i) == 0 and side(actor) != 0 and rnd > 300 and i in turn and turn[i][0] == turn_longest[0]:
                        late.append([rnd, L])
                else:
                    d['other'] = dict(id=victim['id'], side=victim['side'], length=victim['length'], steps=used+1,
                                      distance=geo.bfs([turn[actor][1]])[turn[victim['id']][1]])
            if side(i) == 0:
                c['lost'] += L
                c['death:'+cause] += 1
                c['headons'] += int(reason == 3 and i == actor)
            deaths.append(d)
            if side(i) == 0 and i != queens[0]:
                feed_candidates[idx] = dict(round=rnd, eats=[ev for ev,r in recent_eats[i] if 0 <= rnd-r <= 3])
            drop_pending.extend((cell, idx) for z,cell in enumerate(bodies[i]) if z % 2 == 0)
            bodies.pop(i)
    c['feeder_eat'] = len({ev for death in fed for ev in feed_candidates[death]['eats']})
    snaps[rnd] = state()
    for checkpoint in (100,300):
        st = snaps[checkpoint] if checkpoint <= rnd else snaps[rnd]
        c[f'alive{checkpoint}'] = st[0]['alive']
        c[f'longest{checkpoint}'] = st[0]['longest']
    c['longest_end'] = snaps[rnd][0]['longest']
    qd = next((d for d in deaths if d['queen'] and d['side'] == 0), None)
    deciding = 'elimination' if not snaps[rnd][0]['alive'] or not snaps[rnd][1]['alive'] else next((name for name in ('queen_length', 'longest') if snaps[rnd][0][name] != snaps[rnd][1][name]), 'total')
    quantity = 'queen_length' if deciding == 'queen_length' else 'longest'
    passed = None
    if snaps[rnd][1][quantity] > snaps[rnd][0][quantity]:
        last_not_ahead = max((r for r,st in snaps.items() if st[1][quantity] <= st[0][quantity]), default=-1)
        passed = last_not_ahead+1
    return dict(counts=dict(c), queen_death=qd, late_rams=late, first10=first10, passed=passed,
                quantity=quantity, decided=deciding, snaps=snaps, room_cells=len(rooms), queen_splits=queen_splits)


def count_job(label, path, meta, counter):
    root = sb.load_replay(path).root()
    original_load = sb.load_replay
    sb.load_replay = lambda _: type('Loaded', (), {'root': lambda _: root})()
    captured = {}
    original_scan = counter.scan
    def scan(row):
        result = original_scan(row)
        captured['rows'], _, captured['geo'] = result
        return result
    counter.scan = scan
    own = int(meta['teamAId'] != 1119)
    try:
        fingerprint = sb.count_game(counter, path, label, (meta['mapName'], 0, own))
    finally:
        sb.load_replay, counter.scan = original_load, original_scan
    ours = next(r for r in captured['rows'] if r['relation'] == 'us')
    spawn_read = spawn.read
    spawn.read = lambda _: root
    try:
        map_source = type('MapText', (), {'read_text': lambda _: root.text(0)})()
        sp = spawn.scan(path, (meta['mapName'], 0, own), map_source)['measures'][0]
    finally:
        spawn.read = spawn_read
    extra = supplement(root, meta, captured['geo'])
    timer_events = sum(ev.u16(0) == 2 for ev in root.pointer(3))
    timer_available = timer_events > 0
    final = ours['final_reconstructed']
    their = next(r['final_reconstructed'] for r in captured['rows'] if r['relation'] == 'them')
    expected = None if fingerprint['result'] == 'draw' else 'ab'[own if fingerprint['result'] == 'win' else 1-own]
    assert meta['winner'] == expected, (path, 'metadata winner differs')
    assert meta['scores'+'AB'[own]] == final['total'] and meta['scores'+'AB'[1-own]] == their['total']
    assert extra['counts'].get('eaten', 0) == ours['game_counts'].get('pearls_eaten', 0), (path, 'pearl count mismatch')
    assert extra['counts'].get('splits', 0) == ours['game_counts'].get('splits', 0), (path, 'split count mismatch')
    return dict(label=label, game=meta['id'], arm='B10' if label.startswith('agg9-a') else 'OLD' if label == 'sr51-bob1' else 'MAIN' if '-m' in label else 'B7Q' if label.startswith('agg8-q') else 'B7',
                opponent=meta['team'+'AB'[1-own]+'Name'], opponent_id=meta['team'+'AB'[1-own]+'Id'],
                map=meta['mapName'], map_id=meta['mapId'], cells=ours['cells'], result=fingerprint['result'], timer_available=timer_available,
                final=final, their=their, rates=fingerprint['rates'], spawn=sp, extra=extra)


def sign_test(b, m):
    n = b+m
    return min(1, 2*sum(math.comb(n,k) for k in range(min(b,m)+1))/2**n) if n else None


def paired(rows, arm='B7'):
    by = {r['label']: {} for r in rows}
    for r in rows:
        key = r['opponent_id'], r['map_id']
        assert key not in by[r['label']], ('duplicate opponent/map', r['label'], key)
        by[r['label']][key] = r
    pairs = []
    for n in (1,2):
        main_label = f'agg7-m{n}' if arm == 'B7' else f'agg7-m{n+1}'
        bundle_label = f'agg7-b{n}' if arm == 'B7' else f'agg8-q{n}'
        main, bundle = by.get(main_label,{}), by.get(bundle_label,{})
        pairs.extend((n, main[k], bundle[k]) for k in sorted(main.keys() & bundle.keys()))
    return pairs


def rate(rs, n, d, scale=1, source='counts'):
    if source == 'counts':
        cs = [r['extra']['counts'] for r in rs]
    else:
        cs = [r[source] for r in rs if source != 'spawn' or r['timer_available']]
    return ratio(scale*sum(c.get(n,0) for c in cs), sum(c.get(d,0) for c in cs))


def reference_data():
    refs = json.loads((DOS/'target/scoreboard.json').read_text())
    marks = {(r['name'],r['window']): r['shared_equal_layouts'] for r in refs['rates']}
    raw = {}
    for name, path in [('R', DOS/'target/per-game-top1.jsonl'), ('O', DOS/'per-game.jsonl')]:
        raw[name] = [r for r in map(json.loads,path.read_text().splitlines()) if r['relation'] == 'us']
    return marks, raw


def pack_table_rows(lines, start):
    cells = [line.split('|')[1:-1] for line in lines[start:]]
    lines[start:] = ['| '+' | '.join('<br>'.join(row[i].strip() for row in cells) for i in range(len(cells[0])))+' |']


def report(rows, found, missing, notes, validation):
    arms = {a: [r for r in rows if r['arm'] == a] for a in (*ARMS,'OLD')}
    pairs = paired(rows)
    lines = ['# agg7 온라인 재집계', '', f'생성: {datetime.now().astimezone().isoformat(timespec="seconds")}. 팀 1119. 발견: {", ".join(found)}.',
             '미도착: '+(', '.join(missing) or '없음')+'. '+('; '.join(notes) or '현재 자료에서 누락 판 없음')+'.',
             f'검증: {len(rows)}판 각각 1회; 로그 대조 {validation}. 원자료/봇 코드 변경 없음. sr51-bob1은 모든 MAIN/B7/B7Q/B10 비교에서 제외.', '',
             '## 1. 결과', '| arm / 상대 | 판/승 | 우리/상대 최종 총길이 평균 | 결정 Q/L/T/E | 여왕 생존/평균 길이 |', '|---|---:|---:|---|---:|']
    opponents = sorted({r['opponent'] for r in rows})
    for arm in arms:
        if arm in ('B7Q','B10') and not arms[arm]:
            lines.append(f'| {arm} / 자료 없음 | 0/0 | NA | 0/0/0/0 | NA |')
        for opponent in opponents:
            rs = [r for r in arms[arm] if r['opponent'] == opponent]
            if not rs:
                continue
            dc = Counter(r['extra']['decided'] for r in rs)
            lines.append(f'| {arm} / {opponent} | {len(rs)}/{sum(r["result"]=="win" for r in rs)} | {sum(r["final"]["total"] for r in rs)/len(rs):.1f}/{sum(r["their"]["total"] for r in rs)/len(rs):.1f} | '+ '/'.join(str(dc[k]) for k in ('queen_length','longest','total','elimination'))+f' | {sum(r["final"]["queen_length"]>0 for r in rs)}/{sum(r["final"]["queen_length"] for r in rs)/len(rs):.2f} |')
    lines += ['Q=여왕 길이, L=최장, T=총길이, E=전멸. 여왕 평균은 죽은 여왕 0 포함.',
              '| 짝 (회차+상대+지도) / 크기 | n | 둘 승/둘 패/B7만/MAIN만/무승부 포함 | 양측 sign p |', '|---|---:|---|---:|']
    groups = [('전체', pairs)] + [(f'회차 {n}',[p for p in pairs if p[0] == n]) for n in (1,2)] + [(op,[p for p in pairs if p[1]['opponent'] == op]) for op in opponents] + [(sz,[p for p in pairs if size(p[1]['cells']) == sz]) for sz in ('<=700','701-1200','>1200')]
    for name, ps in groups:
        co = Counter('draw' if 'draw' in (m['result'],b['result']) else 'bothwin' if m['result']==b['result']=='win' else 'bothloss' if m['result']==b['result']=='loss' else 'B7' if b['result']=='win' else 'MAIN' for _,m,b in ps)
        lines.append(f'| {name} | {len(ps)} | '+ '/'.join(str(co[k]) for k in ('bothwin','bothloss','B7','MAIN','draw'))+' | '+fmt(sign_test(co['B7'],co['MAIN']))+' |')
    q_pairs = paired(rows, 'B7Q')
    lines += ['B7Q–MAIN 짝: q1↔m2, q2↔m3 (각각 바로 뒤 실행).',
              '| B7Q–MAIN / 크기 | n | 둘 승/둘 패/B7Q만/MAIN만/무승부 포함 | 양측 sign p |', '|---|---:|---|---:|']
    groups_q = [('전체', q_pairs)] + [(f'q{n}↔m{n+1}', [p for p in q_pairs if p[0] == n]) for n in (1,2)] + [(op,[p for p in q_pairs if p[1]['opponent'] == op]) for op in opponents] + [(sz,[p for p in q_pairs if size(p[1]['cells']) == sz]) for sz in ('<=700','701-1200','>1200')]
    q_table_start = len(lines)
    for name, ps in groups_q:
        co = Counter('draw' if 'draw' in (m['result'],q['result']) else 'bothwin' if m['result']==q['result']=='win' else 'bothloss' if m['result']==q['result']=='loss' else 'B7Q' if q['result']=='win' else 'MAIN' for _,m,q in ps)
        lines.append(f'| {name} | {len(ps)} | '+ '/'.join(str(co[k]) for k in ('bothwin','bothloss','B7Q','MAIN','draw'))+' | '+fmt(sign_test(co['B7Q'],co['MAIN']))+' |')
    pack_table_rows(lines, q_table_start)
    pooled = defaultdict(lambda: defaultdict(list))
    for a in ('B7','B7Q'):
        for r in arms[a]:
            pooled[r['opponent_id'], r['map_id']][a].append(r)
    shared = [g for g in pooled.values() if g['B7'] and g['B7Q']]
    lines += ['B7Q–B7: 시간대가 다름. 모든 회차를 (상대, 지도)별 합산; 지도별 승률 비교(동률은 승률 0/1/혼합으로 구분), sign은 공유 지도 단위.',
              '| B7Q–B7 합산 / 크기 | 공유 지도 | B7Q 판/승 | B7 판/승 | Q만 우세/B만 우세/동률(0/1/혼합) | 양측 sign p |', '|---|---:|---:|---:|---|---:|']
    groups_b = [('전체', shared)] + [(op,[g for g in shared if g['B7Q'][0]['opponent'] == op]) for op in opponents] + [(sz,[g for g in shared if size(g['B7Q'][0]['cells']) == sz]) for sz in ('<=700','701-1200','>1200')]
    b_table_start = len(lines)
    for name, gs in groups_b:
        co = Counter()
        for g in gs:
            q, b = [ratio(sum(r['result']=='win' for r in g[a]),len(g[a])) for a in ('B7Q','B7')]
            co['Q' if q > b else 'B' if b > q else 'tie0' if q == 0 else 'tie1' if q == 1 else 'mixed'] += 1
        counts = [f'{sum(len(g[a]) for g in gs)}/{sum(r["result"]=="win" for g in gs for r in g[a])}' for a in ('B7Q','B7')]
        lines.append(f'| {name} | {len(gs)} | '+' | '.join(counts)+' | '+'/'.join(str(co[k]) for k in ('Q','B','tie0','tie1','mixed'))+' | '+fmt(sign_test(co['Q'],co['B']))+' |')
    pack_table_rows(lines, b_table_start)
    by_label = defaultdict(dict)
    for r in rows:
        by_label[r['label']][r['opponent_id'],r['map_id']] = r
    for baseline, labels in [('B7Q', ('agg8-q1',)), ('MAIN', ('agg7-m1','agg7-m2','agg7-m3'))]:
        ps = []
        for label in labels:
            base = by_label[label]
            for new_label in sorted(by_label):
                if not new_label.startswith('agg9-a'):
                    continue
                new = by_label[new_label]
                ps.extend((label,base[k],new[k]) for k in sorted(base.keys() & new.keys()))
        lines += [f'B10–{baseline} 짝 (시간대가 다름): (상대, 지도). '+('MAIN 합산은 회차별 짝을 합침(같은 B10 판은 회차마다 재사용).' if baseline == 'MAIN' else 'agg8-q1과 비교.'),
                  f'| B10–{baseline} / 크기 | n | 둘 승/둘 패/B10만/{baseline}만/무승부 포함 | 양측 sign p |', '|---|---:|---|---:|']
        groups = [('전체 (합산)',ps)] + [(label,[p for p in ps if p[0]==label]) for label in labels] + [(op,[p for p in ps if p[1]['opponent']==op]) for op in opponents] + [(sz,[p for p in ps if size(p[1]['cells'])==sz]) for sz in ('<=700','701-1200','>1200')]
        start = len(lines)
        for name, subset in groups:
            co = Counter('draw' if 'draw' in (b['result'],n['result']) else 'bothwin' if b['result']==n['result']=='win' else 'bothloss' if b['result']==n['result']=='loss' else 'B10' if n['result']=='win' else baseline for _,b,n in subset)
            lines.append(f'| {name} | {len(subset)} | '+'/'.join(str(co[k]) for k in ('bothwin','bothloss','B10',baseline,'draw'))+' | '+fmt(sign_test(co['B10'],co[baseline]))+' |')
        pack_table_rows(lines,start)
    lines += ['', '| 크기 | MAIN 판/승 | B7 판/승 | B7Q 판/승 | B10 판/승 |', '|---|---:|---:|---:|---:|']
    for sz in ('<=700','701-1200','>1200'):
        lines.append('| '+sz+' | '+' | '.join(f'{len(rs)}/{sum(r["result"]=="win" for r in rs)}' for rs in ([r for r in arms[a] if size(r['cells']) == sz] for a in ARMS))+' |')
    lines += ['여왕 (MAIN/B7/B7Q/B10): r100/150/300/종료는 라운드 끝(조기 종료는 최종 유지); 길이 평균은 생존 판만. 턴 비율은 0≤r≤300 차례 시작 길이, 합산 분모. 일상/탈출 분기는 기보에 없어 일상 분열은 NA; 자식 L2 분열은 일상 후보이며 탈출·대기도 포함. 개별 분열 직후 길이는 JSON queen_splits에 전부 보존.',
              '| 여왕 지표 | MAIN | B7 | B7Q | B10 |', '|---|---|---|---|---|']
    def queen_cell(rs, checkpoint):
        if not rs:
            return 'NA (0판)'
        lengths = []
        for r in rs:
            snaps = r['extra']['snaps']
            end = max(map(int, snaps))
            k = end if checkpoint == 'end' else min(checkpoint, end)
            st = snaps[k] if k in snaps else snaps[str(k)]
            lengths.append(st[0]['queen_length'])
        living = [L for L in lengths if L > 0]
        return f'{len(living)}/{len(rs)}; L{fmt(ratio(sum(living),len(living)))}'
    lines.append('| 생존 판/전체; 생존 평균 L (r100;150;300;종료) | '+' | '.join('<br>'.join(f'{k}: '+queen_cell(arms[a],k) for k in (100,150,300,'end')) for a in ARMS)+' |')
    lines.append('| 턴 L2/L3/L4+ (%) / 전체 여왕 턴 0-300 | '+' | '.join('/'.join(fmt(rate(arms[a],'queen_turns_L'+L,'queen_turns_0_300',100)) for L in ('2','3','4+'))+f' / {sum(r["extra"]["counts"].get("queen_turns_0_300",0) for r in arms[a])}' for a in ARMS)+' |')
    split_cells, death_cells, decided_cells, children_cells = [], [], [], []
    for a in ARMS:
        rs = arms[a]
        if not rs:
            for cells in (split_cells, death_cells, decided_cells, children_cells):
                cells.append('NA (0판)')
            continue
        splits = [sp for r in rs for sp in r['extra']['queen_splits']]
        candidate = [sp for sp in splits if sp['child_length'] == 2]
        post = Counter(sp['after_length'] for sp in splits)
        candidate_post = Counter(sp['after_length'] for sp in candidate)
        histogram = lambda co: ','.join(f'L{L}:{n}' for L,n in sorted(co.items())) or '없음'
        split_cells.append(f'일상 NA; L2자식 후보 {fmt(len(candidate)/len(rs))}/판 ({histogram(candidate_post)}); 전체 {fmt(len(splits)/len(rs))}/판 ({histogram(post)})')
        by_cause = defaultdict(Counter)
        for r in rs:
            d = r['extra']['queen_death']
            if d:
                by_cause[d['cause']][d['length']] += 1
        death_cells.append('; '.join(f'{cause} {sum(co.values())}건 ({histogram(co)})' for cause,co in sorted(by_cause.items())) or '0건')
        qgames = [r for r in rs if r['extra']['decided'] == 'queen_length']
        decided_cells.append(f'{len(qgames)}판 / {sum(r["result"]=="win" for r in qgames)}승 / {sum(r["result"]=="loss" for r in qgames)}패')
        children_cells.append(f'{len(splits)}명 / {fmt(len(splits)/len(rs))}명/판')
    lines.append('| 일상 분열/판; 직후 여왕 L:횟수 (전체 게임 창) | '+' | '.join(split_cells)+' |')
    lines.append('| 사망 원인별 건수 (사망 L:횟수) | '+' | '.join(death_cells)+' |')
    lines.append('| 여왕 길이 결정 판/승/패; 직접 분열 자식 수/판 (전체 게임 창) | '+' | '.join(f'{dec}; 자식 {child}' for dec,child in zip(decided_cells,children_cells))+' |')
    lines += ['', '## 2. 행동 (R=1위, O=우리 래더; * R에 가까워짐, ! 멀어짐)',
              '온라인은 합산 분자/분모; 체크포인트는 판 평균(조기 종료는 최종 상태 유지). 래더 R/O는 기존 동일 지도 가중 평균; 상대·시간대가 달라 인과 비교가 아니다.',
              'NA=자료/분모 없음. 기존 래더에 없는 작은 용 섭취·정확 타이머·순길이 지표의 R/O는 NA; 방향 표식도 생략. 체크포인트 R/O는 판 평균. 두 창 행의 세미콜론은 0-100;101-300 순서다.',
              f'생성 타이머 없는 온라인 기보 {sum(not r["timer_available"] for r in rows)}/{len(rows)}판: kind-2 사건이 없어 c1·c2 기회와 성공률 복원 불가(0건이 아님).',
              '| 지표 / 창 | R | O | MAIN | B7 | B7Q | B10 |', '|---|---:|---:|---:|---:|---:|---:|']
    marks, raw = reference_data()
    recount = {'R': json.loads((DOS/'target/recount.json').read_text()), 'O': json.loads((DOS/'work/fp_recount.json').read_text())['games']}
    intake_refs = []
    for arm in ('R','O'):
        layouts = defaultdict(list)
        for r in raw[arm]:
            layouts[r['layout_key']].append(recount[arm][str(r['game'])]['us']['game'])
        intake_refs.append(sum(1000*sum(c.get('eaten',0) for c in cs)/sum(c.get('turns',0) for c in cs) for cs in layouts.values())/len(layouts))
    def append_metric(name, window, vals, ref=None):
        rv, ov = ref if ref is not None else (marks.get((name,window),{}).get('rank1'), marks.get((name,window),{}).get('ours'))
        cells = []
        for v in vals:
            marker = ''
            if v is not None and rv is not None and vals[0] is not None and len(cells):
                delta = abs(vals[0]-rv)-abs(v-rv)
                marker = '*' if delta > 1e-12 else '!' if delta < -1e-12 else '='
            cells.append(fmt(v)+marker)
        lines.append(f'| {name} / {window} | {fmt(rv)} | {fmt(ov)} | '+' | '.join(cells)+' |')
    for n,d,name,scale,source in [('small_eaten','small_turns','L2-3 섭취 /1k turns',1000,'counts'),('on1','case1','c1 생성칸 밟음 %',100,'spawn'),('two_born','two_cases','c2 두 칸 밖에서 생성 %',100,'spawn'),('eaten','turns','전체 섭취 /1k turns',1000,'counts'),('natural_eaten','natural_born','자연 진주 섭취/생성',1,'counts'),('wait_sum','eaten','생성→섭취 대기',1,'counts'),('splits','turns','Split frequency',1000,'counts'),('headons','turns','Head-on meetings started',1000,'counts')]:
        append_metric(name, '0-300' if source=='spawn' else 'game', [rate(arms[a],n,d,scale,source) for a in ARMS], intake_refs if name=='전체 섭취 /1k turns' else None)
    for checkpoint, field in [(100,'alive'),(300,'alive'),(300,'longest'),('end','longest')]:
        def context(rs):
            return ratio(sum(r['extra']['counts'][f'{field}{checkpoint}' if field=='alive' else f'longest{checkpoint}' if checkpoint != 'end' else 'longest_end'] for r in rs),len(rs))
        refs = []
        for a in ('R','O'):
            values = [r['final_reconstructed'][field] if checkpoint=='end' or r['last_round']<checkpoint else r['ranges']['0-100' if checkpoint==100 else '101-300']['end_state'][field] for r in raw[a]]
            refs.append(sum(values)/len(values))
        append_metric(field,str(checkpoint),[context(arms[a]) for a in ARMS],refs)
    append_metric('순길이 (섭취−사망 길이) /1k turns','game',[rate(arms[a],'eaten','turns',1000)-rate(arms[a],'lost','turns',1000) if arms[a] else None for a in ARMS])
    for name in ('Natural birth-cohort harvest','Birth-cohort wait until eaten','Split frequency','Head-on meetings started') + tuple('Death: '+c for c in ('head-on mover','head-on hit','wall','own body','another body','no action','unpaid sprint','illegal split','timeout')):
        for window in ('0-100','101-300'):
            append_metric(name,window,[sb.pool(arms[a],sb.metric_key(name,window)) for a in ARMS])
        second, first = lines.pop(), lines.pop()
        cells1, cells2 = first.split('|'), second.split('|')
        lines.append('| '+name+' / 0-100;101-300 | '+' | '.join(cells1[i].strip()+';'+cells2[i].strip() for i in range(2, 4+len(ARMS)))+' |')
    lines += ['', '## 3. 스위치 관련 사건',
              '아래는 브리프의 관측 조건에 맞는 사건이며 독점 발동 증명은 아니다: MAIN도 만들 수 있고 로그에 스위치 실행 표식이 없다. 두 포털 스위치는 같은 사건으로 분리 불가.',
              '| 스위치 | MAIN | B7 | B7Q | B10 |', '|---|---|---|---|---|']
    def count_event(a,key):
        rs = arms[a]
        if not rs:
            return 'NA (0판)'
        n = sum(r['extra']['counts'].get(key,0) for r in rs)
        return str(n)+(' (10건 미만: 읽기 작음)' if n < 10 else '')
    lines.append('| SPAWN_CLEAR c1 on/case; c2 born/case | '+' | '.join('NA (0판)' if not arms[a] else 'NA (타이머 없음)' if not any(r['timer_available'] for r in arms[a]) else '; '.join(f'{sum(r["spawn"].get(n,0) for r in arms[a] if r['timer_available'])}/{sum(r["spawn"].get(d,0) for r in arms[a] if r['timer_available'])}' for n,d in [('on1','case1'),('two_born','two_cases')]) for a in ARMS)+' |')
    for switch,key in [('ZONE_NEARER','zone_nearer'),('TRADE_EVEN','trade_even'),('HUNT_SMALL_RATIO','hunt_small'),('POCKET_LOOP','room100'),('HARVEST_PORTAL','room100')]:
        lines.append(f'| {switch} | '+' | '.join(count_event(a,key) for a in ARMS)+' |')
    for name, keys in [('TRADE_SHORT_BY (L3/L4/L5+; 동길이/2+ 짧음)', ('trade_short_L3','trade_short_L4','trade_short_L5plus','trade_equal','trade_short_2plus')),
                       ('LUNGE_PEARL / 전체 paid-sprint hits', ('lunge_pearl','paid_sprint_hits')),
                       ('FEEDER_EAT', ('feeder_eat',))]:
        lines.append('| '+name+' | '+' | '.join('/'.join(count_event(a,k) for k in keys) for a in ARMS)+' |')
    lines.append('| QS_KEEP_LEN 3 (자식 L2·직후 Q<3; 일상/탈출 미분리) | '+' | '.join('NA (0판)' if not arms[a] else str(sum(sp['child_length']==2 and sp['after_length']<3 for r in arms[a] for sp in r['extra']['queen_splits'])) for a in ARMS)+' |')
    lines.append('| LEADER_FULL_UNITS (>1200, L>10 & 수<56 첫 r) | '+' | '.join('; '.join(f'{r["game"]}:r{r["extra"]["first10"]}' for r in arms[a] if r['extra']['first10'] is not None) or '0건 (읽기 작음)' if arms[a] else 'NA (0판)' for a in ARMS)+' |')
    lines += ['TRADE_SHORT_BY: 비여왕 아군이 시작한 적 머리 충돌; 충돌 시 우리 길이 3/4/5+에서 적이 정확히 1 짧음, 같은 모집단의 동길이/2 이상 짧음도 집계.',
              'LUNGE_PEARL: 적 머리 충돌 걸음이 시작 길이 ceil(L/4)를 넘고, 그 차례의 유료 이동 걸음에서 진주를 먹은 충돌/전체 유료 충돌(여왕 포함).',
              'FEEDER_EAT: 섭취 차례 시작에 비여왕·최장보다 짧은 아군이 사망 전 0–3라운드에 먹은 진주 중, 그 사망 낙하 진주가 사망 후 0–3라운드에 차례 시작 최장 아군에게 먹힌 경우를 1회씩 집계; 내부 feed_index·흡수 의도는 복원 불가.',
              'ZONE 거리=시작 머리와 진주의 토러스 맨해튼; 최장 동률은 최소 id. 리더 r=작은 지도 300, 큰 지도 150. TRADE 길이는 충돌 시점, 수는 차례 시작·실제 UNIT_LIMIT 기준.',
              '', '## 4. 패배 해부 (MAIN/B7/B7Q/B10 분리; OLD는 상세 JSON에 보존)',
              '항목: game 지도; 결정; Q 사망 r/원인/L/아군5; 충돌 상대 id:L(시작 L), 차례 시작 머리→충돌 칸 최단 열린 변·포털 거리 d/실제 걸음 k; 영구 역전 r(라운드 끝); r300 이후 최장 피격 r:L.',
              '| arm / 상대 | 각 패배 (상대별, 판마다 줄바꿈) |', '|---|---|']
    classes = defaultdict(Counter)
    for arm in ARMS:
        for opponent in opponents:
            losses = [r for r in arms[arm] if r['opponent']==opponent and r['result']=='loss']
            entries = []
            for r in losses:
                ex = r['extra']; d = ex['queen_death']
                q = '생존' if d is None else f'r{d["round"]}/{d["cause"]}/L{d["length"]}/a{d["allies5"]}'
                if d and d['other']:
                    o=d['other']; q += f' ←#{o["id"]}:L{o["length"]}(시작{o.get("start_length",o["length"])}),d{o["distance"]}/k{o["steps"]}'
                entries.append(f'{r["game"]} {r["map"]}; {ex["decided"]}; Q {q}; {ex["quantity"]}↑{ex["passed"]}; late {ex["late_rams"] or "없음"}')
                categories = []
                if d:
                    categories.append('queen <100' if d['round']<100 else 'queen 100-300' if d['round']<=300 else 'queen >300')
                if r['final']['alive']==0:
                    categories.append('eliminated')
                if ex['late_rams']:
                    categories.append('leader rammed late')
                if r['final']['queen_length']==r['their']['queen_length']==0 and r['final']['alive']>0 and r['their']['alive']>0:
                    categories.append('out-eaten both queens dead')
                classes[arm,opponent].update(categories or ['other'])
            if entries:
                lines.append(f'| {arm} / {opponent} | '+'<br>'.join(entries)+' |')
    lines += ['', '| arm / 상대 | Q<100 / Q100-300 / Q>300 / 늦은 최장 피격 / 두 Q 사망·out-eaten / 전멸 / 기타 |', '|---|---|']
    names = ('queen <100','queen 100-300','queen >300','leader rammed late','out-eaten both queens dead','eliminated','other')
    loss_classes_start = len(lines)
    for arm in ARMS:
        for opponent in opponents:
            co=classes[arm,opponent]
            lines.append(f'| {arm} / {opponent} | '+ '/'.join(str(co[k]) for k in names)+' |')
    lines += ['클래스는 겹칠 수 있다(예: Q 사망과 전멸). out-eaten은 두 Q 사망·양팀 생존 상태의 패배이며 섭취 인과 증명은 아니다. 기타는 앞 조건 모두 없음.', '', '## 5. 관측 요약 (조언 없음)',
              f'MAIN {len(arms["MAIN"])}판 {sum(r["result"]=="win" for r in arms["MAIN"])}승; B7 {len(arms["B7"])}판 {sum(r["result"]=="win" for r in arms["B7"])}승; 짝 {len(pairs)}판.',
              f'B7Q {len(arms["B7Q"])}판 {sum(r["result"]=="win" for r in arms["B7Q"])}승; MAIN 짝 {len(q_pairs)}판; B7 공유 지도 {len(shared)}개.',
              f'B10 {len(arms["B10"])}판 {sum(r["result"]=="win" for r in arms["B10"])}승.',
              f'별도 시간대 sr51-bob1 {len(arms["OLD"])}판 {sum(r["result"]=="win" for r in arms["OLD"])}승.',
              'MAIN 최대 패배 클래스: '+', '.join(f'{k} {v}건' for k,v in sum((classes['MAIN',op] for op in opponents),Counter()).most_common(3))+'.',
              'B7 미도착: 묶음 차이 관측 0쌍.' if not arms['B7'] else f'B7 관련 사건: even {sum(r["extra"]["counts"].get("trade_even",0) for r in arms["B7"])}건, small hunt {sum(r["extra"]["counts"].get("hunt_small",0) for r in arms["B7"])}건.',
              f'재실행: `{COMMAND}`. 상세 분자/분모·모든 판: `agg7-games.json`; 검증: `agg7-validation.json`.']

    if sum(bool(line) for line in lines) + 2*sum(line.startswith('#') for line in lines) + 2 > 160:
        stop = loss_classes_start + len(ARMS)*len(opponents)
        packed = lines[loss_classes_start:stop]
        if packed:
            cells = [line.split('|')[1:-1] for line in packed]
            lines[loss_classes_start:stop] = ['| '+' | '.join('<br>'.join(row[i].strip() for row in cells) for i in range(2))+' |']

    separated = []
    for index,line in enumerate(lines):
        if not line:
            if separated and separated[-1].startswith('|') and index+1 < len(lines) and lines[index+1].startswith('|'):
                separated.append('')
            continue
        if separated and (line.startswith('#') or separated[-1].startswith('#')):
            separated.append('')
        separated.append(line)
    assert len(separated)<=160, ('report too long',len(separated))
    return '\n'.join(separated)+'\n'


def validate_logs(rows, found):
    checks=[]
    for label in found:
        rs=[r for r in rows if r['label']==label]
        path=SMOKE/(label+'-report.log')
        if not path.exists():
            checks.append(dict(label=label,status='pending report log'))
            continue
        text=path.read_text()
        checks_by_op={}
        for raw_line in text.splitlines(keepends=True):
            line = raw_line.rstrip('\r\n')
            if label.startswith('agg9-a') and not raw_line.endswith(('\n','\r')) and re.search(r'wins new \d+/\d+$',line):
                continue
            m=re.match(r'vs (.*?): wins new (\d+)/(\d+)',line)
            if not m:
                m=re.match(r'no live baseline yet vs (.*?): new (\d+)/(\d+) wins',line)
            if m:
                op,w,n=m[1],int(m[2]),int(m[3])
                subset=[r for r in rs if r['opponent']==op]
                if len(subset)<n:
                    checks_by_op[op]=dict(games=len(subset),wins=sum(r['result']=='win' for r in subset),expected_games=n,expected_wins=w,pending=True)
                    continue
                assert (len(subset),sum(r['result']=='win' for r in subset))==(n,w),(label,op,'log mismatch')
                checks_by_op[op]=dict(games=n,wins=w)
        absent = {r['opponent'] for r in rs} - set(checks_by_op)
        if label.startswith('agg9-a'):
            for op in absent:
                checks_by_op[op] = dict(pending=True, reason='pending report line')
        else:
            assert not absent, (label,'opponent missing from log')
        checks.append(dict(label=label,status='pending downloads' if any(v.get('pending') for v in checks_by_op.values()) else 'passed',opponents=checks_by_op))
    return checks


def main():
    found, missing, jobs, notes=inventory()
    counter=sb.load_counter()
    cache_path=HERE/'agg7-cache.json'
    dependencies=[DOS/'count_dossier.py',DOS/'local/scoreboard.py',DOS/'local/spawn.py',DOS/'local/replay_format.py',DOS/'local/count_local.py',DOS/'work/fp_build.py',ROOT/'tools/ladder_replay.py',DOS.parent/'losses/counts/count_replays.py']
    tree=ast.parse(Path(__file__).read_text())
    scan_source=''.join(ast.dump(n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('supplement','count_job'))
    version=hashlib.sha256(scan_source.encode()+b''.join(p.read_bytes() for p in dependencies)).hexdigest()
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    legacy_version = '8f0d28eda426b34dabd86f30a2e3f44c66d08b72d8c712015a854527030a7c95'
    legacy_dependencies = '1eaa74a668e2bcb566268f98650e2eb6a1d18659c45a658bbbd83de7b098644e'
    migrate = hashlib.sha256(b''.join(p.read_bytes() for p in dependencies)).hexdigest() == legacy_dependencies
    rows=[]
    reused = refreshed = parsed = 0
    for i,(label,path,meta) in enumerate(jobs,1):
        signature=[version,hashlib.sha256(path.read_bytes()).hexdigest(),hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest()]
        key=str(path)
        if key in cache and cache[key]['signature']==signature:
            row=cache[key]['row']
            reused += 1
        else:
            st=path.stat()
            if label.startswith('agg9-a'):
                try:
                    sb.load_replay(path).root().pointer(4).u16(2)
                except (ValueError, IndexError, OSError, EOFError, struct.error, AttributeError, subprocess.CalledProcessError):
                    notes.append(f'{label}: pending replay game {meta["id"]}')
                    continue
            old = cache.get(key)
            if migrate and old and old['signature'] == [legacy_version, *signature[1:]]:
                root = sb.load_replay(path).root()
                text = root.text(0)
                w,h = map(int,text.splitlines()[0].split()[1:3])
                edges = [tuple(map(int,q[1:4])) for q in map(str.split,text.splitlines()) if q and q[0]=='EDGE']
                extra = supplement(root,meta,counter.Geo(w,h,edges))
                previous_extra = old['row']['extra']
                normalized = json.loads(json.dumps(extra))
                assert all(normalized[k] == v for k,v in previous_extra.items() if k != 'counts'), (meta['id'],'legacy supplement mismatch')
                assert all(extra['counts'].get(k,0) == v for k,v in previous_extra['counts'].items()), (meta['id'],'legacy count mismatch')
                row = dict(old['row'], extra=extra)
                refreshed += 1
            else:
                row=count_job(label,path,meta,counter)
                parsed += 1
            assert (st.st_size,st.st_mtime_ns)==(path.stat().st_size,path.stat().st_mtime_ns),'input changed; rerun'
            cache[key]=dict(signature=signature,row=row)
            cache_path.write_text(json.dumps(cache,ensure_ascii=False)+'\n')
        rows.append(row)
        print(f'{i}/{len(jobs)} {label} {meta["id"]} {row["result"]}',flush=True)
    assert len(rows)==len({r['game'] for r in rows})
    for row in rows:
        ex = row['extra']
        end = ex['snaps'][max(ex['snaps'], key=int)][0]
        assert end['queen_length'] == row['final']['queen_length'], (row['game'], 'queen final mismatch')
        counts = ex['counts']
        assert sum(counts.get('queen_turns_L'+L,0) for L in ('2','3','4+')) == counts.get('queen_turns_0_300',0), (row['game'], 'queen turns mismatch')
        splits = ex['queen_splits']
        assert len(splits) == len({sp['child'] for sp in splits}), (row['game'], 'duplicate queen child')
        assert all(sp['before_length'] == sp['after_length']+sp['child_length'] for sp in splits), (row['game'], 'queen split length mismatch')
    checks=validate_logs(rows,found)
    validation=dict(found=found,missing=missing,notes=notes,games=len(rows),unique_games=len(rows),logs=checks,cache=dict(reused=reused,refreshed=refreshed,parsed=parsed),arms={a:dict(games=sum(r['arm']==a for r in rows),wins=sum(r['arm']==a and r['result']=='win' for r in rows)) for a in ARMS})
    output=report(rows,found,missing,notes,'; '.join(c['label']+':'+c['status'] for c in checks))
    (HERE/'agg7-games.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
    (HERE/'agg7-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    (HERE/'agg7.md').write_text(output)
    print(f'Validated {len(rows)} games; report {len(output.splitlines())} lines',flush=True)



if __name__=='__main__':
    main()
