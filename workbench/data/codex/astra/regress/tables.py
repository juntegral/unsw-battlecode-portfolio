#!/usr/bin/env python3
"""Deterministic tables and exhaustive persistence screens from games.jsonl."""
import sys
sys.dont_write_bytecode = True
import csv
import json
import re
from collections import Counter, defaultdict
from statistics import mean, median
from count import HERE, ROOT, SM, VERSIONS, METRICS

TITLES = {
    'pearls50': '진주 r50', 'pearls100': '진주 r100', 'pearls200': '진주 r200',
    'alive100': '생존 용 r100', 'alive200': '생존 용 r200',
    'total100': '총 길이 r100', 'total200': '총 길이 r200',
    'queen100': '여왕 길이 r100', 'queen200': '여왕 길이 r200',
    'queen_death_share': '여왕 사망 경기 비율', 'queen_death_median': '여왕 사망 라운드 중앙값',
    'portals100': '포털 통과 r0–99', 'splits100': '분열 r0–99',
    'deaths_wall': '벽 사망 r0–199', 'deaths_own_body': '자기 몸 사망 r0–199',
    'deaths_mate': '아군 몸 사망 r0–199', 'deaths_enemy_body': '적 몸 사망 r0–199',
    'deaths_rammed_head_on': '적에게 들이받힌 머리 충돌 사망 r0–199',
    'deaths_initiated_head_on': '우리 공격 머리 충돌 사망 r0–199 (보충)',
    'deaths_mate_head_on': '아군 머리 충돌 사망 r0–199 (보충)',
    'deaths_other': '기타 사망 r0–199 (보충)',
    'far_share': '시작 칸에서 12걸음 초과인 턴 비율 r0–199',
}

def stat(rows, metric):
    vals = [r['values'][metric] for r in rows if r['values'][metric] is not None]
    return ((median(vals) if metric == 'queen_death_median' else mean(vals)) if vals else None,
            len(vals), len(rows))

def fmt(value, metric):
    if value is None: return '—'
    return f'{value*100:.1f}%' if metric in ('far_share', 'queen_death_share') else f'{value:.1f}'

def cell(rows, metric):
    value, n, total = stat(rows, metric)
    count = f'{n}/{total}' if metric == 'queen_death_median' else str(total)
    return f'{fmt(value, metric)} [{count}]'

def md_table(header, rows):
    return '\n'.join(['| '+' | '.join(header)+' |', '| '+' | '.join(['---']*len(header))+' |'] +
                     ['| '+' | '.join(map(str, row))+' |' for row in rows])

def crossed(old, new):
    if old is None or new is None or old == new: return 0
    if old == 0: return 1 if new > 0 else 0
    ratio = (new-old)/old
    return 1 if ratio > .35 else -1 if ratio < -.35 else 0

def switches():
    sources = {}
    for ver in VERSIONS:
        p = SM/f'{ver}-bot/main.cpp'
        vals = {}
        for ln, line in enumerate(p.read_text().splitlines(), 1):
            m = re.match(r'^constexpr\s+(?:bool|int|double)\s+(\w+)\s*=\s*([^;]+);', line)
            if m: vals[m[1]] = (m[2].strip(), ln)
        sources[ver] = vals
    changes = {}
    for a, b in zip(VERSIONS, VERSIONS[1:]):
        out = []
        for name, (new, ln) in sources[b].items():
            old = sources[a].get(name, ('없음', None))[0]
            if old == new: continue
            if old == '없음' and new in ('0', '0.0', 'false'): continue
            out.append(dict(name=name, old=old, new=new, line=ln))
        changes[b] = out
    (HERE/'switches.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2))
    table = []
    for a, b in zip(VERSIONS, VERSIONS[1:]):
        bits = '; '.join(f'{x["name"]} {x["old"]}→{x["new"]} (L{x["line"]})' for x in changes[b])
        table.append([f'Δ{b[3:]}: {a}→{b}', '[C] '+bits,
                      f'[업로드 노트](../../../guide/px-live-{b}.txt); '
                      '[CARDS](../CARDS.md:13); '
                      f'[소스](../../../online/smoke/{b}-bot/main.cpp)'])
    return table

def main():
    rows = [json.loads(l) for l in (HERE/'games.jsonl').read_text().splitlines()]
    good = [r for r in rows if 'excluded' not in r]
    groups = defaultdict(list)
    for r in good: groups[r['map'], r['version']].append(r)
    maps = sorted({r['map'] for r in good})
    with (HERE/'means.tsv').open('w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['map', 'version', 'metric', 'value', 'observations', 'games'])
        for m in maps:
            for v in VERSIONS:
                for k in METRICS: writer.writerow([m, v, k, *stat(groups[m,v], k)])
    sustained, returned, latest = [], [], []
    for m in maps:
        for k in METRICS:
            for a, b in zip(VERSIONS, VERSIONS[1:]):
                old, an, at = stat(groups[m,a], k)
                new, bn, bt = stat(groups[m,b], k)
                direction = crossed(old, new)
                if not direction: continue
                successors = []
                for v in VERSIONS[VERSIONS.index(b)+1:]:
                    val, n, total = stat(groups[m,v], k)
                    if val is not None: successors.append([v,val,n,total])
                shared = sorted({r['opponent_id'] for r in groups[m,a]} &
                                {r['opponent_id'] for r in groups[m,b]})
                matched = []
                for opp in shared:
                    aa = [r for r in groups[m,a] if r['opponent_id'] == opp]
                    bb = [r for r in groups[m,b] if r['opponent_id'] == opp]
                    av, aon, _ = stat(aa,k); bv, bon, _ = stat(bb,k)
                    matched.append(dict(opponent_id=opp, opponent=aa[0]['opponent'],
                                        before=av, after=bv, n_before=len(aa), n_after=len(bb),
                                        observations_before=aon, observations_after=bon,
                                        same_direction=crossed(av,bv)==direction))
                rec = dict(map=m, metric=k, before_version=a, after_version=b,
                           before=old, after=new, direction=direction,
                           change=(new-old)/old if old else None, n_before=an, n_after=bn,
                           total_before=at,total_after=bt, successors=successors, matched=matched)
                if not successors:
                    latest.append(rec)
                elif all(crossed(old,val)==direction for v,val,n,total in successors):
                    rec['repeated'] = min([an,bn]+[x[2] for x in successors]) >= 2
                    sustained.append(rec)
                else:
                    rec['return_version'] = next(v for v,val,n,total in successors if crossed(old,val)!=direction)
                    returned.append(rec)
    (HERE/'steps.json').write_text(json.dumps(dict(sustained=sustained,returned=returned,latest=latest),
                                            ensure_ascii=False,indent=2))
    with (HERE/'steps.tsv').open('w') as f:
        writer = csv.writer(f,delimiter='\t')
        writer.writerow(['status','map','metric','before_version','after_version','before','after',
                         'change','n_before','n_after','successors','switch_delta'])
        for status, seq in [('sustained',sustained),('returned',returned),('latest',latest)]:
            for r in seq:
                writer.writerow([status]+[r[x] for x in ('map','metric','before_version','after_version',
                                'before','after','change','n_before','n_after')]+[
                                json.dumps(r['successors']), 'Δ'+r['after_version'][3:]])
    parts = []
    parts.append('## [M] 표본 구성\n\n'+md_table(['버전','경기','지도','상대별 경기','진영 A/B'],[
        [v, len(rr := [r for r in good if r['version']==v]),len({r['map'] for r in rr}),
         '; '.join(f'{opp}: {n}' for opp,n in sorted(Counter(r['opponent'] for r in rr).items())),
         f'{sum(r["side"]=="A" for r in rr)}/{sum(r["side"]=="B" for r in rr)}'] for v in VERSIONS]))
    for k in METRICS:
        parts.append(f'## [M] {TITLES[k]} (`{k}`)\n\n'+md_table(['지도']+VERSIONS,[
            [m]+[cell(groups[m,v],k) for v in VERSIONS] for m in maps]))
    parts.append('## [C] 단계 경계에서 바뀐 상수\n\n'+md_table(['경계','변경 (뒤 버전의 소스 줄)','근거'],switches()))

    def step_table(seq):
        rs = []
        for r in seq:
            k=r['metric']
            change=f'{r["change"]*100:+.1f}%' if r['change'] is not None else '0→양수'
            series='; '.join(f'{v} {fmt(val,k)} [{n if k=="queen_death_median" else total}]' for v,val,n,total in r['successors'])
            def match_count(x, which):
                return (f'{x["observations_"+which]}/{x["n_"+which]}' if k=='queen_death_median'
                        else str(x['n_'+which]))
            matches='; '.join(f'{x["opponent"]} {fmt(x["before"],k)} [{match_count(x,"before")}]→'
                             f'{fmt(x["after"],k)} [{match_count(x,"after")}]' for x in r['matched']) or '공통 상대 없음'
            rs.append([r['map'],k,f'{r["before_version"]}→{r["after_version"]}',
                       f'{fmt(r["before"],k)} [{r["n_before"]}]→{fmt(r["after"],k)} [{r["n_after"]}]',
                       change,series,matches,'Δ'+r['after_version'][3:]])
        return md_table(['지도','지표','경계','평균/중앙값 [관측 수]','변화','후속 버전','같은 상대 재집계','스위치'],rs)
    for title, seq in [('반복 관측된 지속 단계', [r for r in sustained if r['repeated'] and r['change'] is not None]),
                       ('얇은 표본의 지속 후보 (단판을 배제하지 못함)', [r for r in sustained if not r['repeated'] and r['change'] is not None]),
                       ('이전 평균 0의 지속 후보 (퍼센트 변화 정의 불가)', [r for r in sustained if r['change'] is None]),
                       ('후속에서 돌아온 35% 초과 변화 (지속 조건 탈락)', returned),
                       ('후속 버전이 없어 지속 확인 불가', latest)]:
        parts.append('## [M] '+title+f' — {len(seq)}건\n\n'+step_table(seq))
    (HERE/'tables.md').write_text('\n\n'.join(parts)+'\n')
    print(json.dumps(dict(games=len(good), maps=len(maps), versions=dict(Counter(r['version'] for r in good)),
                         repeated=sum(r['repeated'] for r in sustained),thin=sum(not r['repeated'] for r in sustained),
                         returned=len(returned),latest=len(latest)),ensure_ascii=False))

if __name__=='__main__': main()
