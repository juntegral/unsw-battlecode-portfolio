#!/usr/bin/env python3
"""Offline, replay-only counts for the three sets in brief-long30.md."""
import sys
sys.dont_write_bytecode = True
from collections import Counter, deque
from functools import lru_cache
from statistics import mean

import label_report as reader

HERE = reader.HERE
SETS = ('c5455-w1-new', 'one2-w1-old', 'one1-w1-old')
SIDES = ('우리', '상대')
CAUSES = ('kelp', '자기 몸', '다른 몸', '머리 충돌', '유효 행동 없음')


def scan(path, meta):
    root = reader.agg.sb.load_replay(path).root()
    result = root.pointer(4)
    assert result is not None and result.bit(0), ('미완결 기보', path)
    bodies, teams, records, edges = {}, {}, {}, []
    w = h = 0
    own = int(meta['teamAId'] != 1119)
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'EDGE':
            edges.append(tuple(map(int, q[1:4])))
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(int(q[1]) != own)
            records[i] = dict(peak=len(bodies[i]), side=teams[i], death=None)
    geo = reader.agg.spawn.Geo(w, h, edges)
    queens = [min(i for i in bodies if teams[i] == s) for s in (0, 1)]
    counts = [Counter(), Counter()]
    rnd, actor, turn, action_detail = -1, None, None, None
    tile = lambda p: reader.agg.sb.replay_format.point(p)[1]*w+reader.agg.sb.replay_format.point(p)[0]

    @lru_cache(maxsize=None)
    def near3(src):
        seen, queue = {src: 0}, deque([src])
        while queue:
            c = queue.popleft()
            if seen[c] == 3:
                continue
            for dest in geo.adj[c]:
                if dest not in seen:
                    seen[dest] = seen[c]+1
                    queue.append(dest)
        return seen

    def peak(i):
        records[i]['peak'] = max(records[i]['peak'], len(bodies[i]))

    def close_turn():
        nonlocal turn
        if turn is None or not turn['threats']:
            turn = None
            return
        c = counts[teams[turn['id']]]
        c['threat'] += 1
        if turn['split']:
            category = 'split'
        elif turn['paid']:
            category = 'paid'
        elif turn['id'] not in bodies:
            category = 'dead'
        else:
            ball = near3(bodies[turn['id']][0])
            category = 'within' if any(hd in ball for hd in turn['threats']) else 'away'
        c[category] += 1
        turn = None

    for index, ev in enumerate(root.pointer(3)):
        kind = ev.u16(0)
        if kind not in (0, 1, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kind == 0:
            close_turn()
            rnd, actor = p.i32(0), None
        elif kind == 1:
            close_turn()
            actor, action_detail = p.i32(0), None
            assert actor in bodies
            length, hd = len(bodies[actor]), bodies[actor][0]
            long = length >= 30
            counts[teams[actor]]['turns'] += int(long)
            ball = near3(hd) if long else {}
            threats = [b[0] for i, b in bodies.items()
                       if teams[i] != teams[actor] and 2 <= len(b) <= 4 and b[0] in ball]
            turn = dict(id=actor, length=length, steps=0, split=False, paid=False, threats=threats)
        elif kind == 4:
            a, fuel = p.pointer(0), p.pointer(1)
            action_detail = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                             ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)]
                             if a is not None and a.u16(0) < 3 else 'no action')
        elif kind == 9:
            i = p.i32(0)
            b, hd, tail = bodies[i], tile(p.pointer(0)), tile(p.pointer(1))
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    assert turn is not None
                    turn['steps'] += 1
                    turn['paid'] |= turn['steps'] > (turn['length']+3)//4
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
            peak(i)
        elif kind == 10:
            parent, child = p.i32(0), p.i32(4)
            assert parent == actor and child not in records
            turn['split'] = True
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
                teams[i] = int(p.u16(8) != own)
                if i == child:
                    records[i] = dict(peak=len(bodies[i]), side=teams[i], death=None)
                peak(i)
        elif kind == 11:
            i, reason = p.i32(0), p.u16(4)
            length = len(bodies[i])
            cause = CAUSES[reason]
            if length < 30:
                category = 'below'
            elif reason == 3 and i != actor and teams[i] != teams[actor]:
                category = 'rammed'
            elif i == actor:
                category = 'own_head' if reason == 3 else 'own'
            else:
                category = 'other'
            other = actor if reason == 3 and i != actor else None
            detail = action_detail if reason == 4 else None
            records[i]['death'] = dict(game=meta['id'], id=i, round=rnd, event=index,
                                       length=length, cause=cause, category=category,
                                       actor=actor, other=other, detail=detail)
            bodies.pop(i)
    close_turn()
    for s in (0, 1):
        expected = result.pointer(own if s == 0 else 1-own)
        actual = (sum(teams[i] == s for i in bodies),
                  max((len(b) for i, b in bodies.items() if teams[i] == s), default=0),
                  sum(len(b) for i, b in bodies.items() if teams[i] == s),
                  len(bodies.get(queens[s], ())))
        assert actual == tuple(expected.i32(o) for o in (0, 4, 8, 12)), (meta['id'], s, actual)
        c = counts[s]
        assert c['threat'] == sum(c[k] for k in ('away', 'within', 'paid', 'split', 'dead'))
    return records, counts


def collect(folder):
    inv = reader.directory_inventory(folder, str(reader.SMOKE/folder))
    assert not inv['notes'] and len(inv['jobs']) == 15, inv['notes']
    totals = [Counter(), Counter()]
    peaks, deaths, games = [[], []], [[], []], [set(), set()]
    for path, meta in inv['jobs']:
        records, counts = scan(path, meta)
        for s in (0, 1):
            totals[s].update(counts[s])
        for record in records.values():
            if record['peak'] < 30:
                continue
            s, d = record['side'], record['death']
            peaks[s].append(record['peak'])
            games[s].add(meta['id'])
            totals[s]['alive' if d is None else d['category']] += 1
            if d is not None and d['length'] >= 30:
                deaths[s].append(d)
                totals[s]['cause:'+d['cause']] += 1
        print(f'{folder}: {meta["id"]}', flush=True)
    for s in (0, 1):
        assert len(peaks[s]) == sum(totals[s][k] for k in ('alive', 'below', 'rammed', 'own', 'own_head', 'other'))
    return dict(counts=totals, peaks=peaks, deaths=deaths, games=games)


def report(sets):
    lines = ['# 길이 30 이상 드래곤: 온라인 기보 기계 집계', '',
             '우리 팀 1119. 각 열 15판이며 각 경기의 드래곤 id를 한 번만 센다. 수치는 지정된 45개 기보에서만 계산했다.', '',
             '| 항목 / 진영 | c5455-w1-new | one2-w1-old | one1-w1-old |',
             '|---|---:|---:|---:|']
    metrics = [
        ('30+ 도달 드래곤', lambda r, s: len(r['peaks'][s])),
        ('30+ 도달 경기', lambda r, s: len(r['games'][s])),
        ('도달 드래곤의 최대 길이 평균', lambda r, s: f'{mean(r["peaks"][s]):.3f}' if r['peaks'][s] else 'NA'),
        ('종료 생존', lambda r, s: r['counts'][s]['alive']),
        ('30+ 적 머리 피격 사망 (상대 이동)', lambda r, s: r['counts'][s]['rammed']),
        ('30+ 자기 차례 사망: kelp / 자기 몸 / 다른 몸 / 유효 행동 없음',
         lambda r, s: ' / '.join(str(sum(d['category'] == 'own' and d['cause'] == cause for d in r['deaths'][s]))
                                for cause in (CAUSES[0], CAUSES[1], CAUSES[2], CAUSES[4]))),
        ('30+ 자기 차례 머리 충돌 사망', lambda r, s: r['counts'][s]['own_head']),
        ('30 미만으로 줄어든 뒤 사망', lambda r, s: r['counts'][s]['below']),
        ('30+ 기타 타자 차례 사망', lambda r, s: r['counts'][s]['other']),
        ('30+ 드래곤 차례', lambda r, s: r['counts'][s]['turns']),
        ('피격 사망 / 30+ 차례 1,000회', lambda r, s: f'{1000*r["counts"][s]["rammed"]/r["counts"][s]["turns"]:.3f}' if r['counts'][s]['turns'] else 'NA'),
        ('30+ 시작, 적 L2–4 머리 3걸음 이내 차례', lambda r, s: r['counts'][s]['threat']),
        ('위 조건: 3걸음 밖으로 이동', lambda r, s: r['counts'][s]['away']),
        ('위 조건: 3걸음 안에 남음', lambda r, s: r['counts'][s]['within']),
        ('위 조건: 유료 sprint', lambda r, s: r['counts'][s]['paid']),
        ('위 조건: 분열', lambda r, s: r['counts'][s]['split']),
        ('위 조건: 유료 걸음 없이 자기 차례 사망', lambda r, s: r['counts'][s]['dead']),
    ]
    for title, fn in metrics:
        for s, side in enumerate(SIDES):
            lines.append(f'| {title} / {side} | '+' | '.join(str(fn(r, s)) for r in sets)+' |')
    lines += ['', '우리의 30+ 사망 전수 목록 (경기 id, r은 기보의 0부터 시작하는 라운드, #는 드래곤 id):', '']
    for name, r in zip(SETS, sets):
        lines.append(f'- **{name}**:')
        if not r['deaths'][0]:
            lines.append('  - 없음.')
        for d in sorted(r['deaths'][0], key=lambda d: (d['game'], d['event'])):
            kind = {'rammed': '적 머리 피격', 'own': '자기 차례', 'own_head': '자기 차례 머리 충돌', 'other': '타자 차례 기타'}[d['category']]
            detail = f'; {d["detail"]}' if d['detail'] else ''
            other = f'; 이동한 적 #{d["other"]}' if d['category'] == 'rammed' else ''
            lines.append(f'  - {d["game"]}, r{d["round"]}, #{d["id"]}, L{d["length"]}: {kind}, {d["cause"]}{other}{detail}.')
    lines += ['', '상대의 30+ 사망 전수 목록:', '']
    for name, r in zip(SETS, sets):
        items = []
        for d in sorted(r['deaths'][1], key=lambda d: (d['game'], d['event'])):
            kind = {'rammed': '피격', 'own': '자기 차례', 'own_head': '자기 차례 머리 충돌', 'other': '타자 차례 기타'}[d['category']]
            items.append(f'{d["game"]}:r{d["round"]} #{d["id"]} L{d["length"]} {kind}({d["cause"]})')
        lines.append(f'- **{name}**: '+('; '.join(items) or '없음')+'.')
    lines += ['',
              '집계 정의: 최대 길이·사망 길이는 초기 몸과 기보의 몸 갱신/분열/사망 사건으로 복원한다. 분열한 자식은 새 id이며 부모의 최대 길이를 물려받지 않는다. 종료 생존에는 최종 길이 30 미만도 포함한다. 30+ 차례는 차례 시작 길이 30 이상인 실제 차례만 센다. 사망 분류는 사망 직전 길이로 결정한다.', '',
              '근접 조건은 차례 시작에 적 길이 2–4 머리가 열린 변·포털 최단거리 3 이내에 있는 경우다(몸 무시, 적 여왕 포함). 각 차례를 분열 → 실제 유료 걸음 수행 → 사망 → 거리 순서로 한 범주에만 넣는다. 유료는 시작 길이 L에 고정된 무료 ceil(L/4) 걸음을 넘는 성공한 걸음이며, 실패한 유료 이동 요청만으로는 세지 않는다. 밖으로 이동/안에 남음은 생존한 비분열·비유료 차례 끝 머리에서 시작 때 근접했던 적 머리 위치까지의 거리 >3/≤3이다. 차례 중 새로 접근한 적은 거리 판정에 추가하지 않는다.', '',
              '점검: 세 폴더 모두 누락·중복 없이 15판, 45개 고유 경기. 모든 경기의 복원 최종 생존 수·최장·총길이·여왕 길이가 기보 결과와 양쪽 모두 일치한다. 도달 드래곤의 종료 분류 합과 근접 차례의 행동 분류 합을 각각 대조했다. 기존 `agg7_report.supplement`의 사망 사건과 45판 양쪽의 30+ 사망 id·라운드·길이를 대조해 모두 일치했다. 전략 효과나 승패에 대한 판정은 하지 않는다.', '',
              '리더: `label_report.agg.sb.load_replay`; 입력 목록: `label_report.directory_inventory`. 재실행: `nice -n 10 python3 -B data/analysis/ladder/dossier/online/long30.py`.']
    return '\n'.join(lines)+'\n'


def main():
    ids = [meta['id'] for name in SETS
           for _, meta in reader.directory_inventory(name, str(reader.SMOKE/name))['jobs']]
    assert len(ids) == len(set(ids)) == 45
    sets = [collect(name) for name in SETS]
    (HERE/'long30.md').write_text(report(sets))
    print('작성 완료: '+str(HERE/'long30.md'))


if __name__ == '__main__':
    main()
