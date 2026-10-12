#!/usr/bin/env python3
"""Validate completed counts, write the report, and write last.txt last."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import median

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
DATA = ROOT / 'data/analysis/ladder'


def read(name):
    return json.loads((OUT / name).read_text())


def pct(n, d):
    return '—' if d == 0 else f'{100 * n / d:.2f}%'


def avg(n, d):
    return '—' if d == 0 else f'{n / d:.3f}'


def hunt_stats(rows, length=None):
    selected = [(r, [t for t in r['turns'] if length is None or length(t[1])]) for r in rows]
    turns = [t for _, tt in selected for t in tt]
    ages = Counter('never' if t[5] is None else '0_20' if t[5] <= 20 else '21_60' if t[5] <= 60 else 'gt60' for t in turns)
    mid = [t for t in turns if t[5] is not None and 21 <= t[5] <= 60]
    distances = Counter('no_short' if t[6] == 0 else 'unreachable' if t[4] is None else
                        'le20' if t[4] <= 20 else '21_40' if t[4] <= 40 else 'gt40' for t in mid)
    return dict(games=len(rows) if length is None else sum(bool(tt) for _, tt in selected),
                queen_turns=len(turns), heads_within12=sum(t[2] for t in turns),
                short_heads_within12=sum(t[3] for t in turns), sightings=dict(ages),
                mid_age_turns=len(mid), mid_age_distances=dict(distances))


def growth_stats(rows):
    c = Counter()
    for r in rows:
        c.update(r['no_meal'])
        assert sum(v[-1] for v in r['joint']) == r['no_meal']['turns']
        for klass in ('none', 'le6', '7_15', 'gt15', 'unreachable'):
            assert sum(v[-1] for v in r['joint'] if v[0] == klass) == r['no_meal'].get('known_' + klass, 0)
        for index, key in ((1, 'centre_reduce'), (2, 'enemy_in_view'), (3, 'no_successful_step')):
            assert sum(v[index] * v[-1] for v in r['joint']) == r['no_meal'].get(key, 0)
        assert sum(r['no_meal'].get('known_' + k, 0) for k in ('none', 'le6', '7_15', 'gt15', 'unreachable')) == r['no_meal']['turns']
        assert r['no_meal']['centre_reduce'] <= r['no_meal']['turns'] - r['no_meal']['no_successful_step']
    return dict(games=len(rows), layouts=len({r['map_key'] for r in rows}), no_meal=dict(c),
                first_meal=[r['first_meal_round'] for r in rows],
                first_split=[r['first_split_round'] for r in rows],
                pearls50={s: sum(r['pearls_through50'][s] for r in rows) for s in ('us', 'them')},
                gone_before100=sum(r['gone_before100'] for r in rows))


def round_summary(values):
    present = [v for v in values if v is not None]
    return ('—' if not present else f'{median(present):g} [{min(present)}–{max(present)}]') + f'; {len(values) - len(present)}'


def main():
    hunt, growth, validation = read('hunt.json'), read('growth.json'), read('validation.json')
    inputs = read('inputs.json')
    for relative, expected in inputs.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    rows = [json.loads(s) for s in (DATA / 'rows.jsonl').read_text().splitlines() if s.strip()]
    rows = {r['game']: r for r in rows if r['our_code'] == 'main'}
    losses = json.loads((DATA / 'losses/losses.json').read_text())
    expected_q1 = {r['game'] for r in losses if r['our_code'] == 'main' and r['bucket'] == 'Q1'}
    assert {r['game'] for r in hunt if r['group'] == 'Q1'} == expected_q1
    assert len({r['game'] for r in validation}) == len(validation) == len(rows)
    for rec in validation + hunt + growth:
        assert rec['final_matches_rows'] and rec['winner_matches_rows']
        assert rec['final_reconstructed'] == rows[rec['game']]['final']
    expected_never = {r['game'] for r in rows.values() if (r['curves']['100']['us']['alive'] <= 6
                      if r['curves']['100'] is not None else r['final']['us']['alive'] == 0)}
    assert {r['game'] for r in growth if r['group'] == 'never_grew'} == expected_never
    for r in growth:
        if rows[r['game']]['curves']['50'] is not None:
            assert all(r['pearls_through50'][s] == rows[r['game']]['curves']['50'][s]['pearls'] for s in ('us', 'them'))
    length_bins = [('전체', None), ('≤4', lambda l: l <= 4), ('5–12', lambda l: 5 <= l <= 12), ('≥13', lambda l: l >= 13)]
    hs, gs = {}, {}
    for group in ('Q1', 'reference'):
        sel = [r for r in hunt if r['group'] == group]
        hs[group] = {label: hunt_stats(sel, f) for label, f in length_bins}
        assert sum(hs[group][label]['queen_turns'] for label, _ in length_bins[1:]) == hs[group]['전체']['queen_turns']
        for r in sel:
            assert all(t[2] >= t[3] and t[1] > 0 and t[0] > 100 for t in r['turns'])
            assert 'closest_short_window' in r and 'adjacent_steps_window' in r
            assert r['adjacent_steps'] >= r['adjacent_steps_window']
            assert all(t[3] <= t[6] and (t[3] == 0 or (t[4] is not None and t[4] <= 12)) for t in r['turns'])
            if r['closest_short_window'] is not None:
                assert r['closest_short'] is not None and r['closest_short'] <= r['closest_short_window']
            if r['group'] == 'reference':
                assert r['our_queen_death']['event'] < r['queen_death']['event']
                assert r['our_queen_death'].get('simultaneous_with') != r['queen_death']['id']
    for subset in ('all', 'two_a_side'):
        gs[subset] = {group: growth_stats([r for r in growth if r['group'] == group and
                      (subset == 'all' or r['two_a_side'])]) for group in ('never_grew', 'grew')}
    lines = [
        '# 기보 집계', '',
        '| 군 | 상대 여왕 길이 | 경기 | 여왕 턴 | 12걸음 내 머리 평균 / 짧은 머리 평균 | 시야 나이 0–20 / 21–60 / >60 / 미관측 (%) | 21–60 턴 | 그 안의 짧은 용 거리 ≤20 / 21–40 / >40 / 미측정 (%) |',
        '|---|---|---:|---:|---:|---|---:|---|',
    ]
    for group in ('Q1', 'reference'):
        for label, _ in length_bins:
            s = hs[group][label]
            n, m = s['queen_turns'], s['mid_age_turns']
            age = ' / '.join(pct(s['sightings'].get(k, 0), n) for k in ('0_20', '21_60', 'gt60', 'never'))
            dd = s['mid_age_distances']
            distance = ' / '.join(pct(dd.get(k, 0), m) for k in ('le20', '21_40', 'gt40'))
            distance += ' / ' + pct(dd.get('no_short', 0) + dd.get('unreachable', 0), m)
            lines.append(f"| {group} | {label} | {s['games']} | {n} | {avg(s['heads_within12'], n)} / {avg(s['short_heads_within12'], n)} | {age} | {m} | {distance} |")
    lines += ['', '| 항목 | 전체: 성장 없음 | 전체: 성장 | 시작 2마리씩: 성장 없음 | 시작 2마리씩: 성장 |', '|---|---:|---:|---:|---:|']
    columns = [gs[subset][group] for subset in ('all', 'two_a_side') for group in ('never_grew', 'grew')]
    metrics = [
        ('경기 / 지도', lambda s: f"{s['games']} / {s['layouts']}"),
        ('r100 전 우리 전멸 경기', lambda s: str(s['gone_before100'])),
        ('먹지 않은 턴', lambda s: str(s['no_meal'].get('turns', 0))),
        ('알려진 진주 없음', lambda s: count_share(s, ['known_none'])),
        ('알려진 진주 거리 ≤6', lambda s: count_share(s, ['known_le6'])),
        ('알려진 진주 거리 7–15', lambda s: count_share(s, ['known_7_15'])),
        ('알려진 진주 거리 >15·도달 불가', lambda s: count_share(s, ['known_gt15', 'known_unreachable'])),
        ('위 항목 중 도달 불가', lambda s: count_share(s, ['known_unreachable'])),
        ('첫 걸음이 중앙 거리 감소', lambda s: count_share(s, ['centre_reduce'])),
        ('성공한 걸음 없음', lambda s: count_share(s, ['no_successful_step'])),
        ('2걸음 이상 이동 턴', lambda s: count_share(s, ['multi_step_turns'])),
        ('적 머리 시야 안', lambda s: count_share(s, ['enemy_in_view'])),
        ('첫 섭취 라운드 중앙값 [최소–최대]; 끝까지 없음', lambda s: round_summary(s['first_meal'])),
        ('r50까지 우리 진주 합계 / 경기 평균', lambda s: f"{s['pearls50']['us']} / {avg(s['pearls50']['us'], s['games'])}"),
        ('r50까지 상대 진주 합계 / 경기 평균', lambda s: f"{s['pearls50']['them']} / {avg(s['pearls50']['them'], s['games'])}"),
        ('첫 분열 라운드 중앙값 [최소–최대]; 끝까지 없음', lambda s: round_summary(s['first_split'])),
    ]
    for label, fn in metrics:
        lines.append('| ' + label + ' | ' + ' | '.join(fn(s) for s in columns) + ' |')
    early = sum(r['curves']['100'] is None and r['final']['us']['alive'] > 0 for r in rows.values())
    omitted = len(rows) - len(growth) - early
    same_round_refs = sum(r['our_queen_death']['round'] == r['queen_death']['round'] for r in hunt if r['group'] == 'reference')
    lines += [
        '', '정의:', '',
        '- 입력은 `our_code == "main"`만 사용. Q1은 losses.json의 Q1 버킷 전부. reference는 우리 여왕 사망 사건 뒤 상대 여왕 사망 사건이 있는 경기이며, 두 여왕의 같은 머리 충돌은 동시 사망으로 제외.',
        f'- reference 중 같은 라운드의 서로 다른 사망 사건: {same_round_refs}경기. 길이별 경기 수는 해당 길이의 대상 턴이 1개 이상인 경기이며, 전체 경기 수에는 대상 턴 0개도 포함.',
        '- 여왕 턴은 r101 이후, 우리 여왕은 사망·상대 여왕은 생존한 상대 여왕 turnStart. 가까운 머리와 짧은 용 거리·상대 길이는 이 순간 상태. 짧은 용은 길이 ≤4.',
        '- 경로는 경계 순환·벽·포털을 반영한 열린 간선 최단 걸음, 몸 무시. 시야는 경계 순환 7×7이며 벽은 가리지 않고 포털 너머로 확장하지 않음.',
        '- 여왕 관측은 우리 용 turnStart의 실제 위치에서만 갱신하며 r0부터 추적. 나이는 라운드 차이. 가장 최근 관측자는 이후 죽었어도 포함. 표의 비율은 턴 가중.',
        '- 게임별 closest_short·adjacent_steps는 상대 여왕이 살아 있는 경기 전체. 최접근은 모든 라운드 시작·턴 시작·이동·분열·사망 후 상태; 인접은 우리 머리가 성공적으로 열린 간선 1걸음 이웃에 들어간 이동 수(포털 포함). *_window는 위 r101 이후 구간만 따로 수록.',
        '- 성장 없음: r100 종료 시 우리 생존 수 ≤6 또는 r100 전 우리 전멸. 성장: 같은 map_key(버전 포함)에서 r100 종료 시 >6. 시작 2마리씩은 양쪽 초기 DRAGON 수가 각각 2.',
        f'- r100 전에 종료했으나 우리 용이 생존한 {early}경기와 성장 없음 군의 지도에 속하지 않는 {omitted}경기는 성장 비교에서 제외. main {len(rows)}경기 모두 최종 상태·승패 재구성 대조.',
        '- 성장 턴은 r0–100 포함, 우리 용의 턴 전체에서 진주 제거/섭취 0개인 턴(분열·사망 포함). 진주 출처는 자연 생성·사망 낙하 모두 포함. r50 섭취도 r0–50 포함. 첫 섭취·분열은 경기 전체.',
        '- 진주 기억은 같은 용이 자신의 turnStart 시야에서 본 살아 있는 진주 생성 사건, 나이 ≤25. 누가 먹든 해당 생성 사건 제거 시 만료. 부모 번호는 기억 유지, 새 번호는 빈 기억. 공유·소나·분열 상속은 포함하지 않음.',
        '- 중앙은 지도 좌표의 기하학적 중앙에 가장 가까운 1/2/4개 타일. 첫 성공 이동의 경로 거리가 턴 시작보다 작으면 감소. 다중 이동은 첫 걸음만 표에 사용(마지막 걸음 대비 감소는 JSON에도 별도 수록). 걸음 없는 턴은 감소 0.',
        '- 성장 표의 턴 항목은 수 (먹지 않은 모든 턴 대비 %). 첫 사건 통계는 사건이 있는 경기만 사용하며 없음 수를 함께 표기. JSON에는 게임별 집계와 결합 분포를 수록.',
        '', '측정 한계:', '',
        '- 기보로 봇 내부의 실제 기억·의사결정은 측정 불가. 시야로 재구성한 개인 관측만 사용. 실패한 충돌 걸음은 성공한 위치 이동이 없어 중앙 감소·인접 이동에 포함하지 않음.',
        '- 짧은 용이 없거나 여왕에서 도달 가능한 짧은 용이 없으면 최단 거리 null·표에서 미측정. 진주는 알려졌지만 경로가 없으면 >15에 포함하고 도달 불가도 별도 표시.',
        '- 여왕 사망 JSON의 length / other_length는 여왕과 충돌 대상 길이. 벽·자기 몸·무효 행동에는 다른 용 길이가 없어 null. 양쪽 여왕 길이도 queen_lengths_before에 기록. 생존 여왕은 사망 정보 null.',
    ]
    assert len(lines) <= 60, len(lines)
    (OUT / 'summary.md').write_text('\n'.join(lines) + '\n')
    (OUT / 'aggregate.json').write_text(json.dumps(dict(hunt=hs, growth=gs), ensure_ascii=False, indent=2) + '\n')
    assert len((OUT / 'summary.md').read_text().splitlines()) <= 60
    assert all((OUT / name).is_file() for name in ('summary.md', 'hunt.json', 'growth.json', 'count_replays.py', 'report_counts.py'))
    if '--prepare' in sys.argv:
        print(f'Validated {len(validation)} games; summary prepared ({len(lines)} lines); last.txt not written.')
        return
    last = [datetime.now().astimezone().isoformat(timespec='seconds'),
            f'Q1(main): {len(expected_q1)} games = losses.json Q1(main) bucket; exact game-id set matched.',
            f'Final standings and winner: {len(validation)}/{len(rows)} main replays match rows.jsonl; all hunt/growth games included; 0 mismatches.',
            f'Hunt: {len(hunt)} games; growth: {len(growth)} games ({len(expected_never)} never grew); summary: {len(lines)} lines.',
            'Offline only; existing inputs unchanged (SHA-256 checked); outputs only in counts/; this file written LAST.']
    (OUT / 'last.txt').write_text('\n'.join(last) + '\n')
    print('\n'.join(last))


def count_share(s, keys):
    n = sum(s['no_meal'].get(k, 0) for k in keys)
    return f"{n} ({pct(n, s['no_meal'].get('turns', 0))})"


if __name__ == '__main__':
    main()
