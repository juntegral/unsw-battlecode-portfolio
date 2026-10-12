#!/usr/bin/env python3
"""Offline replay timelines. Run from any directory: python3 -B tools/top_metrics.py.

Four processes; immutable input snapshot per invocation; stat/version-keyed game cache.
See data/analysis/top1/methodology.md for metric definitions and missing-value rules.
"""
import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
import csv

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/analysis/top1'
PARSER = ROOT.parent / 'battlecode/replay.py'
VERSION = 1
BUCKETS = (25, 50, 100, 150, 200, 250, 300, 350, 400, 450)
CLASSES = ('le4', '5_9', '10plus')
CAUSES = ('wall', 'self', 'body', 'headon', 'other')
STATE = ('units', 'total_length', 'longest_length', 'cells_visited', 'queen_alive',
         'queen_length', 'queen_start_distance', 'queen_teammates_within6',
         'queen_nearest_enemy_distance')
COUNTS = ('pearls_natural', 'pearls_corpse', 'pearls_unknown', 'length_gained',
          'suicides', 'feeding_near_longest', 'portal_crossings', 'sonar_messages',
          'sonar_nonzero_messages') + tuple(
    f'{metric}_{c}' for metric in ('splits', 'deaths', 'headon_initiated', 'sprints', 'sprint_steps')
    for c in CLASSES) + tuple(f'deaths_{cause}' for cause in CAUSES) + tuple(
    f'deaths_{cause}_{c}' for cause in CAUSES for c in CLASSES)
MEANS = tuple(f'sprint_mean_steps_{c}' for c in CLASSES)
METRICS = STATE + COUNTS + MEANS


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    tmp.write_text(text, encoding='utf-8')
    tmp.replace(path)


def length_class(n):
    return 'le4' if n <= 4 else '5_9' if n <= 9 else '10plus'


def size_class(cells):
    return 'small<=700' if cells <= 700 else 'medium701-1500' if cells <= 1500 else 'large>1500'


def distance(a, b, w, h):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, w - dx) + min(dy, h - dy)


def load_parser():
    sys.path.insert(0, str(PARSER.parent))
    return importlib.import_module('replay')


def geometry(text):
    bodies, teams, portals = {}, {}, set()
    w = h = None
    name = '?'
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'MAP':
            w, h = map(int, p[1:3])
        elif p[0] == 'MAP_NAME':
            name = ' '.join(p[1:])
        elif p[0] == 'DRAGON':
            did = len(bodies)
            teams[did] = 'AB'[int(p[1])]
            bodies[did] = deque((int(p[3 + 2*k]), int(p[4 + 2*k])) for k in range(int(p[2])))
        elif p[0] == 'EDGE' and int(p[2]) == 2:
            row, x = divmod(int(p[1]), w + 1)
            portals.add((x % w, (row // 2) % h, 0 if row % 2 == 0 else 3))
    if not w or not h or not bodies:
        raise ValueError('missing map dimensions or starting dragons')
    return w, h, name, bodies, teams, portals


def extract(task):
    started = time.perf_counter()
    rp = load_parser()
    root = rp.load(task['replay_path']).root()
    w, h, name, bodies, teams, portals = geometry(root.text(0))
    queens = {side: next((d for d in (0, 1) if teams.get(d) == side), None) for side in 'AB'}
    if any(q is None for q in queens.values()):
        raise ValueError('queen ids 0/1 do not map to both teams')
    starts = {s: bodies[q][0] for s, q in queens.items()}
    visited = {s: {b[0] for d, b in bodies.items() if teams[d] == s} for s in 'AB'}
    counts = {s: Counter() for s in 'AB'}
    timeline, checks = [], Counter()
    pearls = {}
    drop = False
    current = None
    action = None
    directions = deque()
    headon_counted = False
    rnd, boundary, previous = -1, 0, 0

    def snapshot(bucket, end):
        nonlocal previous
        for side in 'AB':
            mine = {d: b for d, b in bodies.items() if teams[d] == side}
            qb = bodies.get(queens[side])
            enemy = [b for d, b in bodies.items() if teams[d] != side]
            row = dict(game_id=task['game_id'], team_id=task['meta']['team'+side+'Id'],
                       side=side, bucket=str(bucket), round_start=previous, round_end=end,
                       bucket_rounds=end-previous, units=len(mine),
                       total_length=sum(map(len, mine.values())),
                       longest_length=max(map(len, mine.values()), default=0),
                       cells_visited=len(visited[side]), queen_alive=int(bool(qb)),
                       queen_length=len(qb) if qb else 0,
                       queen_start_distance=distance(qb[0], starts[side], w, h) if qb else None,
                       queen_teammates_within6=sum(distance(qb[0], b[0], w, h) <= 6
                           for d, b in mine.items() if d != queens[side]) if qb else None,
                       queen_nearest_enemy_distance=min((distance(qb[0], b[0], w, h)
                           for b in enemy), default=None) if qb else None)
            row.update({m: counts[side][m] for m in COUNTS})
            for c in CLASSES:
                n = counts[side]['sprints_'+c]
                row['sprint_mean_steps_'+c] = counts[side]['sprint_steps_'+c] / n if n else None
            timeline.append(row)
            counts[side].clear()
        previous = end

    for event in root.pointer(3):
        kind = event.u16(0)
        p = event.pointer(0)
        is_drop = kind == 3 and p.bit(0)
        if not is_drop:
            drop = False
        if kind == 0:
            rnd = p.i32(0)
            while boundary < len(BUCKETS) and rnd >= BUCKETS[boundary]:
                snapshot(BUCKETS[boundary], BUCKETS[boundary])
                boundary += 1
        elif kind == 1:
            current = p.i32(0)
            action = None
            directions.clear()
            headon_counted = False
        elif kind == 3:
            cell = rp.point(p.pointer(0))
            if p.bit(0):
                pearls[cell] = 'corpse' if drop else 'natural'
            else:
                origin = pearls.pop(cell, 'unknown')
                if current in teams and rnd >= 0:
                    counts[teams[current]]['pearls_'+origin] += 1
                else:
                    checks['unattributed_pearl_removals'] += 1
        elif kind == 4:
            did = p.i32(0)
            a = p.pointer(0)
            current = did
            action = a.u16(0) if a is not None else None
            headon_counted = False
            directions.clear()
            if did not in bodies:
                checks['action_without_body'] += 1
                continue
            side, body = teams[did], bodies[did]
            c = length_class(len(body))
            if action == 0:
                steps = a.pointer(0)
                directions.extend(steps if steps is not None else [])
                if len(directions) >= 2:
                    counts[side]['sprints_'+c] += 1
                    counts[side]['sprint_steps_'+c] += len(directions)
            elif action == 2:
                counts[side]['suicides'] += 1
                lead = min((d for d in bodies if teams[d] == side), key=lambda d: (-len(bodies[d]), d))
                if lead != did and distance(body[0], bodies[lead][0], w, h) <= 6:
                    counts[side]['feeding_near_longest'] += 1
        elif kind == 9:
            did = p.i32(0)
            head, tail = rp.point(p.pointer(0)), rp.point(p.pointer(1))
            if did not in bodies:
                raise ValueError(f'update for unknown dragon {did}')
            body, side = bodies[did], teams[did]
            before = len(body)
            if did == current and directions:
                direction = directions.popleft()
                x, y = body[0]
                if direction == 1:
                    x, direction = (x+1) % w, 3
                elif direction == 2:
                    y, direction = (y+1) % h, 0
                if (x, y, direction) in portals:
                    counts[side]['portal_crossings'] += 1
            if body[0] != head:
                body.appendleft(head)
            while len(body) > 1 and body[-1] != tail:
                body.pop()
            if body[-1] != tail:
                raise ValueError(f'tail not in reconstructed body of {did}')
            counts[side]['length_gained'] += max(0, len(body)-before)
            visited[side].add(head)
        elif kind == 10:
            parent, child, side = p.i32(0), p.i32(4), 'AB'[p.u16(8)]
            pb = deque(rp.point(v) for v in p.pointer(0))
            cb = deque(rp.point(v) for v in p.pointer(1))
            before = len(bodies[parent])
            if before != len(pb)+len(cb):
                raise ValueError('split length reconciliation failed')
            counts[side]['splits_'+length_class(before)] += 1
            for did, body in ((parent, pb), (child, cb)):
                bodies[did], teams[did] = body, side
                visited[side].add(body[0])
        elif kind == 11:
            did, reason = p.i32(0), p.u16(4)
            if did not in bodies:
                raise ValueError(f'death for absent dragon {did}')
            side, body = teams[did], bodies[did]
            cause, c = CAUSES[reason] if reason < 5 else 'other', length_class(len(body))
            counts[side]['deaths_'+cause] += 1
            counts[side]['deaths_'+c] += 1
            counts[side][f'deaths_{cause}_{c}'] += 1
            # The passive victim may die before the mover; count once per action.
            if reason == 3 and not headon_counted and current in bodies and teams[current] != side:
                counts[teams[current]]['headon_initiated_'+length_class(len(bodies[current]))] += 1
                headon_counted = True
            bodies.pop(did)
            drop = True
        elif kind == 12:
            sender = p.i32(0)
            if sender in teams:
                counts[teams[sender]]['sonar_messages'] += 1
                value = p.u64(16) if p.dwords >= 4 else p.u32(8)
                counts[teams[sender]]['sonar_nonzero_messages'] += int(value != 0)
            else:
                checks['unknown_sonar_sender'] += 1
    rounds = rnd + 1
    while boundary < len(BUCKETS) and rounds >= BUCKETS[boundary]:
        snapshot(BUCKETS[boundary], BUCKETS[boundary])
        boundary += 1
    # At an exact boundary the end row duplicates that interval, not an empty one.
    if rounds == previous and timeline:
        timeline.extend({**r, 'bucket': 'end'} for r in timeline[-2:])
    else:
        snapshot('end', rounds)
    result = root.pointer(4)
    winner = 'AB'[result.u16(6)] if result.u16(4) == 1 else None
    g = {k: v for k, v in task.items() if k in ('game_id', 'battle_id', 'replay_path', 'metadata_path', 'sources')}
    meta = task['meta']
    g.update(map=meta.get('mapName') or name, cells=w*h, width=w, height=h,
             map_size=size_class(w*h), rounds=rounds, winner=winner or 'draw',
             format_version=root.u32(0), terminated=result.bit(0), end_reason_code=result.u16(2),
             completed_at=meta.get('completedAt') or meta.get('downloadedAt'), ranked=meta.get('ranked'),
             scoresA=meta.get('scoresA'), scoresB=meta.get('scoresB'))
    for side in 'AB':
        for field in ('Id', 'Name', 'Elo'):
            g['team'+side+field] = meta.get('team'+side+field)
        end = next(r for r in timeline if r['side'] == side and r['bucket'] == 'end')
        standing = result.pointer('AB'.index(side))
        for metric, offset in (('units', 0), ('longest_length', 4), ('total_length', 8)):
            recorded = standing.i32(offset)
            if end[metric] != recorded:
                raise ValueError(f'final {side} {metric}: reconstructed {end[metric]}, recorded {recorded}')
            g['final_'+metric+'_'+side] = recorded
        g['final_queen_length_'+side] = end['queen_length']
    expected = None
    if result.u16(2) == 0:
        end_type = 'wipe-out'
        a, b = g['final_units_A'], g['final_units_B']
        expected = 'A' if a and not b else 'B' if b and not a else None
    elif result.u16(2) == 1:
        end_type = 'draw'
        for metric, label in (('queen_length', 'queen rule'), ('longest_length', 'longest'), ('total_length', 'total')):
            a, b = g['final_'+metric+'_A'], g['final_'+metric+'_B']
            if a != b:
                end_type, expected = label, 'A' if a > b else 'B'
                break
    else:
        end_type = 'unknown'
    if expected != winner and end_type != 'unknown':
        checks['winner_rule_mismatch'] += 1
        end_type = 'unknown'
    if str(meta.get('winner', '')).upper() in ('A', 'B') and str(meta['winner']).upper() != winner:
        checks['metadata_winner_mismatch'] += 1
    g['end_type'] = end_type
    g['winner_team_id'] = g.get('team'+winner+'Id') if winner else None
    return dict(game=g, timeline=timeline, checks=dict(checks), parse_seconds=time.perf_counter()-started)


def worker(task):
    cache = OUT / 'cache' / (str(task['game_id'])+'.json')
    try:
        signature = {'version': VERSION, 'script': task.pop('_script'),
                     'parser': task.pop('_parser'), 'sources': task['sources']}
        for key in ('replay_path', 'metadata_path'):
            p = Path(task[key])
            st = p.stat()
            signature[key] = [str(p), st.st_size, st.st_mtime_ns]
        if cache.exists():
            try:
                saved = json.loads(cache.read_text())
                if saved.get('signature') == signature:
                    return saved['result'], True, None
            except (ValueError, OSError):
                pass
        result = extract(task)
        for key in ('replay_path', 'metadata_path'):
            st = Path(task[key]).stat()
            if [task[key], st.st_size, st.st_mtime_ns] != signature[key]:
                raise ValueError('input changed during parsing; retry next run')
        atomic(cache, json.dumps({'signature': signature, 'result': result}, ensure_ascii=False))
        return result, False, None
    except Exception as exc:
        return None, False, {'game_id': task['game_id'], 'path': task['replay_path'],
                             'error': f'{type(exc).__name__}: {exc}'}


def discover():
    entries, errors = {}, []
    online = ROOT / 'data/online'
    patterns = [('top1', 'top1/*/game-*.json'), ('ours_ladder', 'dl-*/game-*.json'),
                ('ours_smoke', 'smoke/*/game-*.json')]
    for source, pattern in patterns:
        for path in sorted(online.glob(pattern)):
            try:
                meta = json.loads(path.read_text())
                if source != 'top1' and 1119 not in (meta.get('teamAId'), meta.get('teamBId')):
                    continue
                gid = int(meta.get('id', path.stem[5:]))
                replay = path.with_name(f'M{gid}.replay')
                if not replay.exists():
                    raise ValueError('replay missing (collector may still be writing)')
                if gid in entries:
                    if source not in entries[gid]['sources']:
                        entries[gid]['sources'].append(source)
                    continue
                entries[gid] = dict(game_id=gid, battle_id=path.parent.name, meta=meta,
                    replay_path=str(replay), metadata_path=str(path), sources=[source])
            except (OSError, ValueError, KeyError) as exc:
                errors.append({'path': str(path), 'error': str(exc)})
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    parser_hash = hashlib.sha256(PARSER.read_bytes()).hexdigest()
    for task in entries.values():
        task['_script'], task['_parser'] = script_hash, parser_hash
    return sorted(entries.values(), key=lambda t: t['game_id']), errors


def fmt(value):
    if value is None:
        return 'NA'
    if isinstance(value, float):
        if math.isinf(value):
            return '∞'
        return f'{value:.4g}'
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return ['| '+' | '.join(map(fmt, headers))+' |', '| '+' | '.join('---' for _ in headers)+' |'] + [
        '| '+' | '.join(map(fmt, r))+' |' for r in rows]


def median(rows, metric):
    values = [r[metric] for r in rows if r[metric] is not None]
    return statistics.median(values) if values else None


def write_csv(path, rows, fields):
    tmp = path.with_suffix('.csv.tmp')
    with tmp.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})
    tmp.replace(path)


def outcome(game, side):
    return 'draw' if game['winner'] == 'draw' else 'win' if game['winner'] == side else 'loss'


def team_rows(results, tid, own_only=False):
    return [r for res in results if not own_only or any(s.startswith('ours_') for s in res['game']['sources'])
            for r in res['timeline'] if r['team_id'] == tid]


def team_games(results, tid, own_only=False):
    return [(res['game'], side) for res in results
            if not own_only or any(s.startswith('ours_') for s in res['game']['sources'])
            for side in 'AB' if res['game']['team'+side+'Id'] == tid]


METHOD = '''# 측정 정의와 한계

- 입력은 실행 시작 시 발견된 top1/* 및 팀 1119가 참가한 dl-*와 smoke/*의 game JSON / M replay 쌍이다. game id로 중복 제거한다. 수집 중 불완전하거나 바뀐 파일은 errors.json에 남기고 다음 실행에서 재시도한다. 네트워크를 사용하지 않는다.
- 수치는 실제 온라인 기보의 관측이다. 팀 버전·상대·지도·시간 분포를 통제한 인과 비교가 아니다. top1 표본에는 비랭크 경기도 포함되며, 우리 비교에는 요청대로 smoke 경기도 포함된다. 우리 래더만의 결과도 별도 요약한다.
- 버킷 r25는 r0–24 이벤트와 r25 시작 상태, 이후는 이전 경계 이상 / 현재 경계 미만이다. end는 마지막 경계부터 종료까지다. 정확히 경계에서 끝나면 end가 마지막 버킷을 복제한다. 종료 후 경계는 생성하지 않는다. 따라서 뒤 버킷은 생존 게임으로 조건화되며 end의 구간 길이는 게임마다 다르다. bucket_rounds를 함께 제공한다.
- 상태는 map의 DRAGON 순서와 매 단계 dragonUpdate head/tail, split 전체 몸, death에서 복원한다. 최종 units/total/longest와 모든 split 질량을 기보 기록과 대조하고 불일치 게임은 제외한다. 유료 질주의 길이 감소는 기록된 tail을 따르므로 ceil(L/4) 공짜 걸음을 별도 비용으로 잘못 빼지 않는다.
- cells_visited는 시작·분열 직후·이동 단계의 머리 칸 합집합이다. 시야나 지식 영역이 아니다. 모든 거리는 토러스 맨해튼 거리이며 장애물·포털 최단거리를 뜻하지 않는다.
- pearls_natural/corpse는 tileChange 제거로 센다. 사망 직후 연속 pearl 추가는 corpse, 나머지 추가는 natural로 분류한다. 기존 ledger와 같은 이벤트 순서 규약이다. 출처 없는 제거는 unknown이다. length_gained는 단계별 양의 길이 변화만으로, 유료 걸음에서 먹고 길이가 유지된 경우를 놓치므로 보조 지표다.
- splits 길이 클래스는 분열 직전 부모 길이, deaths는 죽기 직전 길이, headon_initiated는 충돌 직전 공격자 길이, sprints는 요청 시 길이다. 클래스는 le4 / 5_9 / 10plus. 사망 cause는 원본 enum 0–4를 wall/self/body/headon/other로 매핑한다. other에는 자살·무효 행동 등이 포함되며, suicides는 명시적 suicide 행동만 센다.
- feeding_near_longest는 자살 시점 팀 최장(동률 최소 id)이 다른 용이며 6칸 이내인 경우다. 실제 먹이 전달 성공 또는 의도를 증명하지 않는다. 자기 자신을 먹이 대상에 포함하지 않는다.
- headon_initiated는 현재 행동 주체와 다른 팀의 머리 사망 이벤트에서 행동당 한 번 센다. 아군끼리 충돌은 제외한다. sprints/mean_steps는 2걸음 이상 요청 수와 요청 걸음 평균이며, 죽어서 실행 못 한 후속 걸음도 포함한다. 0회 버킷의 평균은 NA다.
- portal_crossings는 실제 dragonUpdate가 있는 이동 단계의 출발 EDGE가 portal인 횟수다. 실패한 충돌 시도의 포털 사용은 제외한다. sonar_messages는 sonarPing 이벤트(방향별 ping) 수이며 sonar_nonzero_messages는 payload가 0이 아닌 ping 수다. 논리적 방송 수·수신 성공·내용 해석은 측정하지 않는다.
- queen은 팀 A/B를 가정하지 않고 DRAGON 순서 id 0/1의 진영으로 정한다. 사망 시 alive=0/length=0, 거리·주변 동료 수는 NA다. 적이 없으면 nearest_enemy_distance는 NA다.
- 종료 원인은 replay의 wipe-out 플래그를 우선하고, 라운드 소진이면 여왕 길이→최장→총 길이 규칙으로 추론해 recorded winner와 검증한다. 종료 세부 동점 규칙은 기보에 명시된 필드가 아니므로 추론이다. terminated 비트는 원문 그대로 보존하며 강제 중단으로 해석하지 않는다(정상 종료 기보도 true). 알 수 없는 종료 enum이나 승자 모순은 unknown이다.
- 팀 순위는 각 팀의 completedAt 기준 가장 최신 top1 game JSON의 ELO(동률 game id)를 취해 내림차순이다. 수집 시각은 없을 때만 대체한다. 현재 서버 실시간 순위가 아니다. 표본 20판 이상 팀을 top 팀 요약에 포함한다.
- 요약은 게임별 각 버킷 지표의 중앙값이며 빈 값은 제외한다. 표마다 N과 각 지표 유효 n을 표시한다. gap의 ratio=rank1/comparator; 둘 다 0이면 1, 비교군만 0이면 ∞, 한쪽 NA면 NA. 상대 격차=max(ratio,1/ratio)-1 (둘 중 하나만 0이면 ∞), 방향은 ratio로 읽는다. 공통점/특이점은 비교용이지 유의성 판정이 아니다.
- notable은 각 지도 크기×상대×승/패에서 큰 격차 게임을 먼저 뽑아 다양성을 확보한다. 승리 크기는 결정 지표 차이(전멸은 최종 총 길이 차이) / max(1, 양팀 지표 합)이다. 서로 다른 종료 유형의 격차를 절대 실력 차이로 읽지 않는다.
'''


def reports(results, errors, runtime):
    games = [r['game'] for r in results]
    by_gid = {g['game_id']: g for g in games}
    rows = [row for r in results for row in r['timeline']]
    if games:
        write_csv(OUT/'games.csv', games, list(games[0]))
        write_csv(OUT/'timeline.csv', rows, list(rows[0]))
    latest, appearances = {}, Counter()
    for g in games:
        if 'top1' not in g['sources']:
            continue
        for side in 'AB':
            tid, elo = g['team'+side+'Id'], g['team'+side+'Elo']
            appearances[tid] += 1
            key = (g.get('completed_at') or '', g['game_id'])
            if elo is not None and (tid not in latest or key > latest[tid][0]):
                latest[tid] = (key, float(elo), g['team'+side+'Name'])
    ranking = sorted(latest, key=lambda t: (-latest[t][1], t))
    rank1 = ranking[0] if ranking else None
    intro = ['# 팀별 기보 지표', '', f'생성: {datetime.now(timezone.utc).isoformat()}; {len(games)} games, {len(rows)} timeline rows.',
             '정의·제약: [methodology.md](methodology.md). NA는 미관측/해당 없음. end는 게임별 남은 구간.', '']
    if rank1 is not None:
        intro += [f'최신 관측 ELO 1위: {latest[rank1][2]} (id {rank1}), {latest[rank1][1]:g}, 최신 game {latest[rank1][0][1]} / {latest[rank1][0][0]}.', '']
    summary = intro[:]
    for tid in [t for t in ranking if appearances[t] >= 20 and t != 1119] + [1119]:
        own = tid == 1119
        pairs = team_games(results, tid, own)
        if not own:
            pairs = [(g, s) for g, s in pairs if 'top1' in g['sources']]
        ids = {g['game_id'] for g, s in pairs}
        team = [r for r in rows if r['team_id'] == tid and r['game_id'] in ids]
        name = latest.get(tid, (None, None, str(tid)))[2]
        summary += [f'## {name} ({tid}), N={len(pairs)}', '']
        high = [(g, s) for g, s in pairs if (g.get('team'+('B' if s == 'A' else 'A')+'Elo') or 0) >= 2000]
        wins = [(g, s) for g, s in pairs if outcome(g, s) == 'win']
        summary += [f'상대 ELO ≥2000: {sum(outcome(g,s)=="win" for g,s in high)}/{len(high)} wins; win rate {fmt(sum(outcome(g,s)=="win" for g,s in high)/len(high) if high else None)} (무승부도 분모 포함).', '']
        ends = Counter(g['end_type'] for g, s in wins)
        summary += table(['승리 종료 유형', 'wins', 'share'], [(k, n, n/len(wins)) for k, n in sorted(ends.items())]) + ['']
        if own:
            ladder = [(g, s) for g, s in pairs if 'ours_ladder' in g['sources'] and g['ranked']]
            summary += [f'우리 ranked dl-*만: N={len(ladder)}, wins={sum(outcome(g,s)=="win" for g,s in ladder)}.', '']
        groups = defaultdict(list)
        for r in team:
            g = by_gid[r['game_id']]
            groups[(g['map_size'], outcome(g, r['side']))].append(r)
        for (size, result), group in sorted(groups.items()):
            summary += [f'### {size} / {result}', '']
            buckets = [str(b) for b in BUCKETS]+['end']
            grouped = {b: [r for r in group if r['bucket'] == b] for b in buckets}
            summary += table(['metric (median; valid n)']+buckets,
                [['N']+[len(grouped[b]) for b in buckets]] + [
                    [m]+[f'{fmt(median(grouped[b],m))} ({sum(r[m] is not None for r in grouped[b])})'
                         for b in buckets] for m in ('bucket_rounds',)+METRICS]) + ['']
        if not pairs:
            summary += ['읽을 수 있는 해당 팀 기보 없음.', '']
    atomic(OUT/'team_summary.md', '\n'.join(summary)+'\n')
    gap = ['# 최신 관측 1위와의 차이', '', '전체 지도 합산 및 지도 크기별 결과. 표본 구성·버전 차이는 통제하지 않았다. 비율은 1위 / 비교군.', '']
    if rank1 is not None:
        gap += [intro[-2], '']
        other = [t for t in ranking if t not in (rank1, 1119)][:2]
        ranked_rows = [r for r in team_rows(results, rank1) if 'top1' in by_gid[r['game_id']]['sources']]
        for tid in [1119]+other:
            comp = team_rows(results, tid, tid == 1119)
            if tid != 1119:
                comp = [r for r in comp if 'top1' in by_gid[r['game_id']]['sources']]
            gap += [f'## vs {latest.get(tid,(None,None,str(tid)))[2]} ({tid})', '']
            records = []
            for size in ('all', 'small<=700', 'medium701-1500', 'large>1500'):
                for bucket in [str(b) for b in BUCKETS]+['end']:
                    a = [r for r in ranked_rows if r['bucket']==bucket and (size=='all' or by_gid[r['game_id']]['map_size']==size)]
                    b = [r for r in comp if r['bucket']==bucket and (size=='all' or by_gid[r['game_id']]['map_size']==size)]
                    for m in ('bucket_rounds',)+METRICS:
                        x, y = median(a,m), median(b,m)
                        ratio = None if x is None or y is None else x/y if y else 1.0 if not x else math.inf
                        rel = -1 if ratio is None else math.inf if ratio == 0 or math.isinf(ratio) else max(ratio,1/ratio)-1
                        records.append((rel, [size,bucket,m,x,y,ratio,
                            sum(r[m] is not None for r in a),sum(r[m] is not None for r in b)]))
            records.sort(key=lambda p: -p[0])
            gap += table(['map size','bucket','metric','rank1 median','comparison median','ratio','n rank1','n comparison'], [r for _,r in records])+['']
    else:
        gap += ['순위를 정할 top1 기보가 없음.']
    atomic(OUT/'gap.md', '\n'.join(gap)+'\n')
    losses = ['# 1위 팀의 ELO ≥2000 상대 패배', '', '각 게임에서 winner / loser의 전체 지표를 같은 버킷으로 비교한다. 인과 추론은 하지 않는다.', '']
    candidates = []
    for g, side in team_games(results, rank1) if rank1 is not None else []:
        if 'top1' not in g['sources']:
            continue
        opp = 'B' if side == 'A' else 'A'
        result = outcome(g,side)
        if result == 'loss' and (g.get('team'+opp+'Elo') or 0) >= 2000:
            losses += [f'## Game {g["game_id"]}: {g["map"]} / {g["end_type"]}',
                       f'승자 {g["team"+opp+"Name"]} ({g["team"+opp+"Id"]}, ELO {g["team"+opp+"Elo"]}); 패자 {g["team"+side+"Name"]}.',
                       f'기보: `{g["replay_path"]}`', '']
            rs = { (r['side'],r['bucket']):r for r in rows if r['game_id']==g['game_id'] }
            bs = [str(b) for b in BUCKETS if (side,str(b)) in rs]+['end']
            losses += table(['metric']+[f'{b} winner / loser' for b in bs],
                [[m]+[f'{fmt(rs[opp,b][m])} / {fmt(rs[side,b][m])}' for b in bs]
                 for m in ('bucket_rounds',)+METRICS])+['']
        if result in ('win','loss'):
            metric = {'queen rule':'queen_length','longest':'longest_length','total':'total_length'}.get(g['end_type'],'total_length')
            a,b = g['final_'+metric+'_'+side],g['final_'+metric+'_'+opp]
            candidates.append(dict(game_id=g['game_id'], battle_id=g['battle_id'], map=g['map'], map_size=g['map_size'],
                opponent_id=g['team'+opp+'Id'], opponent_name=g['team'+opp+'Name'], opponent_elo=g['team'+opp+'Elo'],
                result=result, end_type=g['end_type'], margin_metric=metric, margin=abs(a-b)/max(1,a+b),
                replay_path=g['replay_path'], metadata_path=g['metadata_path']))
    if len(losses) == 4:
        losses += ['조건에 맞는 패배 없음.']
    atomic(OUT/'losses.md', '\n'.join(losses)+'\n')
    chosen, used = [], set()
    groups = defaultdict(list)
    for c in candidates:
        groups[(c['result'],c['map_size'],c['opponent_id'])].append(c)
    for group in groups.values():
        group.sort(key=lambda c: (-c['margin'],c['game_id']))
    # Cover sizes and opponents before filling with additional large margins.
    for result, quota in (('loss', 7), ('win', 8)):
        remaining = [c for c in candidates if c['result'] == result]
        seen_sizes, seen_opponents, seen_groups = Counter(), Counter(), set()
        for _ in range(min(quota, len(remaining))):
            c = max(remaining, key=lambda c: (
                -seen_sizes[c['map_size']], -seen_opponents[c['opponent_id']],
                (c['map_size'], c['opponent_id']) not in seen_groups,
                c['margin'], -c['game_id']))
            remaining.remove(c)
            chosen.append(c)
            used.add(c['game_id'])
            seen_sizes[c['map_size']] += 1
            seen_opponents[c['opponent_id']] += 1
            seen_groups.add((c['map_size'], c['opponent_id']))
    for c in sorted(candidates, key=lambda c: (-c['margin'],c['game_id'])):
        if len(chosen) >= 15:
            break
        if c['game_id'] not in used:
            chosen.append(c); used.add(c['game_id'])
    atomic(OUT/'notable.json',json.dumps(chosen,ensure_ascii=False,indent=2)+'\n')
    checks = Counter()
    for res in results:
        checks.update(res['checks'])
    runtime.update(games=len(games), timeline_rows=len(rows), rank1_team_id=rank1,
                   rank1_name=latest[rank1][2] if rank1 is not None else None,
                   checks=dict(checks), errors=len(errors), notable=len(chosen),
                   own_games=len(team_games(results,1119,True)),
                   top_games=sum('top1' in g['sources'] for g in games))
    atomic(OUT/'run.json', json.dumps(runtime,ensure_ascii=False,indent=2)+'\n')
    atomic(OUT/'errors.json', json.dumps(errors,ensure_ascii=False,indent=2)+'\n')
    atomic(OUT/'methodology.md',METHOD)
    return runtime


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--limit', type=int, help='diagnostic snapshot limit; default all games')
    args = cli.parse_args()
    if args.limit is not None and args.limit <= 0:
        cli.error('--limit must be positive')
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    tasks, errors = discover()
    if args.limit:
        tasks = tasks[:args.limit]
    print(f'Snapshot: {len(tasks)} games; 4 workers; discovery errors {len(errors)}',flush=True)
    results, hits, parsed, parse_seconds = [], 0, 0, 0.0
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(worker,t) for t in tasks]
        for i,future in enumerate(as_completed(futures),1):
            result,cached,error = future.result()
            if error:
                errors.append(error)
                print(f'ERROR {error}',flush=True)
            else:
                results.append(result)
                hits += int(cached)
                if not cached:
                    parsed += 1
                    parse_seconds += result['parse_seconds']
            if i % 25 == 0 or i == len(tasks):
                print(f'{i}/{len(tasks)} done; cache {hits}; parsed {parsed}; errors {len(errors)}; {time.perf_counter()-started:.1f}s',flush=True)
    results.sort(key=lambda r:r['game']['game_id'])
    runtime = reports(results,errors,dict(started_at=datetime.fromtimestamp(time.time()-(time.perf_counter()-started),timezone.utc).isoformat(),
        workers=4,discovered_games=len(tasks),cache_hits=hits,parsed_games=parsed,
        worker_parse_seconds=parse_seconds,worker_seconds_per_parsed_game=parse_seconds/parsed if parsed else None))
    runtime['wall_seconds'] = time.perf_counter()-started
    runtime['wall_seconds_per_game'] = runtime['wall_seconds']/len(results) if results else None
    atomic(OUT/'run.json', json.dumps(runtime,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(runtime,ensure_ascii=False),flush=True)
    return 0 if results and not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
