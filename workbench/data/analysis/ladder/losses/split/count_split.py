#!/usr/bin/env python3
"""Offline replay count; run with python3 -B. Writes new files only here."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import hashlib
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from statistics import median

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
DATA = ROOT / 'data/analysis/ladder'
COUNTS = OUT.parent / 'counts'
spec = importlib.util.spec_from_file_location('previous_counts', COUNTS / 'count_replays.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
replay, Geometry = previous.replay, previous.Geometry
SIDES = ('us', 'them')
CHECKPOINTS = (0, 5, 10, 20, 30)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan(row, old, checks, digest):
    path = ROOT / checks['replay']
    meta_path = path.parent / ('game-%d.json' % row['game'])
    digest[str(path.relative_to(ROOT))] = sha(path)
    digest[str(meta_path.relative_to(ROOT))] = sha(meta_path)
    metadata = json.loads(meta_path.read_text())
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    xy = lambda c: [c % w, c // w]
    bodies, teams, edges = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2*k])*w + int(q[3 + 2*k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            edges.append(tuple(map(int, q[1:4])))
    g = Geometry(w, h, edges)
    ours = row['our_side']
    assert metadata['team' + ours + 'Id'] == 1119
    side = lambda i: 'us' if teams[i] == ours else 'them'
    starts = {s: sorted(i for i in bodies if side(i) == s) for s in SIDES}
    queens = {s: starts[s][0] for s in SIDES}
    assert set(queens.values()) == {0, 1}
    initial = {s: len(starts[s]) for s in SIDES}
    assert initial == checks['initial_dragons']
    two = all(n == 2 for n in initial.values())
    initial_lengths = {i: len(b) for i, b in bodies.items()}
    out = {s: dict(side=ours if s == 'us' else ('B' if ours == 'A' else 'A'),
                   queen_id=queens[s], starting_dragons=[dict(id=i, queen=i == queens[s],
                   initial_length=initial_lengths[i]) for i in starts[s]],
                   first_split=None, second_split=None, first_three_meals=[],
                   starting_snapshots={}, turns_0_30=[], deaths_0_30=[],
                   split_lengths=Counter()) for s in SIDES}
    eaten = defaultdict(list)
    pearl_counts = Counter()
    pearl50 = Counter()
    present = {}
    rnd, actor, used, seq = 0, None, 0, 0
    dirs, action_cause = [], None
    pending = None
    turn_deaths = []
    snap100 = None
    seen_round = False

    def standings():
        return {s: dict(alive=sum(side(i) == s for i in bodies),
                        total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                        longest=max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                        queen_length=len(bodies.get(queens[s], ()))) for s in SIDES}

    def snapshot(n):
        nonlocal snap100
        if n == 100:
            snap100 = standings()
        if two and n in CHECKPOINTS:
            for s in SIDES:
                population = sum(side(i) == s for i in bodies)
                out[s]['starting_snapshots'][str(n)] = [
                    dict(id=i, alive=i in bodies, length=len(bodies.get(i, ())),
                         side_dragons=population, pearls_eaten=len(eaten[i])) for i in starts[s]]

    def finish_turn():
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if hs:
            assert len(hs) == 2
            for d in hs:
                other = next(z for z in hs if z is not d)
                d.update(other_id=other['id'], other_side=other['side'],
                         other_length=other['length'], simultaneous_with=other['id'])
        turn_deaths.clear()

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            assert pending is None
            finish_turn()
        if k == 0:
            if seen_round:
                snapshot(rnd)
            rnd, actor = p.i32(0), None
            seen_round = True
        elif k == 1:
            actor = p.i32(0)
            assert actor in bodies
            seq += 1
            dirs, used, action_cause = [], 0, None
            if two and rnd <= 30:
                s = side(actor)
                enemies = [i for i, b in bodies.items() if side(i) != s and g.visible(bodies[actor][0], b[0])]
                any_view = any(g.visible(b[0], eb[0]) for i, b in bodies.items() if side(i) == s
                               for ei, eb in bodies.items() if side(ei) != s)
                out[s]['turns_0_30'].append(dict(round=rnd, event=idx, turn=seq, id=actor,
                    length=len(bodies[actor]), enemy_head_in_actor_view=bool(enemies),
                    enemy_head_ids=enemies, enemy_head_in_any_side_dragon_view=any_view))
        elif k == 4:
            assert actor == p.i32(0)
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used_up = p.pointer(1)
            action_cause = ('timeout' if p.bit(32) or (used_up is not None and used_up.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)] if a and a.u16(0) < 3 else 'no action')
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                assert c not in present
                present[c] = dict(origin='natural' if actor is None else 'death_drop',
                                  spawn_round=rnd, spawn_event=idx)
            else:
                assert c in present and actor in bodies and pending is None
                meal = dict(round=rnd, event=idx, id=actor, xy=xy(c), **present.pop(c))
                eaten[actor].append(meal)
                s = side(actor)
                pearl_counts[s] += 1
                if rnd <= 50:
                    pearl50[s] += 1
                if len(out[s]['first_three_meals']) < 3:
                    out[s]['first_three_meals'].append(meal)
                pending = (actor, c)
        elif k == 9:
            i = p.i32(0)
            head, tail = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != head
            if moved:
                b.appendleft(head)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
            if pending is not None:
                assert pending == (i, head) and moved
                pending = None
            if i == actor and moved:
                used += 1
        elif k == 10:
            i, child = p.i32(0), p.i32(4)
            s = side(i)
            assert i == actor and child not in teams
            length = len(bodies[i])
            out[s]['split_lengths'][length] += 1
            pieces = [deque(tile(replay.point(c)) for c in p.pointer(z)) for z in (0, 1)]
            assert sum(map(len, pieces)) == length
            split = dict(round=rnd, event=idx, id=i, child_id=child, length_before_split=length,
                         child_lengths=list(map(len, pieces)), queen=i == queens[s],
                         starting_dragon=i in starts[s],
                         who='queen' if i == queens[s] else 'other_starting' if i in starts[s] else 'descendant',
                         pearls_eaten_before=len(eaten[i]),
                         meals_before_split=list(eaten[i]),
                         meal_origins=dict(Counter(m['origin'] for m in eaten[i])))
            if out[s]['first_split'] is None:
                out[s]['first_split'] = split
            elif out[s]['second_split'] is None:
                out[s]['second_split'] = split
            for z, dragon_id in enumerate((i, child)):
                bodies[dragon_id] = pieces[z]
                teams[dragon_id] = 'AB'[p.u16(8)]
                assert side(dragon_id) == s
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            dest = g.moves[bodies[i][0]][dirs[used]][1] if i == actor and used < len(dirs) else None
            other = next((z for z, b in bodies.items() if z != i and dest in b), None) if reason == 2 else None
            d = dict(round=rnd, event=idx, turn=seq, id=i, side=side(i), actor=actor,
                     length=len(bodies[i]), reason=reason,
                     cause=('wall', 'own body', 'other dragon body', 'head-on', action_cause or 'no action')[reason],
                     starting_dragon=i in starts[side(i)], queen=i == queens[side(i)],
                     other_id=other, other_side=side(other) if other is not None else None,
                     other_length=len(bodies[other]) if other is not None else None)
            if two and rnd <= 30:
                out[side(i)]['deaths_0_30'].append(d)
            turn_deaths.append(d)
            bodies.pop(i)
    finish_turn()
    assert pending is None
    snapshot(rnd)
    final = standings()
    assert final == row['final'] == checks['final_reconstructed']
    assert rnd == row['last_round']
    result = root.pointer(4)
    for z, s in enumerate(SIDES if ours == 'A' else ('them', 'us')):
        st = result.pointer(z)
        assert [final[s][k] for k in ('alive', 'longest', 'total', 'queen_length')] == [st.i32(o) for o in (0, 4, 8, 12)]
    winner = 'AB'[result.u16(6)] if result.u16(4) == 1 else None
    assert ('draw' if winner is None else 'win' if winner == ours else 'loss') == row['result']
    if row['curves']['100'] is not None:
        assert snap100 == {s: {k: row['curves']['100'][s][k] for k in final[s]} for s in SIDES}
    if old is not None:
        assert two == old['two_a_side']
        assert (out['us']['first_split'] or {}).get('round') == old['first_split_round']
        assert (out['us']['first_three_meals'][0]['round'] if out['us']['first_three_meals'] else None) == old['first_meal_round']
        assert {s: pearl50[s] for s in SIDES} == old['pearls_through50']
        assert (snap100['us']['alive'] if snap100 is not None else 0) == old['alive_end_round100']
    for s in SIDES:
        out[s]['first_split_round'] = (out[s]['first_split'] or {}).get('round')
        out[s]['second_split_round'] = (out[s]['second_split'] or {}).get('round')
        out[s]['first_three_meal_rounds'] = [m['round'] for m in out[s]['first_three_meals']]
        out[s]['first_three_meal_rounds'] += [None] * (3 - len(out[s]['first_three_meal_rounds']))
        out[s]['turns_with_enemy_0_30'] = sum(t['enemy_head_in_actor_view'] for t in out[s]['turns_0_30'])
        out[s]['turns_with_any_side_view_enemy_0_30'] = sum(t['enemy_head_in_any_side_dragon_view'] for t in out[s]['turns_0_30'])
        out[s]['turns_count_0_30'] = len(out[s]['turns_0_30'])
        out[s]['pearls_through50'] = pearl50[s]
        out[s]['pearls_entire_game'] = pearl_counts[s]
        out[s]['split_lengths'] = dict(sorted(out[s]['split_lengths'].items()))
        if two:
            for n in CHECKPOINTS:
                out[s]['starting_snapshots'].setdefault(str(n), None)
    excluded = None if old else ('ended_before100_with_us_alive' if row['curves']['100'] is None
                                else 'layout_has_no_never_grew_main_games')
    record = dict(game=row['game'], battle=row['battle'], replay=checks['replay'],
                  our_code='main', our_side=ours, map_key=row['map_key'], result=row['result'],
                  opponent_result='draw' if row['result'] == 'draw' else 'win' if row['result'] == 'loss' else 'loss',
                  group=old['group'] if old else None, comparison_exclusion=excluded,
                  last_round=rnd, initial_dragons=initial,
                  alive_end_round100=snap100['us']['alive'] if snap100 else (0 if final['us']['alive'] == 0 else None),
                  final_reconstructed=final, final_matches_rows=True, winner_matches_rows=True, sides=out)
    return record, two


def bins(records, side):
    c = Counter('later_or_never' if r['sides'][side]['first_split_round'] is None else
                '0_10' if r['sides'][side]['first_split_round'] <= 10 else
                '11_30' if r['sides'][side]['first_split_round'] <= 30 else
                '31_60' if r['sides'][side]['first_split_round'] <= 60 else 'later_or_never' for r in records)
    return '/'.join(str(c[k]) for k in ('0_10', '11_30', '31_60', 'later_or_never'))


def medrange(values):
    return '—' if not values else f'{median(values):g}[{min(values)}–{max(values)}]'


def hist(values):
    return ','.join(f'{v}:{n}' for v, n in sorted(Counter(values).items())) or '—'


def describe_lengths(rs, rnd):
    parts = []
    for j in (0, 1):
        observed = [r['sides']['us']['starting_snapshots'][str(rnd)] for r in rs]
        vals = [z[j]['length'] for z in observed if z is not None]
        dead = sum(not z[j]['alive'] for z in observed if z is not None)
        parts.append(medrange(vals) + f';사망{dead};미도달{sum(z is None for z in observed)}')
    return '/'.join(parts)


def report(records, minimum):
    selected = [r for r in records if r['group'] is not None]
    lines = ['# 초기 분열 집계', '',
             '| 군 | 우리 편 | layout key | 경기 | 우리 0–10/11–30/31–60/>60·없음 | 상대 같은 구간 | 시작 길이 우리 Q/O; 상대 Q/O |',
             '|---|---|---|---:|---|---|---|']
    for group in ('never_grew', 'grew'):
        rs = [r for r in selected if r['group'] == group]
        slices = [('*', '*', rs)]
        slices += [(s, '*', [r for r in rs if r['our_side'] == s]) for s in 'AB']
        slices += [(s, key, [r for r in rs if r['our_side'] == s and r['map_key'] == key])
                   for key in sorted({r['map_key'] for r in selected}) for s in 'AB'
                   if any(r['our_side'] == s and r['map_key'] == key for r in rs)]
        for side, key, subset in slices:
            lengths = '; '.join('/'.join(hist([r['sides'][s]['starting_dragons'][j]['initial_length'] for r in subset])
                                        for j in (0, 1)) for s in SIDES)
            lines.append(f'| {group} | {side} | {key} | {len(subset)} | {bins(subset, "us")} | {bins(subset, "them")} | {lengths} |')
    lines += ['', '| 우리 첫 분열 | 경기 | r5 길이 Q/O | r10 길이 Q/O | 시작 용 섭취 ≤5/≤10 | 적 시야 <10 | 시작 용 사망 <30 |',
              '|---|---:|---|---|---|---:|---:|']
    for early in (False, True):
        rs = [r for r in selected if (r['sides']['us']['first_split_round'] is not None and
                                      r['sides']['us']['first_split_round'] <= 10) == early]
        meal = [sum(any(z['pearls_eaten'] > 0 for z in r['sides']['us']['starting_snapshots'][str(n)] or [])
                    for r in rs) for n in (5, 10)]
        view = sum(any(t['round'] < 10 and t['enemy_head_in_actor_view'] for t in r['sides']['us']['turns_0_30']) for r in rs)
        dead = sum(any(d['round'] < 30 and d['starting_dragon'] for d in r['sides']['us']['deaths_0_30']) for r in rs)
        lines.append(f'| {"≤10" if early else ">10·없음"} | {len(rs)} | {describe_lengths(rs, 5)} | {describe_lengths(rs, 10)} | {meal[0]}/{meal[1]} | {view} | {dead} |')
    lines += ['', '| 군 | 관측 편 | Q/O/후손/없음 | 첫 분열 길이 Q; O; 후손 (길이:건) |', '|---|---|---|---|']
    for group in ('never_grew', 'grew'):
        for s in SIDES:
            fs = [r['sides'][s]['first_split'] for r in selected if r['group'] == group]
            who = Counter(f['who'] if f else 'none' for f in fs)
            counts = '/'.join(str(who[k]) for k in ('queen', 'other_starting', 'descendant', 'none'))
            lengths = '; '.join(hist([f['length_before_split'] for f in fs if f and f['who'] == k])
                                for k in ('queen', 'other_starting', 'descendant'))
            lines.append(f'| {group} | {s} | {counts} | {lengths} |')
    lines += ['', '| 군 | 상대 먼저/같음/나중 | 우리 없음·상대 있음/우리 있음·상대 없음/둘 없음 |', '|---|---|---|']
    for group in ('never_grew', 'grew'):
        c = Counter()
        for r in selected:
            if r['group'] != group:
                continue
            u, t = (r['sides'][s]['first_split_round'] for s in SIDES)
            if u is None or t is None:
                c['both_none' if u is t else 'us_none' if u is None else 'them_none'] += 1
            else:
                c['earlier' if t < u else 'same' if t == u else 'later'] += 1
        lines.append(f'| {group} | ' + '/'.join(str(c[k]) for k in ('earlier', 'same', 'later')) + ' | ' +
                     '/'.join(str(c[k]) for k in ('us_none', 'them_none', 'both_none')) + ' |')
    lines += ['',
              f'관측 최소 분열 길이: main {minimum["main_games"]}판 {minimum["events"]}건, 전체 {minimum["overall"]}, 우리 {minimum["us"]}, 상대 {minimum["them"]}; L<4 성공 {minimum["below4"]}건; 최소 L의 자식 길이 {minimum["minimum_child_lengths"]}.',
              '정의·한계:',
              '- main만; 양쪽 2마리 시작 174판은 JSON 전수 수록. 비교는 기존 growth.json의 같은 layout key 집단 118판=66/52; Maze 30·weakhold 22·r100 전 종료 생존 Trophy 4판은 군 null·표 제외.',
              '- 군: r100 종료 우리 수 ≤6·그 전 전멸=never_grew, 같은 layout에서 >6=grew. 표 *는 합계; us/them은 우리/상대; Q/O는 낮은 시작 id(0/1) 여왕/나머지 시작 용.',
              '- 첫·둘째 분열과 첫 3회 섭취는 전체 경기 사건 순서; 섭취 1회=진주 1개(자연·낙하 포함), 같은 라운드 중복 가능. 분열 길이는 사건 직전; 섭취 이력은 그 id 자신의 평생 기록이며 물려받은 질량 제외.',
              '- r0/5/10/20/30 상태는 라운드 종료; 시작 길이는 지도 원본. 길이 중앙값[최소–최대], 사망=0; 사망/미도달은 경기 수, 길이:건은 빈도. 섭취·시야·사망 열은 조건을 만족한 경기 수.',
              '- 시야는 이전 파서와 같은 turnStart의 행동 용 중심 경계 순환 7×7(벽 무시·포털 확장 없음); JSON에 그 편 모든 용 시야 합집합도 별도 수록. 초기 사건 r0–30 포함; 표 <10/<30은 엄격한 미만.',
              '- >10·없음은 첫 분열 없는 판 포함. 상대 비교는 양쪽 분열 존재 시 라운드만 비교(같은 라운드 사건 선후 제외); 분열 없음 조합 별도. 미도달 스냅샷 null, 봇 내부 결정·최소 허용 규칙은 기보만으로 확정 불가.',
              '- 관측상 L=4에서 2+2 분열; L<4 성공 없음. 이전 validation.json의 main 400판 ID 고정; 갱신된 rows.jsonl 중 그 ID만 스냅샷. 최종 상태·승패와 이전 첫 섭취·분열·r50 섭취·r100 생존 수 대조.']
    assert len(lines) <= 60, len(lines)
    return '\n'.join(lines) + '\n'


def worker(args):
    digest = {}
    record, two = scan(*args, digest)
    return record, two, digest


def main():
    names = ('summary.md', 'per-game.json', 'validation.json', 'last.txt')
    assert not any((OUT / n).exists() for n in names), 'Existing outputs must not be overwritten.'
    digest = {str(p.relative_to(ROOT)): sha(p) for p in COUNTS.iterdir() if p.is_file()}
    growth = {r['game']: r for r in json.loads((COUNTS / 'growth.json').read_text())}
    checks = {r['game']: r for r in json.loads((COUNTS / 'validation.json').read_text())}
    source = (DATA / 'rows.jsonl').read_bytes()
    current = {r['game']: r for r in map(json.loads, source.decode().splitlines()) if r}
    rows = [current[i] for i in sorted(checks)]
    assert len(rows) == 400 and all(r['our_code'] == 'main' for r in rows)
    assert all(r['final'] == checks[r['game']]['final_reconstructed'] for r in rows)
    frozen = OUT / 'source-snapshot.json'
    assert not frozen.exists()
    frozen.write_text(json.dumps(dict(rows=rows, source_rows_sha256_at_read=hashlib.sha256(source).hexdigest(),
                                     original_counts_inputs_sha256=json.loads((COUNTS / 'inputs.json').read_text())),
                                     ensure_ascii=False, indent=2) + '\n')
    digest[str(frozen.relative_to(ROOT))] = sha(frozen)
    records, all_splits, examples = [], {s: Counter() for s in SIDES}, []
    verified = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(worker, (row, growth.get(row['game']), checks[row['game']])) for row in rows]
        for n, future in enumerate(as_completed(futures), 1):
            record, two, hashes = future.result()
            digest.update(hashes)
            verified.append(record['game'])
            for s in SIDES:
                all_splits[s].update(record['sides'][s]['split_lengths'])
                if two:
                    fs = record['sides'][s]['first_split']
                    if fs is not None:
                        examples.append(dict(game=record['game'], side=s, **fs))
            if two:
                records.append(record)
            if n % 25 == 0 or n == len(rows):
                print(f'Offline reconstructed {n}/{len(rows)} fixed main games; {len(records)} two-start games.', flush=True)
    assert set(verified) == set(checks)
    records.sort(key=lambda r: r['game'])
    selected = [r for r in records if r['group'] is not None]
    expected = {i for i, r in growth.items() if r['two_a_side']}
    assert {r['game'] for r in selected} == expected
    assert len(records) == 174 and Counter(r['group'] for r in selected) == {'never_grew': 66, 'grew': 52}
    assert {r['game'] for r in records} == {i for i, c in checks.items() if c['initial_dragons'] == {'us': 2, 'them': 2}}
    all_lengths = all_splits['us'] + all_splits['them']
    minimum = dict(main_games=len(rows), events=sum(all_lengths.values()), overall=min(all_lengths),
                   us=min(all_splits['us']), them=min(all_splits['them']),
                   below4=sum(n for l, n in all_lengths.items() if l < 4),
                   minimum_child_lengths=sorted({tuple(e['child_lengths']) for e in examples if e['length_before_split'] == min(all_lengths)}),
                   split_length_histograms={s: dict(sorted(all_splits[s].items())) for s in SIDES})
    assert minimum['overall'] == 4 and minimum['minimum_child_lengths'] == [(2, 2)]
    summary = report(records, minimum)
    for relative, expected_hash in digest.items():
        assert sha(ROOT / relative) == expected_hash, relative
    validation = dict(main_games_verified=len(verified), main_game_ids=sorted(verified),
                      two_start_games=len(records), comparison_games=len(selected),
                      previous_group_counts={'never_grew': 66, 'grew': 52}, exact_previous_game_id_sets_match=True,
                      previous_metrics_match=True, final_standings_and_winners_match=True,
                      observed_minimum_split=minimum, inputs_sha256=digest,
                      summary_lines=len(summary.splitlines()))
    (OUT / 'summary.md').write_text(summary)
    (OUT / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'per-game.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    last = [datetime.now().astimezone().isoformat(timespec='seconds'),
            'Two-start main: 174 games; previous comparison: 66 never grew + 52 grew = 118; exact game-id sets matched.',
            f'Main {len(verified)}/{len(rows)} final states/winners match; previous first meals/splits, r50 intake and r100 population match.',
            f'Observed minimum successful split length {minimum["overall"]}; L<4: {minimum["below4"]}; summary {len(summary.splitlines())} lines.',
            'Offline only; frozen inputs/counts/replays SHA-256 unchanged; source rows updated externally; outputs only in split/; written LAST.']
    assert len(last) <= 5
    (OUT / 'last.txt').write_text('\n'.join(last) + '\n')
    print('\n'.join(last), flush=True)


if __name__ == '__main__':
    main()
