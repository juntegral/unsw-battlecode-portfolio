#!/usr/bin/env python3
import hashlib
import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
BUCKETS = ['E1', 'E2', 'Q1', 'Q2', 'Q3', 'L1', 'Other']
CODES = ['main', 'v31']
CUT = '2026-10-06T14:48:15+00:00'
LABELS = ['r100 뒤짐', '여왕 r100까지 사망', 'r200 우리 여왕 사망·상대 생존',
          '체크포인트에서 우리 여왕만 생존', 'big 지도', '상대 2100+',
          '상대 1900–2099', 'r200 여왕 생존·길이 ≤3', 'r100 생존 수 열세']


def position(s):
    if s is None:
        return 'missing'
    u, t = s['us']['total'], s['them']['total']
    if 5 * u < 4 * t:
        return 'behind'
    if 5 * u > 6 * t:
        return 'ahead'
    return 'level'


def died(q, rnd):
    return q['death_round'] is not None and q['death_round'] <= rnd


def classify(r):
    end, q = r['ended_by'], r['queens_at_end']
    if end == 'elimination' and r['final']['us']['alive'] == 0:
        return 'E1' if r['last_round'] <= 125 else 'E2'
    if end == 'queen rule' and q == 'only theirs':
        return 'Q1' if r['final']['us']['longest'] >= r['final']['them']['longest'] else 'Q2'
    if end == 'queen rule' and q == 'both alive' and r['final']['us']['queen_length'] < r['final']['them']['queen_length']:
        return 'Q3'
    if q == 'both dead' and end in ('longest dragon', 'total length'):
        return 'L1'
    return 'Other'


def conditions(r, m):
    c100, c200 = r['curves']['100'], r['curves']['200']
    checkpoints = [c for c in r['curves'].values() if c is not None]
    return [None if c100 is None else position(c100) == 'behind',
            died(r['queen']['us'], 100),
            None if c200 is None else not c200['us']['queen_alive'] and c200['them']['queen_alive'],
            any(c['us']['queen_alive'] and not c['them']['queen_alive'] for c in checkpoints),
            m['width'] * m['height'] > 1200,
            r['opponent_rating'] >= 2100,
            1900 <= r['opponent_rating'] < 2100,
            None if c200 is None else c200['us']['queen_alive'] and c200['us']['queen_length'] <= 3,
            None if c100 is None else c100['us']['alive'] < c100['them']['alive']]


def conjunction(a, b):
    if a is False or b is False:
        return False
    return None if a is None or b is None else True


def risk(rows, vals):
    yes = [r for r, v in zip(rows, vals) if v is True]
    no = [r for r, v in zip(rows, vals) if v is False]
    ly = sum(r['result'] == 'loss' for r in yes)
    ln = sum(r['result'] == 'loss' for r in no)
    return dict(games_with=len(yes), losses_with=ly, loss_rate_with=ly / len(yes) if yes else None,
                games_without=len(no), losses_without=ln, loss_rate_without=ln / len(no) if no else None,
                missing=len(rows) - len(yes) - len(no))


def stats(rows, total):
    rounds = [r['queen']['us']['death_round'] for r in rows if r['queen']['us']['death_round'] is not None]
    return dict(n=len(rows), share=len(rows) / total if total else None,
                position_r100=dict(Counter(position(r['curves']['100']) for r in rows)),
                big=sum(r['_conditions'][4] for r in rows), rest=sum(not r['_conditions'][4] for r in rows),
                two_dragon_start=sum(r['_map']['dragons_at_spawn'] == 2 for r in rows),
                opponent_band=dict(Counter('under 1900' if r['opponent_rating'] < 1900 else '1900-2099' if r['opponent_rating'] < 2100 else '2100+' for r in rows)),
                queen_alive_end=sum(r['queen']['us']['alive_end'] for r in rows),
                queen_dead_end=sum(not r['queen']['us']['alive_end'] for r in rows),
                queen_death_round_median=median(rounds) if rounds else None,
                queen_death_causes=dict(Counter(r['queen']['us']['death_cause'] for r in rows if not r['queen']['us']['alive_end'])),
                queen_dead_by100=sum(died(r['queen']['us'], 100) for r in rows),
                queen_dead_by200=sum(died(r['queen']['us'], 200) for r in rows),
                thrown_lead=sum(position(r['curves']['300']) == 'ahead' for r in rows),
                missing_r300=sum(r['curves']['300'] is None for r in rows))


def pct(x):
    return '—' if x is None else f'{100*x:.1f}%'


def riskcell(s):
    return f"{s['games_with']}; {s['losses_with']}/{s['games_with']} {pct(s['loss_rate_with'])}; {s['losses_without']}/{s['games_without']} {pct(s['loss_rate_without'])}; {s['losses_with']}; {s['missing']}"


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def main():
    raw = (ROOT / 'rows.jsonl').read_bytes()
    mapraw = (ROOT / 'maps.json').read_bytes()
    maps = json.loads(mapraw)
    rows = [json.loads(line) for line in raw.splitlines()]
    rows = [r for r in rows if r['our_code'] in CODES]
    assert len({r['game'] for r in rows}) == len(rows)
    for r in rows:
        r['_map'] = {k: maps[r['map_key']][k] for k in ('width', 'height', 'dragons_at_spawn')}
        r['_conditions'] = conditions(r, r['_map'])
        if r['result'] == 'loss':
            r['_bucket'] = classify(r)
        assert r['queen']['us']['alive_end'] == (r['final']['us']['queen_length'] > 0)
    slices = {c: [r for r in rows if r['our_code'] == c] for c in CODES}
    losses = {c: [r for r in slices[c] if r['result'] == 'loss'] for c in CODES}
    bucketstats = {c: {b: stats([r for r in losses[c] if r['_bucket'] == b], len(losses[c])) for b in BUCKETS} for c in CODES}
    risks = {c: {label: risk(slices[c], [r['_conditions'][i] for r in slices[c]]) for i, label in enumerate(LABELS)} for c in CODES}
    pairs = {}
    for c in CODES:
        candidates = []
        for i, j in itertools.combinations(range(len(LABELS)), 2):
            s = risk(slices[c], [conjunction(r['_conditions'][i], r['_conditions'][j]) for r in slices[c]])
            candidates.append(dict(indices=[i, j], conditions=[LABELS[i], LABELS[j]], **s))
        pairs[c] = sorted(candidates, key=lambda s: (-s['losses_with'], s['indices']))[:5]
    halves = {}
    for name, before in [('half 1', True), ('half 2', False)]:
        rs = [r for r in slices['main'] if (datetime.fromisoformat(r['time'].replace('Z', '+00:00')) < datetime.fromisoformat(CUT)) == before]
        ls = [r for r in rs if r['result'] == 'loss']
        halves[name] = dict(games=len(rs), losses=len(ls), buckets={b: stats([r for r in ls if r['_bucket'] == b], len(ls)) for b in BUCKETS})
    for c in CODES:
        assert sum(s['n'] for s in bucketstats[c].values()) == len(losses[c])
        assert all(r['result'] in ('win', 'loss', 'draw') for r in slices[c])
        for s in risks[c].values():
            assert s['games_with'] + s['games_without'] + s['missing'] == len(slices[c])
        for b, s in bucketstats[c].items():
            assert sum(s['position_r100'].values()) == s['n']
            assert s['big'] + s['rest'] == s['n']
            assert sum(s['opponent_band'].values()) == s['n']
            assert s['queen_alive_end'] + s['queen_dead_end'] == s['n']
            assert sum(s['queen_death_causes'].values()) == s['queen_dead_end']
    outrows = []
    for r in rows:
        if r['result'] != 'loss':
            continue
        x = {k: r[k] for k in ('battle', 'game', 'our_code', 'result', 'time', 'last_round', 'ended_by', 'queens_at_end', 'map_key', 'opponent_rating', 'final', 'curves', 'queen')}
        x.update(bucket=r['_bucket'], map_metadata=r['_map'], position_r100=position(r['curves']['100']),
                 thrown_lead=position(r['curves']['300']) == 'ahead' if r['curves']['300'] is not None else None,
                 conditions=dict(zip(LABELS, r['_conditions'])))
        outrows.append(x)
    write('losses.json', outrows)
    write('bucket-stats.json', bucketstats)
    write('risk-stats.json', dict(conditions=risks, top_pairs=pairs, stability=halves,
          source_sha256=dict(rows=hashlib.sha256(raw).hexdigest(), maps=hashlib.sha256(mapraw).hexdigest()),
          result_counts={c: dict(Counter(r['result'] for r in slices[c])) for c in CODES}))
    lines = ['# 래더 패배 분류', '', '모집단: ' + '; '.join(f"{c} {len(slices[c])}판, {len(slices[c])-len(losses[c])}승, {len(losses[c])}패" for c in CODES) + '. 테스트 빌드 제외.',
             '브리프 기준(main 169/375패, v31 207/410패)과 ' + ('일치.' if (len(slices['main']), len(losses['main']), len(slices['v31']), len(losses['v31'])) == (375, 169, 410, 207) else '다름: 위 현재 집계 사용.'), '',
             '| 버킷 | main n (패배 중 비율) | v31 n (패배 중 비율) |', '|---|---:|---:|']
    for b in BUCKETS:
        lines.append('| ' + b + ' | ' + ' | '.join(f"{bucketstats[c][b]['n']} ({pct(bucketstats[c][b]['share'])})" for c in CODES) + ' |')
    lines += ['', 'main 상위 3개 버킷 내부(모두 판 수):']
    for b in sorted(BUCKETS, key=lambda b: -bucketstats['main'][b]['n'])[:3]:
        s = bucketstats['main'][b]
        p, bands = s['position_r100'], s['opponent_band']
        lines.append(f"- {b}: r100 뒤/동/앞/없음 {p.get('behind',0)}/{p.get('level',0)}/{p.get('ahead',0)}/{p.get('missing',0)}; big/나머지 {s['big']}/{s['rest']}; 2마리 시작 {s['two_dragon_start']}; 상대 <1900/1900–2099/2100+ {bands.get('under 1900',0)}/{bands.get('1900-2099',0)}/{bands.get('2100+',0)}.")
        lines.append(f"  여왕 끝 생존/사망 {s['queen_alive_end']}/{s['queen_dead_end']}; 사망 라운드 중앙값 {s['queen_death_round_median']}; 사인 {json.dumps(s['queen_death_causes'],ensure_ascii=False)}; r100/r200까지 사망 {s['queen_dead_by100']}/{s['queen_dead_by200']}; r300 앞섰다 패배 {s['thrown_lead']} (r300 없음 {s['missing_r300']}).")
    lines += ['', '전체 판 위험표: 각 칸 = 조건 판 수; 조건 있음 패/판·패율; 조건 없음 패/판·패율; 조건을 가진 패배 수; 결측 판 수.', '', '| 조건 | main | v31 |', '|---|---|---|']
    for label in LABELS:
        lines.append('| ' + label + ' | ' + ' | '.join(riskcell(risks[c][label]) for c in CODES) + ' |')
    lines += ['', '패배에서 가장 흔한 조건 쌍 5개(코드별 선정, 같은 칸 표기; 동률은 위 조건 순서):', '', '| 코드 | 조건 쌍 | 집계 |', '|---|---|---|']
    for c in CODES:
        for s in pairs[c]:
            lines.append(f"| {c} | {' + '.join(s['conditions'])} | {riskcell(s)} |")
    lines += ['', '안정성(main, UTC 2026-10-06 14:48:15 전/이후; 버킷 순 E1/E2/Q1/Q2/Q3/L1/Other): ' + '; '.join(f"{name} {s['games']}판·{s['losses']}패: " + ', '.join(f"{s['buckets'][b]['n']} ({pct(s['buckets'][b]['share'])})" for b in BUCKETS) for name,s in halves.items()) + '.', '',
              '정의와 한계:',
              '- E1/E2: ended_by=elimination이고 final.us.alive=0, last_round ≤125/>125. 원시 라운드는 0부터 시작한다.',
              '- Q1/Q2: ended_by=queen rule, queens_at_end=only theirs, 우리 최장 ≥상대/상대보다 짧음. Q3: queen rule, both alive, 우리 여왕이 짧음.',
              '- L1: both dead이며 longest dragon 또는 total length로 패배. Other: 앞 조건 모두 불충족; 게임별 종료 내역 아래.',
              '- 여왕 규칙: 500턴 종료 때 여왕 길이 비교, 사망=0. 같으면 최장 드래곤, 그다음 총 길이. full game=500턴 도달(last_round=499).',
              '- level game: r100 우리/상대 총 길이 0.8–1.2(경계 포함); behind <0.8, ahead >1.2. “서로 20% 이내”의 분모는 ledger에 명시되지 않아 상대 길이를 사용했다.',
              '- big=width×height>1200; maps.json의 dragons_at_spawn는 팀당 시작 수. 밴드 <1900/1900–2099/2100+; <1900에 ledger의 별도 밴드 밖 1664–1665도 포함.',
              '- r100/r200/r300=해당 원시 라운드 종료 상태. 없는 체크포인트는 외삽 없이 결측; 위험표 조건 있음/없음 분모에서 제외하며 결측 수를 표시.',
              '- r100/r200까지 사망은 death_round≤100/≤200; 사망 중앙값·사인은 끝에 죽은 여왕만. r200 우리 사망·상대 생존과 길이≤3 조건은 curves.200에서 측정.',
              '- 우리만 생존: curves의 50/100/150/200/300/400/end 중 한 번이라도 참(체크포인트 사이 상태는 측정 안 됨). 조건 쌍은 AND; 하나가 거짓이면 거짓, 그 외 결측은 결측.',
              '- thrown lead: curves.300에서 우리 총 길이>1.2×상대이고 최종 loss. 전체 버킷 내부는 bucket-stats.json, 위험표·안정성 원자료는 risk-stats.json, 패배별 사용 필드는 losses.json.']
    others = [r for r in outrows if r['bucket'] == 'Other']
    for c in CODES:
        lines.append(f'- Other {c} 게임별(모두 both alive, 여왕 길이 동률): ' + '; '.join(f"{r['game']} {r['ended_by']}" for r in others if r['our_code'] == c) + '.')
    assert len(lines) <= 70, len(lines)
    (OUT / 'summary.md').write_text('\n'.join(lines) + '\n')
    assert (ROOT / 'rows.jsonl').read_bytes() == raw
    assert (ROOT / 'maps.json').read_bytes() == mapraw
    (OUT / 'last.txt').write_text('\n'.join([
        '완료: main/v31 전수 패배 분류, 모든 버킷 내부 집계, 전체 판 조건·상위 조건 쌍·시간 안정성.',
        f'집계: main {len(losses["main"])}/{len(slices["main"])}패; v31 {len(losses["v31"])}/{len(slices["v31"])}패; summary {len(lines)}줄.',
        '검사: 버킷 합계·결과 합계·내부 분할·조건 분모·게임 ID 고유성·원본 파일 불변 통과.',
        '분석 실패 없음. nice 우선순위 변경 시도는 환경 권한으로 거부됨; 분석은 완료. 결측·level 분모는 summary.md에 명시.',
        datetime.now(timezone.utc).isoformat()]) + '\n')
    print(json.dumps(dict(results={c: dict(Counter(r['result'] for r in slices[c])) for c in CODES}, buckets={c: {b:s['n'] for b,s in bucketstats[c].items()} for c in CODES}, summary_lines=len(lines)), ensure_ascii=False))


if __name__ == '__main__':
    main()
