#!/usr/bin/env python3
"""Aggregate offline dossier rows; completion marker is the final write."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SIDES = ('us', 'them')
LOW = ('Islands #1', 'Stripes #1', 'Australia #1', 'Tower Defense #1')
CAUSES = ('head-on mover', 'head-on hit', 'wall', 'own body', 'another body', 'no action',
          'unpaid sprint', 'illegal split', 'timeout')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mean(values):
    values = [v for v in values if v is not None]
    return dict(value=sum(values)/len(values) if values else None, n=len(values))

def rate(pairs):
    n, d = sum(x[0] for x in pairs), sum(x[1] for x in pairs)
    return dict(value=n/d if d else None, numerator=n, denominator=d)

def nfmt(v):
    if v is None:
        return 'NA'
    return f'{v:.2f}'

def fmt(stat, pct=False):
    return nfmt(None if stat['value'] is None else stat['value']*(100 if pct else 1))

def queen_dead(r, hi):
    death = r['queen']['death']
    if death is not None:
        return int(death['round'] <= hi)
    return 0 if r['last_round'] >= hi else None

def ab(sides):
    def side(rs):
        a = {}
        a['pearls50'] = mean([r['ranges']['0-50']['pearls_eaten'] for r in rs])
        a['pearls100'] = mean([r['ranges']['0-100']['pearls_eaten'] for r in rs])
        a['dragons100'] = mean([(r['ranges']['0-100']['end_state'] or {}).get('alive') for r in rs])
        for name, numerator, denominator in (('dither', 'dither', 'no_view_pearl_moved'),
            ('keeps', 'keeps', 'keeps_eligible'), ('hot', 'hot_turns', 'turns')):
            a[name] = rate([(r['ranges']['0-100'][numerator], r['ranges']['0-100'][denominator]) for r in rs])
        a['seen100'] = mean([r['ranges']['0-100']['seen_share_end'] for r in rs])
        a['portal_game'] = mean([r['portal_steps_game'] for r in rs])
        a['head_on_net100'] = mean([r['ranges']['0-100']['head_on_net_length_lost'] for r in rs])
        a['queen_dead100'] = mean([queen_dead(r, 100) for r in rs])
        return a
    return {s: side(sides[s]) for s in SIDES}

def detailed(rs, interval):
    lo, hi = map(int, interval.split('-'))
    cs = [r['ranges'][interval] for r in rs]
    a = {}
    for name, key in [('pearls', 'pearls_eaten'), ('splits', 'splits'), ('portal_steps', 'portal_steps'),
                     ('head_on_trades', 'cross_head_on_trades'), ('head_on_lost', 'head_on_length_lost'),
                     ('head_on_net_lost', 'head_on_net_length_lost'), ('head_on_same_team', 'same_team_head_on_trades'),
                     ('births', 'births'), ('portal_room_births', 'portal_room_births'),
                     ('portal_required_births', 'portal_required_births')]:
        a[name] = mean([c[key] for c in cs])
    for key in ('alive', 'total'):
        a['end_'+key] = mean([(c['end_state'] or {}).get(key) for c in cs])
    for cause in CAUSES:
        a['death_'+cause.replace(' ', '_')] = mean([c['deaths'][cause] for c in cs])
    a['seen_end%'] = mean([None if c['seen_share_end'] is None else c['seen_share_end']*100 for c in cs])
    for name, num, den in [('dither%', 'dither', 'no_view_pearl_moved'),
                          ('keeps%', 'keeps', 'keeps_eligible'),
                          ('hot%', 'hot_turns', 'turns'),
                          ('adj_pearl_miss%', 'adjacent_pearl_missed', 'adjacent_pearl_turns'),
                          ('birth_near6%', 'near6_births', 'births'),
                          ('natural_birth_near6%', 'natural_near6', 'natural_births')]:
        a[name] = rate([(c[num], c[den]) for c in cs])
        if a[name]['value'] is not None:
            a[name]['value'] *= 100
    for name, key in [('distinct20', 'distinct_per_dragon_20'),
                      ('no_pearl_distinct20', 'no_view_pearl_distinct_per_dragon_20')]:
        a[name] = rate([(c[key]['sum'], c[key]['n']) for c in cs])
    own = rs[0]['relation'] if rs else 'us'
    for label, count, denominator in [('birth_ate%', 'cohort_eaten', 'births'),
                                      ('natural_birth_ate%', 'natural_eaten', 'natural_births'),
                                      ('portal_room_ate%', 'portal_room_eaten', 'portal_room_births'),
                                      ('portal_required_ate%', 'portal_required_eaten', 'portal_required_births')]:
        a[label] = rate([(c[count][own], c[denominator]) for c in cs])
        if a[label]['value'] is not None:
            a[label]['value'] *= 100
    for label, count in [('portal_room_eaten', 'portal_room_eaten'), ('portal_required_eaten', 'portal_required_eaten')]:
        a[label] = mean([c[count][own] for c in cs])
    a['birth_wait'] = rate([(c['cohort_wait']['sum'], c['cohort_wait']['n']) for c in cs])
    a['portal_steps_game'] = mean([r['portal_steps_game'] for r in rs])
    a['portal_room_births_game'] = mean([r['portal_births_game']['rooms'] for r in rs])
    a['portal_room_eaten_game'] = mean([r['portal_births_game']['room_eaten'][own] for r in rs])
    a['portal_required_births_game'] = mean([r['portal_births_game']['required'] for r in rs])
    a['portal_required_eaten_game'] = mean([r['portal_births_game']['required_eaten'][own] for r in rs])
    contacts = [r['first_enemy_head_in_view'] for r in rs]
    a['first_contact_round'] = mean([v if v is not None and lo <= v <= hi else None for v in contacts])
    a['first_contact_in_window%'] = mean([100*int(v is not None and lo <= v <= hi) for v in contacts])
    deaths = [r['queen']['death'] for r in rs]
    a['queen_death_round'] = mean([d['round'] if d is not None and lo <= d['round'] <= hi else None for d in deaths])
    a['queen_death_in_window%'] = mean([100*int(d is not None and lo <= d['round'] <= hi) for d in deaths])
    a['queen_dead_end%'] = mean([None if queen_dead(r, hi) is None else 100*queen_dead(r, hi) for r in rs])
    for cause in CAUSES:
        a['queen_death_'+cause.replace(' ', '_')] = mean([int(d is not None and lo <= d['round'] <= hi and d['cause'] == cause) for d in deaths])
    for rnd in (50, 100, 200):
        if lo <= rnd <= hi:
            a['queen_length'+str(rnd)] = mean([r['queen']['length'][str(rnd)] for r in rs])
    for rnd in (50, 100):
        if lo <= rnd <= hi:
            a['enemy_half'+str(rnd)+'%'] = rate([(r['heads_enemy_half'][str(rnd)]['n'], r['heads_enemy_half'][str(rnd)]['d'])
                                               for r in rs if r['heads_enemy_half'][str(rnd)] is not None])
            if a['enemy_half'+str(rnd)+'%']['value'] is not None:
                a['enemy_half'+str(rnd)+'%']['value'] *= 100
    return a

def within(rs):
    result = {}
    for outcome in ('win', 'loss'):
        selected = [r for r in rs if r['our_result'] == outcome]
        result[outcome] = dict(games=len(selected),
             dither=mean([r['ranges']['0-100']['dither_share'] for r in selected]),
             seen100=mean([r['ranges']['0-100']['seen_share_end'] for r in selected]),
             pearls50=mean([r['ranges']['0-50']['pearls_eaten'] for r in selected]))
    return result

def main():
    assert not (OUT / 'last.txt').exists(), 'Completion marker already exists.'
    rows = [json.loads(line) for line in (OUT / 'per-game.jsonl').read_text().splitlines()]
    frozen = json.loads((OUT / 'input-snapshot.json').read_text())
    validation = json.loads((OUT / 'validation.json').read_text())
    source = {r['game']: r for r in frozen['rows']}
    assert len(rows) == 2*len(source)
    indexed = {s: {r['game']: r for r in rows if r['relation'] == s} for s in SIDES}
    assert all(set(indexed[s]) == set(source) for s in SIDES)
    keys = sorted({r['layout_key'] for r in rows})
    assert len(keys) == 19 and all(key in keys for key in LOW)
    def select(ids):
        return {s: [indexed[s][i] for i in ids] for s in SIDES}
    a, b, c, d = [], [], [], []
    for key in keys:
        ids = [i for i, r in source.items() if r['map_key'] == key]
        sides = select(ids)
        a.append(dict(layout=key, games=len(ids), wins=sum(source[i]['result'] == 'win' for i in ids),
                      measures=ab(sides)))
        d.append(dict(layout=key, **within(sides['us'])))
    for label, lo, hi in (('<1900', -math.inf, 1900), ('1900-2099', 1900, 2100), ('2100+', 2100, math.inf)):
        ids = [i for i, r in source.items() if r['opponent_rating'] is not None and lo <= r['opponent_rating'] < hi]
        b.append(dict(rating=label, games=len(ids), wins=sum(source[i]['result'] == 'win' for i in ids), measures=ab(select(ids))))
    assert sum(r['games'] for r in b) == len(source)
    others = [i for i, r in source.items() if r['map_key'] not in LOW]
    assert len({source[i]['map_key'] for i in others}) == 15
    for key in LOW:
        ids = [i for i, r in source.items() if r['map_key'] == key]
        for interval in ('0-100', '101-300'):
            mine = {s: detailed(select(ids)[s], interval) for s in SIDES}
            ref = {s: detailed(select(others)[s], interval) for s in SIDES}
            metrics = []
            for name in mine['us']:
                u, t = mine['us'][name]['value'], mine['them'][name]['value']
                gap = None if u is None or t is None else abs(u-t)/max(abs(u), abs(t)) if u or t else 0
                metrics.append(dict(measure=name, ours=mine['us'][name], theirs=mine['them'][name],
                                    other15_ours=ref['us'][name], other15_theirs=ref['them'][name],
                                    gap=u-t if u is not None and t is not None else None,
                                    relative_absolute_gap=gap))
            metrics.sort(key=lambda m: (m['relative_absolute_gap'] is None, -(m['relative_absolute_gap'] or 0), m['measure']))
            c.append(dict(layout=key, interval=interval, games=len(ids), other15_games=len(others), measures=metrics))
    centred = []
    for key in keys:
        pairs = [(r['ranges']['0-100']['dither_share'], r['ranges']['0-100']['pearls_eaten'])
                 for r in indexed['us'].values() if r['layout_key'] == key and r['ranges']['0-100']['dither_share'] is not None]
        if pairs:
            mx, my = sum(x for x, y in pairs)/len(pairs), sum(y for x, y in pairs)/len(pairs)
            centred.extend((x-mx, y-my) for x, y in pairs)
    xy = sum(x*y for x, y in centred)
    xx, yy = sum(x*x for x, y in centred), sum(y*y for x, y in centred)
    correlation = dict(n=len(centred), layouts=len(keys), pearson=xy/math.sqrt(xx*yy) if xx and yy else None,
                       sum_xy=xy, sum_x2=xx, sum_y2=yy)
    cols = ('pearls50', 'pearls100', 'dragons100', 'dither', 'keeps', 'seen100', 'hot', 'portal_game', 'head_on_net100', 'queen_dead100')
    pct = {'dither', 'keeps', 'seen100', 'hot', 'queen_dead100'}
    lines = ['# 래더 행동 집계', '', '## A. 레이아웃: 우리/상대', '',
             '| layout | 경기 | 우리 승 | P50 | P100 | D100 | dither% | keep% | seen100% | hot% | portal/game | Hnet100 | Qdead100% |',
             '|---|---:|---:|---|---|---|---|---|---|---|---|---|---|']
    def abline(item, label):
        pairs = ['/'.join(fmt(item['measures'][s][col], col in pct) for s in SIDES) for col in cols]
        return '| '+label+' | '+str(item['games'])+' | '+str(item['wins'])+' | '+' | '.join(pairs)+' |'
    lines.extend(abline(item, item['layout']) for item in a)
    lines += ['', '## B. 상대 레이팅: 우리/상대', '',
              '| rating | 경기 | 우리 승 | P50 | P100 | D100 | dither% | keep% | seen100% | hot% | portal/game | Hnet100 | Qdead100% |',
              '|---|---:|---:|---|---|---|---|---|---|---|---|---|---|']
    lines.extend(abline(item, item['rating']) for item in b)
    lines += ['', '## C. 구간별 모든 지표: 상대차 크기 내림차순', '',
              '| layout | 구간 | 경기/기타15경기 | 지표: 우리/상대 [기타15 우리/상대]; 상대차% |',
              '|---|---|---:|---|']
    for item in c:
        entries = []
        for m in item['measures']:
            entries.append(m['measure']+': '+fmt(m['ours'])+'/'+fmt(m['theirs'])+' ['+fmt(m['other15_ours'])+'/'+fmt(m['other15_theirs'])+']; '+nfmt(None if m['relative_absolute_gap'] is None else 100*m['relative_absolute_gap']))
        lines.append('| '+item['layout']+' | '+item['interval']+' | '+str(item['games'])+'/'+str(item['other15_games'])+' | '+'<br>'.join(entries)+' |')
    lines += ['', '## D. 동일 레이아웃 내부: 우리 승/패', '',
              '| layout | 경기 승/패 | dither% 승/패 | seen100% 승/패 | P50 승/패 |',
              '|---|---:|---|---|---|']
    for item in d:
        vals = ['/'.join(fmt(item[outcome][key], key != 'pearls50') for outcome in ('win', 'loss')) for key in ('dither', 'seen100', 'pearls50')]
        lines.append('| '+item['layout']+' | '+str(item['win']['games'])+'/'+str(item['loss']['games'])+' | '+' | '.join(vals)+' |')
    lines.append('')
    lines.append(f'동일 레이아웃 평균 제거 Pearson(dither0–100, P100): {nfmt(correlation["pearson"])}; N={correlation["n"]}; layouts={correlation["layouts"]}.')
    lines += ['', '## 정의·한계', '',
        f'- main {len(source)}판, 19레이아웃, 양쪽 {len(rows)}행; 결과·최종 생존수/총길이/최장/여왕 길이 {validation["games_verified"]}/{len(source)} 일치. 입력 시각 {frozen["time"]}; 파일별 해시·분모는 JSON.',
        '- P=섭취 진주 수, D=생존 용 수, Q=여왕(진영 최저 시작 id). 계수·길이는 판당 평균; 비율은 분자/분모 합계, seen·Qdead는 유효 판 평균. D표는 유효 판별 비율 평균; 무승부 제외.',
        '- 구간 양끝 포함, 상태는 라운드 종료. 조기 종료 뒤 상태·seen·여왕 길이는 NA(외삽 없음); 계수는 관측 사건만. Qdead는 관측 사망≤시점=1, 그 시점 관측 생존=0, 살아서 조기 종료=NA.',
        '- 시야=행동 시작 머리 중심 경계 순환 7×7, 벽 무시·포털 확장 없음. seen=그 편 시야 합집합/width×height. 경로=벽 제외·포털 포함 최단 걸음, 몸 무시; 모든 칸은 타일이며 벽은 변.',
        '- dither·keep은 시작 시야에 진주가 없고 첫 성공 걸음이 있는 차례. dither=자기 이전 방문 12칸 재방문(출생 머리 포함, 자식 이력 새로 시작); keep=같은 id 직전 차례의 첫 성공 방향 유지(직전 이동 없으면 제외).',
        '- distinct20=구간 시작부터 겹치지 않는 20라운드 창에서 id별 시작 머리+성공 이동 도착 칸 수; 완전한 창만, 일찍 태어나거나 죽은 id는 포함. no_pearl_distinct20=그중 진주 없는 시작 차례만; 부분 창·활동 라운드 수는 JSON.',
        '- births=자연+사망 낙하 생성 사건(동일 칸 재생성은 새 진주); near6=생성 사건 직전 그 편 머리까지≤6걸음. birth_ate=그 생성 집단 중 해당 편이 경기 종료까지 먹은 몫; wait=해당 편이 먹은 진주만의 생성→섭취 라운드 평균, 미섭취는 우측 절단. natural_*는 자연 생성만.',
        '- adj_pearl_miss=시작 때 열린 변 너머 이웃 진주가 하나 이상 있으나 그 진주를 차례 중 하나도 먹지 않은 비율(포털 이웃 포함). hot=시작 칸 또는 열린 이웃에 그 사건 전에 2회 이상 생성된 칸이 있는 차례/전체 차례; 낙하 포함.',
        '- portal_room=포털 변을 제거한 연결 성분 중 양쪽 시작 머리가 없고 포털로 도달 가능한 성분. portal_required=각 편 출발에서 포털 없이 못 가지만 포털로 갈 수 있는 칸(상대 출발 방 포함). *_ate%=그 구역 생성 진주 중 해당 편 섭취 몫; game은 전체 경기, 그 외는 해당 구간.',
        '- Hnet=교차 진영 head-on에서 우리/상대가 잃은 사건 직전 길이−맞교환 상대 길이(양수=해당 편 순손실), 낙하 회수 미차감; 같은 편 충돌 별도. death는 움직이는 쪽/맞은 쪽 분리, no action·timeout·unpaid sprint·illegal split 별도.',
        '- first_contact_round·queen_death_round=첫 접촉/여왕 사망이 해당 구간에 관측된 판만 평균; *_in_window%=전체 판 중 그 구간에 사건 관측. queen_death_원인=해당 구간 사망 판당 수. enemy_half=양쪽 시작 머리까지 경로거리 중 상대 쪽이 더 짧은 칸, 동거리 중립; r50/100 살아 있는 머리로 가중.',
        '- C 상대차=100×|우리−상대|/max(|우리|,|상대|), 둘 다 0이면 0, 결측이면 NA(맨 뒤); 기타15는 위 4레이아웃 제외. gap의 방향·분모·원값은 aggregate.json. D 상관은 같은 유효 쌍 집단에서 레이아웃별 평균을 뺀 Pearson; 게임 간 독립성 미가정, 인과 추정 없음.'
    ]
    assert len(lines) <= 90, len(lines)
    aggregate = dict(A=a, B=b, C=c, D=d, within_layout_correlation=correlation,
                     conventions=dict(pct_units='percentage points for named % measures',
                                      C_sort='abs(ours-theirs)/max(abs(ours),abs(theirs)); both zero=0; missing last'),
                     summary_lines=len(lines))
    (OUT / 'aggregate.json').write_text(json.dumps(aggregate, ensure_ascii=False, indent=2)+'\n')
    (OUT / 'summary.md').write_text('\n'.join(lines)+'\n')
    # Recheck the current rows and replay bytes before writing completion.
    current = {r['game']: r for r in map(json.loads, (OUT.parent/'rows.jsonl').read_text().splitlines()) if r['our_code'] == 'main'}
    assert set(current) == set(source)
    for check in validation['checks']:
        i = check['game']
        assert check['final_reconstructed'] == current[i]['final']
        assert source[i] == current[i]
        path = ROOT / check['replay']
        assert sha(path) == check['replay_sha256']
        assert sha(path.parent / ('game-%d.json' % i)) == check['metadata_sha256']
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(ROOT/name) == expected, name
    if '--prepare' in sys.argv:
        print(f'PREPARED {len(lines)} summary lines; {len(source)} games checked; no completion marker.', flush=True)
        return
    last = [datetime.now().astimezone().isoformat(timespec='seconds'),
            f'main {len(source)} games; 19 layouts; per-game.jsonl {len(rows)} game-side rows; summary.md {len(lines)} lines.',
            f'Reconstructed final standings match rows.jsonl in {validation["games_verified"]}/{len(source)} games used; winners also match.',
            'A/B/C/D complete; all input and replay SHA-256 unchanged; offline only; writes confined to dossier/.',
            'last.txt written LAST.']
    assert len(last) <= 5
    print('\n'.join(last), flush=True)
    (OUT / 'last.txt').write_text('\n'.join(last)+'\n')

if __name__ == '__main__':
    main()
