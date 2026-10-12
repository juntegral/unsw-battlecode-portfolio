#!/usr/bin/env python3
"""Offline label and downloaded-battle report; references and every input stay read-only."""
import sys
sys.dont_write_bytecode = True
import argparse
import ast
import hashlib
import glob
import json
import re
from collections import Counter, deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

import agg7_report as agg

HERE, DOS, SMOKE = agg.HERE, agg.DOS, agg.SMOKE
CHECKPOINTS = (50, 100, 150, 200, 300, 400)
BANDS = ('0-50', '51-100', '101-300')
KST = timezone(timedelta(hours=9))
USAGE = 'nice -n 10 python3 -B data/analysis/ladder/dossier/online/label_report.py <label> [--ref <label>[:old|:new] ...]'


def specification(value):
    match = re.fullmatch(r'([A-Za-z0-9][A-Za-z0-9_.-]*)(?::(old|new))?', value)
    if not match:
        raise argparse.ArgumentTypeError('라벨에는 영숫자/._-만, half에는 old/new만 사용')
    return match[1], match[2] or 'new'


def read_json(path, notes):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        notes.append(f'{path.name}: {type(error).__name__}: {error}')
        return None


def write_json(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n')
    temporary.replace(path)


def inventory(label, half):
    notes, jobs = [], []
    state = read_json(SMOKE / f'{label}.json', notes)
    if not isinstance(state, dict):
        state = {}
    halves = state.get('halves') or {}
    part = halves.get(half, {}) if isinstance(halves, dict) else {}
    if not isinstance(part, dict):
        part = {}
    if not part:
        notes.append(f'{label}:{half}: half 상태 없음; 폴더에 있는 완결 입력만 집계')
    raw_ids = part.get('battle_ids', [])
    if not isinstance(raw_ids, list):
        notes.append('battle_ids 미완성')
        raw_ids = []
    ids = [i for i in raw_ids if type(i) is int]
    if len(ids) != len(raw_ids):
        notes.append('battle_ids에 미완성/비정수 항목')
    duplicates = sorted(i for i, n in Counter(ids).items() if n > 1)
    if duplicates:
        notes.append(f'중복 battle_ids(한 번만 집계): {duplicates}')
    folder = SMOKE / f'{label}-{half}'
    available = {int(p.stem[1:]) for p in folder.glob('M*.replay') if p.stem[1:].isdigit()}
    metadata = {int(p.stem[5:]) for p in folder.glob('game-*.json') if p.stem[5:].isdigit()}
    unlisted = sorted((available | metadata) - set(ids))
    if unlisted:
        notes.append(f'상태에 아직 없는 파일 id: {unlisted}')
    for gid in sorted(set(ids) | available | metadata):
        rp, mp = folder / f'M{gid}.replay', folder / f'game-{gid}.json'
        absent = [p.name for p in (rp, mp) if not p.is_file()]
        if absent:
            notes.append(f'{gid}: 누락 {", ".join(absent)}')
            continue
        meta = read_json(mp, notes)
        required = ('id', 'teamAId', 'teamBId', 'teamAName', 'teamBName', 'winner',
                    'scoresA', 'scoresB', 'mapId', 'mapName')
        if not isinstance(meta, dict) or any(k not in meta for k in required):
            notes.append(f'{gid}: 메타데이터 미완성')
            continue
        if meta['id'] != gid or 1119 not in (meta['teamAId'], meta['teamBId']):
            notes.append(f'{gid}: id/팀 불일치 (가져온 agg7 집계기는 팀 1119 전용)')
            continue
        jobs.append((rp, meta))
    batches = part.get('batches', state.get('schedule', [])) or []
    planned = sum(len(b.get('maps', [])) for b in batches if isinstance(b, dict))
    if part.get('phase') == 'skipped':
        planned = 0
    elif not planned and state.get('planned_total'):
        halves = 1 if state.get('new_only') or state.get('old_only') else 2
        planned = state['planned_total'] // halves
    if len(set(ids)) < planned:
        notes.append(f'요청 id {len(set(ids))}/{planned}; 미요청 {planned-len(set(ids))}판')
    return dict(label=label, half=half, state=state, part=part, planned=planned,
                jobs=jobs, notes=notes, duplicate_ids=duplicates)


def directory_inventory(label, patterns):
    notes, folders, jobs, seen, requested, duplicates = [], [], [], set(), set(), []
    for pattern in patterns.split(','):
        matches = sorted(glob.glob(pattern))
        if not matches:
            notes.append(f'폴더 없음: {pattern}')
        for match in matches:
            folder = Path(match).resolve()
            if not folder.is_dir():
                notes.append(f'폴더 아님: {match}')
            elif folder not in folders:
                folders.append(folder)
    for folder in folders:
        index = read_json(folder/'index.json', notes)
        entries = (index.get('games') or []) if isinstance(index, dict) else []
        ids = {e['gameId'] for e in entries if isinstance(e, dict) and type(e.get('gameId')) is int}
        ids |= {int(p.stem[1:]) for p in folder.glob('M*.replay') if p.stem[1:].isdigit()}
        ids |= {int(p.stem[5:]) for p in folder.glob('game-*.json') if p.stem[5:].isdigit()}
        requested.update(ids)
        for gid in sorted(ids):
            rp, mp = folder/f'M{gid}.replay', folder/f'game-{gid}.json'
            absent = [p.name for p in (rp, mp) if not p.is_file()]
            if absent:
                notes.append(f'{folder.name}/{gid}: 누락 {", ".join(absent)}')
                continue
            meta = read_json(mp, notes)
            required = ('id', 'teamAId', 'teamBId', 'teamAName', 'teamBName', 'winner',
                        'scoresA', 'scoresB', 'mapId', 'mapName')
            if not isinstance(meta, dict) or any(k not in meta for k in required):
                notes.append(f'{folder.name}/{gid}: 메타데이터 미완성')
                continue
            if meta['id'] != gid or 1119 not in (meta['teamAId'], meta['teamBId']):
                notes.append(f'{folder.name}/{gid}: id/팀 불일치 (agg7 집계기는 팀 1119 전용)')
                continue
            if gid in seen:
                duplicates.append(gid)
                notes.append(f'{gid}: 여러 폴더에 중복(한 번만 집계)')
                continue
            seen.add(gid)
            jobs.append((rp, meta))
    return dict(label=label, half='new', pseudo=True, folders=[str(p) for p in folders],
                state={}, part={}, planned=len(requested), jobs=jobs, notes=notes, duplicate_ids=duplicates)


def dependency_versions():
    dependencies = [DOS/'count_dossier.py', DOS/'local/scoreboard.py', DOS/'local/spawn.py',
                    DOS/'local/replay_format.py', DOS/'local/count_local.py', DOS/'work/fp_build.py',
                    agg.ROOT/'tools/ladder_replay.py', DOS.parent/'losses/counts/count_replays.py']
    source = Path(agg.__file__).read_text()
    tree = ast.parse(source)
    scan_source = ''.join(ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name in ('supplement', 'count_job'))
    base = hashlib.sha256(scan_source.encode() + b''.join(p.read_bytes() for p in dependencies)).hexdigest()
    version = hashlib.sha256(Path(__file__).read_bytes() + base.encode()).hexdigest()
    return base, version


def death_category(death):
    if death is None:
        return 'alive'
    if death['cause'] == 'head-on hit':
        return 'rammed'
    if death['cause'] == 'head-on mover':
        return 'ran into a head'
    return 'boxed in'


def scan_details(root, meta, geo, base):
    w, h = geo.w, geo.h
    bodies, teams = {}, {}
    own = int(meta['teamAId'] != 1119)
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w + int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(int(q[1]) != own)
    queens = [min(i for i in bodies if teams[i] == s) for s in (0, 1)]
    starters = {i for i, b in bodies.items() if teams[i] == 0 and len(b) >= 4}
    split0, snapshots, pearls, turns = set(), {}, [0, 0], [0, 0]
    queen_turns, rams, defend, deaths = [], [], Counter(), []
    rnd, actor, context, qt = -1, None, {}, None
    distances = {}
    queen_context, queen_ram = {}, None

    def man(a, b):
        dx, dy = abs(a % w-b % w), abs(a // w-b // w)
        return min(dx, w-dx) + min(dy, h-dy)

    def square(a, b):
        dx, dy = abs(a % w-b % w), abs(a // w-b // w)
        return min(dx, w-dx) <= 3 and min(dy, h-dy) <= 3

    def path3(src):
        if src not in distances:
            seen, queue = {src: 0}, deque([src])
            while queue:
                c = queue.popleft()
                if seen[c] == 5:
                    continue
                for dest in geo.adj[c]:
                    if dest not in seen:
                        seen[dest] = seen[c]+1
                        queue.append(dest)
            distances[src] = seen
        return distances[src]

    def snapshot():
        return [dict(alive=sum(teams[i] == s for i in bodies),
                     total=sum(len(b) for i, b in bodies.items() if teams[i] == s),
                     longest=max((len(b) for i, b in bodies.items() if teams[i] == s), default=0),
                     queen_length=len(bodies.get(queens[s], ())),
                     pearls=pearls[s], turns=turns[s]) for s in (0, 1)]

    def close_turn():
        nonlocal qt
        if qt is not None:
            qt['end_head'] = bodies[queens[0]][0] if queens[0] in bodies else None
            qt = None

    tile = lambda p: agg.sb.replay_format.point(p)[1]*w + agg.sb.replay_format.point(p)[0]
    for index, ev in enumerate(root.pointer(3)):
        kind = ev.u16(0)
        if kind not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kind == 0:
            close_turn()
            if rnd >= 0:
                snapshots[rnd] = snapshot()
            rnd, actor = p.i32(0), None
        elif kind == 1:
            close_turn()
            actor = p.i32(0)
            context = {i: (len(b), b[0]) for i, b in bodies.items()}
            turns[teams[actor]] += 1
            if actor == queens[0]:
                hd = bodies[actor][0]
                queen_context = dict(context)
                mates = [(i, b[0]) for i, b in bodies.items() if teams[i] == 0 and i != actor]
                enemies = [(i, b[0]) for i, b in bodies.items() if teams[i] == 1]
                ball = path3(hd)
                threats = [i for i, cell in enemies if i != queens[1] and ball.get(cell, 99) <= 3]
                near_own = min((cell for _, cell in mates), key=lambda cell: (man(hd, cell), cell), default=None)
                near_enemy = min((cell for _, cell in enemies), key=lambda cell: (man(hd, cell), cell), default=None)
                qt = dict(n=len(queen_turns)+1, round=rnd, event=index, length=len(bodies[actor]),
                          head=hd, end_head=None, threats=threats,
                          enemy3=int(any(ball.get(cell, 99) <= 3 for _, cell in enemies)),
                          mates5=sum(man(hd, cell) <= 5 for _, cell in mates),
                          own_square=1+sum(square(hd, cell) for _, cell in mates),
                          enemy_square=sum(square(hd, cell) for _, cell in enemies),
                          nearest_own=near_own, nearest_enemy=near_enemy, steps=[], pearls=0)
                queen_turns.append(qt)
        elif kind == 3:
            if not p.u32(0):
                assert actor is not None
                pearls[teams[actor]] += 1
                if actor == queens[0]:
                    assert qt is not None
                    qt['pearls'] += 1
        elif kind == 9:
            i = p.i32(0)
            hd, tail = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if i == queens[0] and qt is not None:
                    qt['steps'].append([b[0], hd])
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
        elif kind == 10:
            parent, child = p.i32(0), p.i32(4)
            if rnd == 0 and parent in starters:
                split0.add(parent)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
                teams[i] = int(p.u16(8) != own)
        elif kind == 11:
            i, reason = p.i32(0), p.u16(4)
            deaths.append(dict(id=i, round=rnd, event=index, side=teams[i], reason=reason, actor=actor))
            if i == queens[0] and reason == 3 and actor != i and actor is not None:
                distance = None
                if actor in queen_context and i in queen_context:
                    distance = geo.bfs([queen_context[i][1]])[queen_context[actor][1]]
                    if distance < 0 or distance >= w*h:
                        distance = None
                queen_ram = dict(id=actor, length=len(bodies[actor]), side='AB'[own if teams[actor] == 0 else 1-own],
                                 relation='우리' if teams[actor] == 0 else '상대', distance=distance,
                                 distance_at='사망 직전 마지막 여왕 차례 시작',
                                 round=queen_turns[-1]['round'] if queen_turns else None)
            if reason == 3 and i != actor and actor is not None and teams[actor] == 0 and teams[i] == 1:
                if actor != queens[0]:
                    ram = dict(round=rnd, event=index, actor=actor, target=i,
                               length=context[actor][0], target_length=context[i][0], distance=None)
                    if queens[0] in context:
                        ram['distance'] = path3(context[queens[0]][1]).get(context[i][1], 99)
                        if i != queens[1]:
                            band = 'near3' if ram['distance'] <= 3 else 'off4_5' if ram['distance'] <= 5 else None
                            if band:
                                defend[band + ('_small' if ram['length'] <= 4 else '_large')] += 1
                    rams.append(ram)
            bodies.pop(i)
    close_turn()
    snapshots[rnd] = snapshot()
    final = snapshots[rnd]
    for s, expected in enumerate((base['final'], base['their'])):
        assert all(final[s][key] == expected[key] for key in ('alive', 'total', 'longest', 'queen_length'))
    assert pearls[0] == base['extra']['counts'].get('eaten', 0)
    assert turns[0] == base['extra']['counts'].get('turns', 0)
    checkpoints = {str(c): snapshots[min(c, rnd)] for c in CHECKPOINTS}
    checkpoints['end'] = final
    episodes, current = [], None
    for turn in queen_turns:
        if not turn['threats']:
            current = None
            continue
        if current is None:
            current = []
            episodes.append(current)
        current.append(turn)
    qdeath = next((d for d in deaths if d['id'] == queens[0]), None)
    chases = []
    for ep in episodes:
        pursuers = sorted({i for turn in ep for i in turn['threats']})
        last_n = ep[-1]['n']
        end_event = queen_turns[last_n]['event'] if last_n < len(queen_turns) else index+1
        hits = [r for r in rams if ep[0]['event'] <= r['event'] < end_event and r['target'] in pursuers]
        rammed = bool(qdeath and qdeath['reason'] == 3 and qdeath['actor'] != queens[0]
                      and ep[-1]['event'] <= qdeath['event'] < end_event)
        chases.append(dict(start=ep[0]['round'], end=ep[-1]['round'], turns=len(ep), pursuers=pursuers,
                           no_mate5=ep[0]['mates5'] == 0, mate_rams=hits, queen_rammed=rammed))
    qc = Counter()
    for turn in queen_turns:
        r, L = turn['round'], turn['length']
        if r <= 300:
            qc['turns_0_300'] += 1
            qc['L'+('4+' if L >= 4 else str(L))] += 1
            band = BANDS[0 if r <= 50 else 1 if r <= 100 else 2]
            qc['turns_'+band] += 1
            qc['enemy3_'+band] += turn['enemy3']
            qc['mates5_'+band] += turn['mates5']
        qc['pearls'] += turn['pearls']
        if 51 <= r <= 300:
            qc['herd_turns'] += 1
            qc['herd_alone'] += turn['mates5'] == 0
        if 51 <= r <= 300 and turn['own_square'] < 2:
            qc['herd_eligible_turns'] += 1
            for before, after in turn['steps']:
                qc['herd_steps'] += 1
                cell = turn['nearest_own']
                if cell is not None:
                    qc['herd_nearer'] += man(after, cell) < man(before, cell)
                else:
                    qc['herd_no_mate_steps'] += 1
        if turn['enemy_square'] > turn['own_square']:
            qc['fallback_turns'] += 1
            hd, end = turn['head'], turn['end_head']
            if end is None:
                qc['fallback_died'] += 1
            else:
                cell = turn['nearest_enemy']
                delta = man(end, cell)-man(hd, cell)
                qc['fallback_'+('away' if delta > 0 else 'toward' if delta < 0 else 'level')] += 1
                mate = turn['nearest_own']
                if mate is not None:
                    qc['fallback_mate_available'] += 1
                    qc['fallback_toward_mate'] += man(end, mate) < man(hd, mate)
    for suffix in ('2', '3', '4+'):
        assert qc['L'+suffix] == base['extra']['counts'].get('queen_turns_L'+suffix, 0)
    assert sum(qc['L'+suffix] for suffix in ('2', '3', '4+')) == qc['turns_0_300']
    assert sum(qc['fallback_'+k] for k in ('away', 'toward', 'level', 'died')) == qc['fallback_turns']
    return dict(last_round=rnd, checkpoints=checkpoints, queen_counts=dict(qc), queen_turns=queen_turns,
                chases=chases, defend=dict(defend), rams=rams,
                split0=dict(split=len(split0), eligible=len(starters), ids=sorted(split0)),
                queen_cause=death_category(base['extra']['queen_death']), queen_ram=queen_ram)


def game_time(meta, inv):
    for key in ('startedAt', 'requestedAt', 'completedAt'):
        value = meta.get(key)
        if value:
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(KST).isoformat(timespec='seconds'), key
            except (ValueError, TypeError):
                pass
    for req in inv['part'].get('requests', []):
        if meta['id'] in req.get('ids', []) and req.get('requested_at'):
            return datetime.fromisoformat(req['requested_at']).astimezone(KST).isoformat(timespec='seconds'), 'batch requested_at'
    return None, '시간 없음'


def collect(inv, cache, legacy, base_version, version, counter, cache_path, stats):
    rows = []
    for path, meta in inv['jobs']:
        signature = [version, hashlib.sha256(path.read_bytes()).hexdigest(),
                     hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()]
        key = str(path)
        old = cache.get(key)
        if old and old['signature'] == signature:
            row = old['row']
            stats['reused'] += 1
        else:
            before = path.stat()
            try:
                cached_base = legacy.get(key)
                if cached_base and cached_base['signature'] == [base_version, *signature[1:]]:
                    base = cached_base['row']
                    stats['agg7_reused'] += 1
                else:
                    base = agg.count_job(inv['label'], path, meta, counter)
                    stats['agg7_counted'] += 1
                root = agg.sb.load_replay(path).root()
                lines = root.text(0).splitlines()
                w, h = map(int, lines[0].split()[1:3])
                raw = [tuple(map(int, q[1:4])) for q in map(str.split, lines) if q and q[0] == 'EDGE']
                details = scan_details(root, meta, counter.Geo(w, h, raw), base)
                after = path.stat()
                assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), '입력 변경; 재실행 필요'
                timestamp, source = game_time(meta, inv)
                row = dict(base, half=inv['half'], time=timestamp, time_source=source, details=details)
                cache[key] = dict(signature=signature, row=row)
                write_json(cache_path, cache)
                stats['parsed'] += 1
            except Exception as error:
                inv['notes'].append(f'{meta["id"]}: 집계 불가 {type(error).__name__}: {error}')
                continue
        rows.append(dict(row, label=inv['label'], half=inv['half']))
        if len(rows) % 5 == 0:
            print(f'{inv["label"]}:{inv["half"]} {len(rows)}/{len(inv["jobs"])}', flush=True)
    assert len(rows) == len({r['game'] for r in rows})
    return rows


def validate_log(inv, rows):
    if inv.get('pseudo'):
        return [dict(opponent=op, actual=[len(rs := [r for r in rows if r['opponent'] == op]),
                                         sum(r['result'] == 'win' for r in rs)],
                     status='not countable', reason='폴더 입력: 상대별 report.log 없음')
                for op in sorted({r['opponent'] for r in rows})] or [dict(status='pending', reason='집계 경기 없음')]
    path = SMOKE / f'{inv["label"]}-report.log'
    if not path.exists():
        return [dict(status='pending', reason='report.log 없음')]
    expected, partial = {}, []
    text = path.read_text()
    for raw in text.splitlines(keepends=True):
        line = raw.rstrip('\r\n')
        if not raw.endswith(('\n', '\r')):
            partial.append('마지막 미완성 로그 줄 제외')
            continue
        m = re.match(r'vs (.*?): wins new (\d+)/(\d+)', line)
        if inv['half'] == 'new':
            m = m or re.match(r'no live baseline yet vs (.*?): new (\d+)/(\d+) wins', line)
            if m:
                expected[m[1]] = (int(m[3]), int(m[2]), 'per-opponent new')
        elif live := re.match(r'vs (.*?): wins live (\d+)/(\d+)', line):
            expected[live[1]] = (int(live[3]), int(live[2]), 'this run only; live-only old half')
        elif m:
            direct = re.search(r'vs live (\d+(?:\.\d+)?)/(\d+)', line)
            if direct:
                expected[m[1]] = (int(direct[2]), float(direct[1]), 'pooled live; 개별 old 로그 아님')
    if inv['half'] == 'old':
        opponents = inv['part'].get('opponents', inv['state'].get('opponents', [])) or []
        complete = ''.join(line for line in text.splitlines(keepends=True) if line.endswith(('\n', '\r')))
        current = re.search(r'^this run only, (\d+) pairs \| wins: live (\d+) -> new (\d+)', complete, re.M)
        if len(opponents) == 1 and current:
            expected[opponents[0]['name']] = (int(current[1]), int(current[2]), 'this run only; 단일 상대 old half')
    included_ops = {r['opponent'] for r in rows}
    if inv.get('excluded_games'):
        expected = {op: value for op, value in expected.items() if op in included_ops}
    checks = []
    for opponent in sorted({r['opponent'] for r in rows} | set(expected)):
        rs = [r for r in rows if r['opponent'] == opponent]
        actual = [len(rs), sum(r['result'] == 'win' for r in rs)]
        exp = expected.get(opponent)
        if exp is None:
            checks.append(dict(opponent=opponent, actual=actual, status='pending', reason='상대별 로그 줄 없음'))
        elif inv['half'] == 'old' and not exp[2].startswith('this run only'):
            checks.append(dict(opponent=opponent, actual=actual, expected=list(exp[:2]),
                               status='not countable', reason=exp[2]))
        else:
            status = 'passed' if actual == list(exp[:2]) else 'pending' if actual[0] < exp[0] else 'mismatch'
            checks.append(dict(opponent=opponent, actual=actual, expected=list(exp[:2]), status=status, reason=exp[2]))
    checks += [dict(status='pending', reason=reason) for reason in partial]
    if not checks:
        checks.append(dict(status='pending', reason='집계 경기/완성 상대별 로그 줄 없음'))
    return checks


def mean(values):
    return agg.ratio(sum(values), len(values))


def number(value):
    return 'NA' if value is None else f'{value:.2f}'


def pooled(rows, source, key):
    if source == 'counts':
        return sum(r['extra']['counts'].get(key, 0) for r in rows)
    return sum(r['details'][source].get(key, 0) for r in rows)


def percent(n, d):
    return f'{number(agg.ratio(100*n, d))}% ({n}/{d})' if d else f'NA ({n}/0)'


def hours(rows):
    times = [r['time'] for r in rows if r['time']]
    return (min(times)+' ～ '+max(times) if times else 'NA') + f'; 시간 미상 {len(rows)-len(times)}'


def shifts(main, references):
    candidates = []
    metrics = [('r100 우리 총길이', lambda rs: mean([r['details']['checkpoints']['100'][0]['total'] for r in rs])),
               ('r300 우리 총길이', lambda rs: mean([r['details']['checkpoints']['300'][0]['total'] for r in rs])),
               ('종료 우리 총길이', lambda rs: mean([r['final']['total'] for r in rs])),
               ('종료 여왕 생존 %', lambda rs: mean([100*int(r['final']['queen_length'] > 0) for r in rs])),
               ('여왕 L2 턴 %', lambda rs: agg.ratio(100*pooled(rs, 'queen_counts', 'L2'), pooled(rs, 'queen_counts', 'turns_0_300'))),
               ('순길이 /1k turns', lambda rs: agg.ratio(1000*(pooled(rs, 'counts', 'eaten')-pooled(rs, 'counts', 'lost')), pooled(rs, 'counts', 'turns')))]
    metrics += [(name+' 사건', lambda rs, key=key: pooled(rs, 'counts', key)) for name, key in
                [('ZONE_NEARER', 'zone_nearer'), ('TRADE_EVEN', 'trade_even'), ('HUNT_SMALL_RATIO', 'hunt_small'),
                 ('LUNGE_PEARL', 'lunge_pearl'), ('FEEDER_EAT', 'feeder_eat')]]
    metrics += [('여왕 진주', lambda rs: pooled(rs, 'queen_counts', 'pearls')),
                ('추격 횟수', lambda rs: sum(len(r['details']['chases']) for r in rs)),
                ('HERD 고립 %', lambda rs: agg.ratio(100*pooled(rs, 'queen_counts', 'herd_alone'), pooled(rs, 'queen_counts', 'herd_turns'))),
                ('HERD 접근 걸음 %', lambda rs: agg.ratio(100*pooled(rs, 'queen_counts', 'herd_nearer'), pooled(rs, 'queen_counts', 'herd_steps')))]
    for name, ref in references:
        if not ref:
            continue
        ops = {r['opponent_id'] for r in ref}
        matched = [r for r in main if r['opponent_id'] in ops]
        for metric, fn in metrics:
            a, b = fn(matched), fn(ref)
            if a is not None and b is not None:
                candidates.append((abs(a-b), f'{metric}: {a:.2f} / {name} {b:.2f}, Δ{a-b:+.2f} (본 라벨 {len(matched)}판/참조 {len(ref)}판)'))
    return '; '.join(text for _, text in sorted(candidates, key=lambda x: -x[0])[:3]) or 'NA (비교 가능한 참조 없음)'


def report(label, columns, inventories, checks, stats):
    main = columns[0][1]
    lines = [f'경기: {columns[0][0]} {len(main)}판.',
             f'승리: {sum(r["result"] == "win" for r in main)}/{len(main)}.',
             '참조와 수치 차이(|Δ| 상위 3, 성장·여왕·기제 지표의 표시 단위 기준): '+shifts(main, columns[1:])+'.', '',
             f'# {label} 온라인 라벨 보고서', '',
             f'생성: {datetime.now(KST).isoformat(timespec="seconds")}; 팀 1119; 시간 KST(UTC+9).',
             '참조 열은 본 라벨에 실제로 집계된 상대 id와 같은 경기만 포함. 상대·시간·지도 분포를 맞춘 인과 비교가 아니다.', '']

    unrestricted = any(inv.get('pseudo') for inv in inventories)
    if unrestricted:
        lines[-2] = '폴더 입력을 포함하여 참조 열의 같은 상대 필터를 끔. 상대·시간·지도 분포를 맞춘 인과 비교가 아니다.'

    def column_header(name, rows):
        if not unrestricted:
            return name
        opponents = sorted({(r['opponent_id'], r['opponent']) for r in rows})
        return name+'; '+('; '.join(f'{op} (id {oid}) {len(sub := [r for r in rows if r["opponent_id"] == oid])}판 {sum(r["result"] == "win" for r in sub)}승'
                                    for oid, op in opponents) or '상대 없음')

    def table(title, entries):
        lines.extend([title, '', '| 항목 | '+' | '.join(column_header(name, rows) for name, rows in columns)+' |', '|---|'+'---|'*len(columns)])
        for name, fn in entries:
            lines.append('| '+name+' | '+' | '.join(str(fn(rs)) if rs else 'NA (0판)' for _, rs in columns)+' |')
        lines.append('')

    ops = sorted({(r['opponent_id'], r['opponent']) for _, rows in columns for r in rows})
    table('## 1. 경기와 시간', [('경기 / 승리', lambda rs: f'{len(rs)} / {sum(r["result"] == "win" for r in rs)}'),
                                 ('시간 범위 / 미상', hours)] +
          [(f'{op} (id {oid}) 경기/승; 시간', lambda rs, oid=oid: f'{len(sub := [r for r in rs if r["opponent_id"] == oid])}/{sum(r["result"] == "win" for r in sub)}; {hours(sub)}') for oid, op in ops])
    for inv in inventories:
        lines.append(f'{inv["label"]}:{inv["half"]}: 예정 {inv["planned"]}판; '+('; '.join(inv['notes']) or '누락 없음')+'.')
    lines.extend(['', '## 2. 각 경기', '',
                  '각 열은 상대 id·지도 id·경기 id 순으로 독립 정렬. 같은 행 번호가 짝 경기를 뜻하지 않는다. 길이 순서는 우리/상대.', '',
                  '| 번호 | '+' | '.join(column_header(name, rows) for name, rows in columns)+' |', '|---|'+'---|'*len(columns)])
    ordered = [sorted(rs, key=lambda r: (r['opponent_id'], r['map_id'], r['game'])) for _, rs in columns]

    def game_cell(r):
        qd = r['extra']['queen_death']
        death = 'alive' if qd is None else f'r{qd["round"]} {r["details"]["queen_cause"]} ({qd["cause"]})'
        ram = r['details'].get('queen_ram')
        if r['details']['queen_cause'] == 'rammed' and ram:
            distance = 'NA' if ram['distance'] is None else str(ram['distance'])
            death += f'; 충돌 용 #{ram["id"]} L{ram["length"]} {ram["side"]}({ram["relation"]}), 직전 여왕 차례 시작 r{ram["round"]} 거리 {distance}걸음'
        return (f'{r["game"]} {r["opponent"]}; {r["map"]}, {r["cells"]}칸; {r["result"]}; {r["extra"]["decided"]}; '
                f'T {r["final"]["total"]}/{r["their"]["total"]}, L {r["final"]["longest"]}/{r["their"]["longest"]}, '
                f'Q {r["final"]["queen_length"]}/{r["their"]["queen_length"]}; Q {death}')
    for i in range(max(map(len, ordered), default=0)):
        lines.append(f'| {i+1} | '+' | '.join(game_cell(rs[i]) if i < len(rs) else '—' for rs in ordered)+' |')
    lines.extend(['', 'Q=여왕 길이, L=최장, T=총길이. 결정은 전멸을 먼저, 그 뒤 Q/L/T. boxed in은 기존 tq2 분류의 기타 사망 묶음이며 세부 원인을 괄호에 병기.', ''])
    growth = []
    for point in (*CHECKPOINTS, 'end'):
        for side, title in ((0, '우리'), (1, '상대')):
            growth.append((f'r{point} {title} 생존 용 / 총길이 (판 평균)', lambda rs, p=str(point), s=side:
                           ' / '.join(number(mean([r['details']['checkpoints'][p][s][k] for r in rs])) for k in ('alive', 'total'))))
    for p in (100, 300):
        growth.append((f'r{p}까지 진주 우리 / 상대 (판 평균)', lambda rs, p=str(p):
                       ' / '.join(number(mean([r['details']['checkpoints'][p][s]['pearls'] for r in rs])) for s in (0, 1))))
    growth.append(('순길이 /1,000 turns (agg7)', lambda rs: number(agg.ratio(1000*(pooled(rs, 'counts', 'eaten')-pooled(rs, 'counts', 'lost')), pooled(rs, 'counts', 'turns')))))
    table('## 3. 성장', growth)
    lines.extend(['체크포인트는 라운드 종료 상태. 조기 종료는 최종 상태를 유지. 순길이=(섭취 진주−사망 당시 길이 합)/우리 차례×1,000. 개별 경기 체크포인트·분자·분모는 JSON에 보존.', ''])
    queen = []
    for p in (100, 150, 300, 'end'):
        queen.append((f'r{p} 여왕 생존', lambda rs, p=str(p): f'{sum(r["details"]["checkpoints"][p][0]["queen_length"] > 0 for r in rs)}/{len(rs)}'))
    queen += [('여왕 사망 원인 / 생존', lambda rs: '; '.join(f'{k} {v}' for k, v in sorted(Counter(r['details']['queen_cause'] for r in rs).items()))),
              ('여왕 턴 길이 2 / 3 / 4+ % (r0-300)', lambda rs: ' / '.join(percent(pooled(rs, 'queen_counts', 'L'+k), pooled(rs, 'queen_counts', 'turns_0_300')) for k in ('2', '3', '4+')))]
    for band in BANDS:
        queen += [(f'r{band} 적 머리 3걸음 안: /여왕 100턴', lambda rs, b=band: percent(pooled(rs, 'queen_counts', 'enemy3_'+b), pooled(rs, 'queen_counts', 'turns_'+b))),
                  (f'r{band} 아군 머리 5칸 안 / 여왕 턴', lambda rs, b=band: number(agg.ratio(pooled(rs, 'queen_counts', 'mates5_'+b), pooled(rs, 'queen_counts', 'turns_'+b))))]
    def all_chases(rs):
        return [c for r in rs for c in r['details']['chases']]
    queen += [('근접 추격: 횟수 / 평균 턴', lambda rs: f'{len(cs := all_chases(rs))} / {number(mean([c["turns"] for c in cs]))}'),
              ('추격마다 턴 수 (game:r범위=턴)', lambda rs: '; '.join(f'{r["game"]}:r{c["start"]}-{c["end"]}={c["turns"]}' for r in rs for c in r['details']['chases']) or '0'),
              ('추격 시작 아군 5칸 없음', lambda rs: percent(sum(c['no_mate5'] for c in all_chases(rs)), len(all_chases(rs)))),
              ('추격 중 아군이 추격자에게 충돌', lambda rs: percent(sum(bool(c['mate_rams']) for c in all_chases(rs)), len(all_chases(rs)))),
              ('여왕 피격으로 끝난 추격', lambda rs: percent(sum(c['queen_rammed'] for c in all_chases(rs)), len(all_chases(rs)))),
              ('여왕 진주 섭취: 합 / 판 평균', lambda rs: f'{pooled(rs, "queen_counts", "pearls")} / {number(agg.ratio(pooled(rs, "queen_counts", "pearls"), len(rs)))}')]
    table('## 4. 여왕', queen)
    lines.extend(['3걸음은 열린 변·포털 최단거리(몸 무시); 위험률은 적 여왕도 포함한 턴 비율. 추격은 비여왕 적 머리가 3걸음 안에 있는 연속 여왕 차례(tq2_chase 정의), 아군 근접은 토러스 맨해튼이며 여왕 자신 제외. 추격자 충돌은 추격 첫 차례부터 다음 비추격 차례 직전까지의 실제 비여왕 아군 선제 충돌. 턴 길이·위험·근접 창 외 추격/진주는 경기 전체.', ''])
    def events(rs, keys):
        return ' / '.join(str(pooled(rs, 'counts', k)) for k in keys)
    mechanisms = [(name, lambda rs, k=key: events(rs, (k,))) for name, key in
                  [('ZONE_NEARER', 'zone_nearer'), ('TRADE_EVEN', 'trade_even'), ('HUNT_SMALL_RATIO', 'hunt_small')]]
    mechanisms += [('QS_KEEP_LEN', lambda rs: str(sum(sp['child_length'] == 2 and sp['after_length'] < 3 for r in rs for sp in r['extra']['queen_splits']))),
                   ('TRADE_SHORT_BY (L3/L4/L5+; equal/2+)', lambda rs: events(rs, ('trade_short_L3', 'trade_short_L4', 'trade_short_L5plus', 'trade_equal', 'trade_short_2plus'))),
                   ('LUNGE_PEARL / paid-sprint hits', lambda rs: events(rs, ('lunge_pearl', 'paid_sprint_hits'))),
                   ('FEEDER_EAT', lambda rs: events(rs, ('feeder_eat',))),
                   ('SPLIT_ROUND0', lambda rs: percent(pooled(rs, 'split0', 'split'), pooled(rs, 'split0', 'eligible'))),
                   ('QUEEN_DEFEND_STEPS (≤3: L≤4/L5+; 4-5: L≤4/L5+)', lambda rs: ' / '.join(str(pooled(rs, 'defend', k)) for k in ('near3_small', 'near3_large', 'off4_5_small', 'off4_5_large'))),
                   ('QUEEN_HERD (r51-300 고립 %; 주변 아군<2일 때 가까워진 걸음 %)', lambda rs: percent(pooled(rs, 'queen_counts', 'herd_alone'), pooled(rs, 'queen_counts', 'herd_turns'))+'; '+percent(pooled(rs, 'queen_counts', 'herd_nearer'), pooled(rs, 'queen_counts', 'herd_steps'))),
                   ('QUEEN_FALLBACK (불리한 턴; away/toward/level/dead; 아군 방향)', lambda rs: str(pooled(rs, 'queen_counts', 'fallback_turns'))+'; '+' / '.join(str(pooled(rs, 'queen_counts', 'fallback_'+k)) for k in ('away', 'toward', 'level', 'died'))+'; '+percent(pooled(rs, 'queen_counts', 'fallback_toward_mate'), pooled(rs, 'queen_counts', 'fallback_mate_available')))]
    table('## 5. 기제 조건에 맞는 사건', mechanisms)
    lines += [
        'ZONE_NEARER: agg7의 리더 전환 라운드 뒤 비리더 섭취 중 리더 머리에서 9칸 이내이며 먹은 용의 시작 머리가 리더보다 진주에 가까운 사건.',
        'TRADE_EVEN: agg7의 아군 선제 적 머리 충돌 중 충돌 시 동길이이고 시작 아군 수가 UNIT_LIMIT 미만인 사건.',
        'HUNT_SMALL_RATIO: agg7의 시작 길이≤4 아군이 시작한 적 머리 충돌 중 적 길이가 우리 시작 길이의 2배 이상인 사건.',
        'QS_KEEP_LEN: agg7의 여왕 분열 중 자식 L2·직후 여왕 L<3 횟수(유지 조건에서 벗어난 관측 사건; 일상/탈출 미분리).',
        'TRADE_SHORT_BY: agg7의 비여왕 선제 충돌 중 충돌 시 아군 L3/L4/L5+이고 적이 정확히 1 짧은 횟수; 동길이/2 이상 짧음도 같은 모집단.',
        'LUNGE_PEARL: agg7의 시작 ceil(L/4)를 넘는 적 머리 충돌 걸음이며 그 차례 유료 걸음에서 진주를 먹은 사건/모든 유료 충돌.',
        'FEEDER_EAT: agg7의 비여왕·최장보다 짧은 용의 사망 전 0–3라운드 섭취 중, 낙하 진주가 사망 후 0–3라운드에 시작 최장에게 먹힌 경우의 고유 섭취 사건.',
        'SPLIT_ROUND0: r0에서 분열한 시작 L≥4 아군 id 수/시작 L≥4 아군 수(여왕 포함).',
        'QUEEN_DEFEND_STEPS: 시작 길이≤4/5+ 비여왕 아군의 선제 적 비여왕 머리 충돌; 차례 시작 적 머리와 우리 여왕 머리의 열린 변·포털 거리≤3/4–5로 구분.',
        'QUEEN_HERD: r51–300의 아군 머리 5칸 없는 여왕 턴/해당 턴; 같은 창에서 시작 7×7 안 아군 머리<2(여왕 포함)인 차례의 실제 성공 걸음 중 시작 시 가장 가까운 아군 머리에 토러스 맨해튼으로 가까워진 비율. 아군이 전혀 없는 걸음은 분모에 포함하고 JSON에 따로 보존.',
        'QUEEN_FALLBACK: 전체 경기의 시작 7×7 안 적 머리>아군 머리(여왕 포함) 차례; 차례 끝 머리와 시작 시 최근접 적/아군의 토러스 맨해튼 변화. 사망은 dead 별도; 아군 방향 분모는 생존하고 아군이 있는 차례.',
        '기보에는 실행 스위치 표식이 없어 위 사건은 발동 의도나 해당 스위치만의 효과를 증명하지 않는다.', '',
        '## 6. 점검', '', '| 열 | 고유 경기 | 로그 대조 |', '|---|---|---|']
    for (name, rows), check in zip(columns, checks):
        lines.append(f'| {name} | {len(rows)} / {len({r["game"] for r in rows})} | '+
                     '; '.join(f'{c.get("opponent", "전체")}: {c["status"]}, 실제 {c.get("actual", "NA")}, 로그 {c.get("expected", "NA")} ({c.get("reason", "")})' for c in check)+' |')
    lines += ['', '각 입력 half의 id를 한 번만 집계; 같은 경기를 여러 참조로 지정해도 파싱은 캐시를 재사용. 참조 필터에서 제외된 경기 수는 JSON inventories에 보존.',
              f'캐시: 재사용 {stats["reused"]}, 새 상세 집계 {stats["parsed"]}; agg7 기존 행 {stats["agg7_reused"]}, count_job 호출 {stats["agg7_counted"]}.',
              '집계 한계: boxed in은 공간 봉쇄의 인과 진단이 아닌 tq2의 비머리충돌 사망 범주. 타임아웃/불법 행동/벽/몸은 원래 원인을 같이 표시. 여왕에게 성공하지 못한 마지막 이동은 걸음 비율에 포함되지 않는다. old의 vs live 값은 여러 실행을 합친 기준선일 수 있어 old half 로그 일치로 간주하지 않는다. 정확 스위치·일상/탈출 분열·먹이기 의도는 기보에 없음.',
              f'재실행: `{USAGE}`. 개별 경기와 상세 추격/차례: `label-{label}{"-old" if inventories[0]["half"] == "old" else ""}.json`.']
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label', type=specification)
    parser.add_argument('--ref', action='append', type=specification, default=[])
    parser.add_argument('--dir', action='append', default=[], metavar='NAME=FOLDER[,FOLDER...]')
    args = parser.parse_args()
    directories = {}
    for value in args.dir:
        name, sep, patterns = value.partition('=')
        if not sep or not patterns or specification(name) != (name, 'new'):
            parser.error('--dir 형식: NAME=FOLDER[,FOLDER...]')
        if name in directories:
            parser.error('--dir 이름 중복')
        directories[name] = patterns
    if any(half != 'new' for label, half in [args.label, *args.ref] if label in directories):
        parser.error('폴더 라벨은 half를 지정하지 않음')
    selected = [args.label, *args.ref]
    unrestricted = any(label in directories for label, _ in selected)
    if len(selected) != len(set(selected)):
        parser.error('동일 라벨:half를 중복 지정할 수 없음')
    base_version, version = dependency_versions()
    cache_path = HERE/'label-report-cache.json'
    cache_notes = []
    cache = (read_json(cache_path, cache_notes) or {}) if cache_path.exists() else {}
    legacy_path = HERE/'agg7-cache.json'
    legacy = (read_json(legacy_path, cache_notes) or {}) if legacy_path.exists() else {}
    counter = agg.sb.load_counter()
    stats = Counter(reused=0, parsed=0, agg7_reused=0, agg7_counted=0)
    inventories, columns, checks, seen = [], [], [], {}
    for index, (label, half) in enumerate(selected):
        inv = directory_inventory(label, directories[label]) if label in directories else inventory(label, half)
        if index == 0:
            inv['notes'].extend(cache_notes)
        rows = collect(inv, cache, legacy, base_version, version, counter, cache_path, stats)
        full_rows = rows
        if index and not unrestricted:
            opponents = {r['opponent_id'] for r in columns[0][1]}
            rows = [r for r in rows if r['opponent_id'] in opponents]
        for r in rows:
            previous = seen.get(r['game'])
            if previous is not None:
                inv['notes'].append(f'{r["game"]}: 앞 열 {previous}와 같은 경기; 이 열에서 제외')
            else:
                seen[r['game']] = f'{label}:{half}'
        rows = [r for r in rows if seen[r['game']] == f'{label}:{half}']
        inv['available_games'], inv['included_games'] = len(full_rows), len(rows)
        inv['excluded_games'] = len(full_rows)-len(rows)
        if inv['excluded_games']:
            inv['notes'].append(f'상대 불일치/중복 {inv["excluded_games"]}판 제외')
        checks.append(validate_log(inv, rows))
        columns.append((f'{label}:{half}', rows))
        inventories.append(inv)
    label = args.label[0]
    output_label = label + ('-old' if args.label[1] == 'old' else '')
    output = report(label, columns, inventories, checks, stats)
    payload = dict(label=label, generated_at=datetime.now(KST).isoformat(timespec='seconds'),
                   columns=[dict(name=name, games=rows) for name, rows in columns],
                   inventories=[{k: v for k, v in inv.items() if k not in ('jobs', 'state', 'part')} for inv in inventories],
                   checks=checks, cache=dict(stats))
    write_json(HERE/f'label-{output_label}.json', payload)
    (HERE/f'label-{output_label}.md').write_text(output)
    for name, rows in columns:
        print(f'{name}: {len(rows)} games, {sum(r["result"] == "win" for r in rows)} wins', flush=True)
    print(f'Cache: {dict(stats)}; report: label-{output_label}.md', flush=True)
    if any(c['status'] == 'mismatch' for check in checks for c in check):
        raise SystemExit('로그 불일치: 보고서 점검 참조')


if __name__ == '__main__':
    main()
