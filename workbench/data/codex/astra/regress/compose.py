#!/usr/bin/env python3
"""Compose the brief's report from frozen measurements; no new inputs."""
import sys
sys.dont_write_bytecode = True
import json
from collections import Counter
from count import HERE
from tables import cell, md_table, TITLES

rows=[json.loads(l) for l in (HERE/'games.jsonl').read_text().splitlines()]
rows=[r for r in rows if 'excluded' not in r]
steps=json.loads((HERE/'steps.json').read_text())
validation=json.loads((HERE/'validation.json').read_text())
manifest=json.loads((HERE/'manifest.json').read_text())
versions=Counter(r['version'] for r in rows)
persist=[r for r in steps['sustained'] if r['change'] is not None]
thin=sum(not r['repeated'] for r in persist)
zero=sum(r['change'] is None for r in steps['sustained'])

priorities=[
    ('Stripes','one12','one13','pearls100',
     '[C] QS_KEEP_MIN_UNITS 6→2 (Δ13)',
     '[E] 최초 여왕 분열 지연이 자손·수확 감소보다 먼저 나타나는지; 포털 통과는 가능한지'),
    ('Queen Of Spades','one11','one12','pearls100',
     '[C] Δ12 전체; one14는 PORTAL_SCOUT_MIN_LEN만 제거',
     '[E] 살아 있는 비퀸이 포털 입구에 도달하는지; QUEEN_PORTAL_LAST·POCKET_KEEP_OUT·TARGET_REACHABLE의 거부인지'),
    ('Australia','one11','one12','pearls100',
     '[C] Δ12 전체; TERRITORY_DECAY·여왕 안전 규칙도 잔존',
     '[E] 포털 재개 뒤 초반 분열·진주 접근이 늦는지; 먹기 대신 안전·가까운 영토를 선택하는지'),
]
ptable=[]
for m,a,b,k,sw,check in priorities:
    values=[cell([r for r in rows if r['map']==m and r['version']==v],k) for v in [a,b,'one14']]
    r=next(r for r in persist if r['map']==m and r['before_version']==a and r['after_version']==b and r['metric']==k)
    ptable.append([m,f'{a}→{b}', ' → '.join(values),f'{r["change"]*100:.1f}%',sw,check])

def game(gid): return next(r for r in rows if r['gid']==gid)
def first_qsplit(gid):
    return next(e['r'] for e in game(gid)['moments'] if e['kind']=='split' and e['queen'])
def first_portal(gid):
    return next(e['r'] for e in game(gid)['moments'] if e['kind']=='portal')

intro=[
    '[M] Stripes는 one12→one13에서 r100 진주가 감소했고 one14에서도 낮다. [E] 포털 규칙 외의 회귀 확인을 우선할 후보다.',
    '[E] 카드: 없음. 먼저 아래 기보를 확인한다; 평균 차이만으로 스위치를 되돌릴 근거는 부족하다.',
    f'[M/E] 확신: 집계는 높음({len(rows)}판 최종 상태 검산·{len(validation["independent_checks"])}판 기존 스캐너 대조 일치), 인과는 미확인(one14 {versions["one14"]}판).',
    '',
    f'[전체 보고서](<{HERE}/report.md>) · [원자료](<{HERE}/games.jsonl>) · [정의](<{HERE}/methods.md>)',
    '',
    f'[M] 최종 입력 고정: {manifest["frozen_at"]}. 지도 {len({r["map"] for r in rows})}개; one14는 Cache 상대만 포함.',
    f'[M] 35% 초과 지속 변화 {len(persist)}건 중 {thin}건은 경계/후속에 단판 표본이 있다. 이전 평균 0의 후보 {zero}건은 별도다.',
    '[E] 아래는 버그 확정 순위가 아니라 기보 확인 순서다. 같은 상대 비교도 시드·시간·상대 행동을 통제하지 못한다.',
    '',
]
intro += md_table(['우선 지도','경계','[M] 진주 r100: 이전→이후→one14 [경기]','[M] 경계 변화','바뀐/남은 스위치','기보에서 확인할 것'],ptable).splitlines()
intro += [
    '',
    '[M] Stripes: 같은 Cache 상대에서 최초 여왕 분열은 '
        f'M1501669 r{first_qsplit(1501669)}(one12), M1506217 r{first_qsplit(1506217)}(one13), '
        f'M1517689 r{first_qsplit(1517689)}(one14). 이 경기들의 포털 첫 통과는 모두 r{first_portal(1501669)}.',
    '[M] Queen Of Spades: M1496853(one11)은 '
        f'r{first_portal(1496853)} 첫 포털 통과. M1506221(one13)·M1517693(one14)은 r0–99 통과가 없고, '
        f'후자의 첫 여왕 분열은 r{first_qsplit(1517693)}; r50 진주는 {game(1517693)["values"]["pearls50"]}.',
    '[M] Australia: M1496846(one11)·M1517686(one14)은 모두 '
        f'r{first_portal(1496846)} 첫 포털 통과지만, r50 진주는 '
        f'{game(1496846)["values"]["pearls50"]}→{game(1517686)["values"]["pearls50"]}, r0–99 통과는 '
        f'{game(1496846)["values"]["portals100"]}→{game(1517686)["values"]["portals100"]}. '
        f'M1501666(one12)의 통과는 {game(1501666)["values"]["portals100"]}.',
    '',
    '[E] 따라서 포털 통과 회복만으로 수입 회복을 보장하지 않는다. Queen Of Spades의 미통과 원인과 Australia의 잔여 수입 격차는 아직 분리하지 못했다.',
    '[C] 스위치 귀속은 아래 Δ 표의 업로드 노트·CARDS·소스 줄에 연결했다. 한 경계에 여러 스위치가 바뀌면 개별 원인은 확정하지 않았다.',
    '',
    '[M] 시간 기준: 진주 rT는 r0..T−1, 길이·용 수는 rT 시작. 일찍 종료한 경기는 최종 상태를 유지한다.',
    '[M] 사망 중앙값은 죽은 경기만 [사망/전체]; 생존 종료는 검열이다. 먼 턴은 여왕 시작 칸에서 벽·포털을 반영한 최단 지형 거리이며 경기별 비율의 평균이다.',
    '[M] 아래 표는 우리 편만 집계했다. 머리 충돌은 피해자(rammed)·공격자·아군 충돌을 구분했고, 기타 원인도 보존했다.',
    '',
    '[M] 지속은 후속 버전 모두가 경계 이전 평균 대비 같은 방향으로 35% 초과인 경우다. 한 판뿐인 버전과 검열 때문에 반복 확인이 약한 후보는 모두 별도 표에 남겼다.',
    '[M] 반복 표의 Trophy 사망 중앙값은 더 늦어진 변화이며, 생존한 one14에는 사망 라운드가 없다. 이를 회귀로 판정하지 않았다.',
    '[M] 상대 봇 ID는 모든 상대 기보에서 비어 있어 상대 버전 불변 여부를 검증할 수 없었다. 전체 표는 요청대로 모든 상대를 포함하고 각 단계에 같은 상대 재집계를 병기했다.',
    '[M] 실행은 nice -n 10·단일 프로세스로 요청했으나 환경이 우선순위 변경을 거부했다. 네트워크·대전·업로드·소스 편집은 하지 않았다.',
    '[E] 미확인: one14의 나머지 상대, 사건별 스위치 발동, 자연/사체 진주 분리, 상대 변경 및 인과. 실행 파일과 측정 결과는 이 폴더에만 썼다.',
    '',
]
report='\n'.join(intro)+'\n'+(HERE/'tables.md').read_text()
(HERE/'report.md').write_text(report)
(HERE/'priority.json').write_text(json.dumps(ptable,ensure_ascii=False,indent=2))
non_tables=[l for l in report.splitlines() if not l.startswith('|') and not l.startswith('#')]
print(json.dumps(dict(report_lines=len(report.splitlines()), narrative_words=len(' '.join(non_tables).split())),ensure_ascii=False))
print('\n'.join(report.splitlines()[:25]))
